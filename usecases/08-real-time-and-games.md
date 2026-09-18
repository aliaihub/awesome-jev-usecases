# Real-time loops and games

**Decision shape:** `Choice` per tick, `Score` for risk, `Noul` for state predicates - evaluated in a tight loop.

**Reach for it when:** the decision must complete faster than human perception, inside a request handler, a control loop, or a game frame.

This is the category that demonstrates *why* latency is a new capability rather than just a speedup. As Nelson Elhage put it, fast software does not just let you do the same tasks faster - it lets you do entirely new kinds of tasks.

---

## The claim, and the demo behind it

TypeSafe's argument is that 70–500 ms enables AI decisions inside real-time loops where a 3–30 second LLM call is a non-starter. The demo that made this concrete is **Jev playing Doom**: structured game state in as text, choice of action out, roughly 10 calls per second, at about $7/hour of inference.

The caveats, which TypeSafe states themselves:
- The demo runs on structured state as a data structure with text, **not on images**.
- A non-AI Doom bot could play better. The point was a bot that reacts to different *representations* of game state and follows instructions.

That honesty matters. The interesting thing is not that Jev can play Doom. It is that **a general model can be dropped into a real-time loop at all** - you can change its instructions in English and it changes its behavior, which a hand-written bot cannot do.

Their second demo, **Wikiracing** (start on one Wikipedia page, reach a target page using only links), is a better illustration of intelligence-per-second: each step means choosing between hundreds to thousands of links. Jev supports a cardinality up to 255; for higher cardinality they use a two-stage system of scoring independently then making an explicit choice.

Source: [launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

---

## The architecture that works: Jev advises, code controls

The best real-world example is [RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone), an autonomous quadrotor flying a five-station obstacle course in MuJoCo using only its onboard camera. It is worth studying specifically for how carefully it scopes Jev's role:

| Rate | Layer | Owner |
| --- | --- | --- |
| 500 Hz | Geometric flight controller | Code |
| 50 Hz | Guidance and safety reflex | Code, **always owns safety** |
| 15 Hz | Camera → symbolic scene | Classical CV |
| ~2.5 Hz | Tactical judgment | **Jev, advisory only** |

The README states the constraint plainly:

> Jev is **not** a vision model. It takes JSON and returns typed answers with probabilities. So it cannot be the perception layer, and it cannot run at control rate. What it can do is answer small questions about a situation that ordinary code finds hard to phrase.

Classical CV compresses depth and segmentation into a compact scene: five forward range sectors, the height of whatever is blocking the path, whether its top edge is visible, and where the target is. Jev reads that and answers three questions in one call:

| Question | Type | Options |
| --- | --- | --- |
| `maneuver` | **Choice** | hold_course / gap_left / gap_right / climb / brake / reacquire |
| `risk` | **Score** | clear and open → tight → about to hit something |
| `target_truly_lost` | **Noul** | genuinely lost, or just briefly occluded? |

**Three design decisions worth copying:**

1. **Code decides *when* to ask.** On an open corridor with the target in view there is nothing to decide, so no call is made.
2. **Scenes are fingerprinted** so an unchanged situation reuses the last judgment. A typical 65-second flight costs about 110 calls.
3. **Code keeps the veto.** A hard reflex layer runs at 50 Hz and overrides any judgment when something is close. Jev can propose `climb`, but code refuses it unless the obstruction's measured top edge is actually within the aircraft's climb capability.

That third point is the whole architecture in one sentence: **Jev proposes, code disposes.**

---

## The pattern

```
every tick:
  1. code computes the symbolic state (no model)
  2. code decides whether a decision is even needed <-- skip most ticks
  3. if needed: one Jev call, several questions in parallel
  4. code validates the answer against hard constraints
  5. code executes or vetoes
```

```python
def tick(game_state):
    # 1. symbolic state - deterministic, cheap, no model
    scene = extract_symbolic_state(game_state)

    # 2. is there actually a decision here?
    if scene["target_visible"] and scene["path_clear"]:
        return hold_course()

    # 3. one call, all questions in parallel
    r = jev.system_one(
        state=scene,
        questions={
            "maneuver": Choice(
                instructions="Which maneuver should the craft take?",
                criteria={
                    "hold_course": "Current heading is safe and efficient",
                    "gap_left": "A clear opening exists to the left",
                    "gap_right": "A clear opening exists to the right",
                    "climb": "Climbing over the obstruction is viable",
                    "brake": "Stopping is the safest action",
                    "reacquire": "Target information is insufficient to proceed",
                },
            ),
            "risk": Score(
                instructions="How close is the craft to a collision?",
                criteria=["Clear and open", "Tight", "About to hit something"],
            ),
            "target_truly_lost": Noul(
                "Is the target genuinely lost rather than briefly occluded?"
            ),
        },
    )
    a = r.answers

    # 4. code validates against hard constraints - Jev cannot override physics
    if a["maneuver"].choice == "climb" and not scene["top_edge_within_climb_envelope"]:
        return brake()

    if a["risk"].score > 1.8 or a["risk"].confidence < 0.5:
        return safety_reflex() # deterministic layer owns safety

    # 5. execute the advisory judgment
    return execute(a["maneuver"].choice)
```

The `top_edge_within_climb_envelope` check is exactly the kind of computation that must stay in code. Jev judges whether climbing is *intended*; code judges whether it is *physically possible*.

---

## What the community built

### Game-playing agents

- [**fhshaik/typesafe-mario**](https://github.com/fhshaik/typesafe-mario) (217★) plays Super Mario Bros. from structured emulator state, not screenshots. The harness translates telemetry and RAM into object-centric JSON - Mario's motion, jump trajectory, upcoming enemies, terrain, measured response delay, recent-control results, episode progress - and Jev chooses one of seven legal controller actions (`noop`, `right`, `right_jump`, `right_run`, `right_run_jump`, `jump`, `left`).
- [**phyous/tsai-sc**](https://github.com/phyous/tsai-sc) has Jev complete the first StarCraft shareware mission across 421 decisions, through keyboard and mouse, with recorded action probabilities and a verification report.
- [**sorrycc/typesafe-snake**](https://github.com/sorrycc/typesafe-snake) - one System One choice per tick, with legal moves and facts generated in code.
- [**KyleKreuter/jev2048**](https://github.com/KyleKreuter/jev2048) lets Jev solve 2048.
- [**AbdelStark/heist-one**](https://github.com/AbdelStark/heist-one) is an observable browser stealth game where Jev makes typed guard judgments while deterministic code owns the world.

**Notice the shared property:** in every one, the *legal action set and the facts* are generated deterministically, and Jev only picks from the legal set. [sorrycc/typesafe-snake](https://github.com/sorrycc/typesafe-snake)'s description says it directly.

### Trading and financial loops

- [**jarrodwatts/jev-trader**](https://github.com/jarrodwatts/jev-trader) (527★) makes one decision per Monad block, roughly every 300 ms. Jev reads the Kuru MON-USDC order book and answers buy or sell; the bot posts a post-only limit order one tick inside the touch, so it earns the spread instead of paying it. Reported model latency in the event stream is around **81 ms**, and the hot loop makes exactly two RPC round trips to fit the block budget. It ships with a dry-run mode using real book data and simulated fills.
- [justinhe16/trade-jev](https://github.com/justinhe16/trade-jev) backtests Jev as a BUY/SELL/HOLD trader on NQ L10 order-book data.
- [zadescoxp/Jev-Trades](https://github.com/zadescoxp/Jev-Trades) is another trading bot built on Jev.
- [sosopop/jev_stock](https://github.com/sosopop/jev_stock) forecasts short-term stock price direction from structured market data.

**The trader's design detail is worth noting:** one decision per block, not per tick, and the loop is budgeted to the block time. Real-time does not mean unstructured - it means the loop boundary is explicit.

### Simulations

- [**vinilana/live-jev**](https://github.com/vinilana/live-jev) - a 2D autonomous car simulation in the browser.
- [**arielweinberger/jev-autopilot**](https://github.com/arielweinberger/jev-autopilot) - autonomously flies a drone from point A to point B in a random city, avoiding obstacles.
- [**emrickgarrett/OneVOneJev**](https://github.com/emrickgarrett/OneVOneJev) - a 1v1 quickscope arena in Three.js.
- [**Icohen007/jev-play-ping-pong**](https://github.com/Icohen007/jev-play-ping-pong) - browser table tennis with structured telemetry and auditable evidence.
- [**ashaazami/river-run-typesafe**](https://github.com/ashaazami/river-run-typesafe) - a River Raid–inspired shooter played by a TypeSafe pilot.
- [**rchovatiya88/cyber-breach-jev**](https://github.com/rchovatiya88/cyber-breach-jev) and [**onionminionops-beep/pdoom-protocol**](https://github.com/onionminionops-beep/pdoom-protocol) - arena shooters.

### Home automation

[**AboveColin/HA-Jev**](https://github.com/AboveColin/HA-Jev) is a Home Assistant integration: ask a question about your house and get a probability, a choice, or a score as an entity. [JanOstrowka/typesafe-assist](https://github.com/JanOstrowka/typesafe-assist) is a Home Assistant Assist conversation agent powered by Jev.

The [Syntax YouTube channel](https://www.youtube.com/watch?v=QbYBRjOaGOo) demonstrated exactly this:

> This took 300 milliseconds to ask Jev to answer the question and then call the particular home assistant API endpoint to actually turn the thing off.

That 300 ms end-to-end - model plus API call - is the number that makes voice interfaces viable.

---

## Design notes specific to real-time loops

### Compute the symbolic state outside the model

Jev takes JSON. Your job is to turn the world into JSON. In every successful real-time project, deterministic code and classical CV do the perception; Jev does the judgment. This is not a workaround - it is the architecture.

### Ask only when there is something to decide

The most important optimization is not making the call cheaper. It is not making it at all. [RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone) skips the call entirely on an open corridor with the target in view.

### Fingerprint states and cache verdicts

An unchanged situation has the same answer. Cache by state fingerprint and a 65-second flight costs ~110 calls instead of thousands.

### Put safety in a faster deterministic layer

Jev runs at 2.5 Hz. The safety reflex runs at 50 Hz. Jev can never be the safety layer, both because it is slower and because it is probabilistic. Hard constraints - physical limits, position bounds, rate limits - must be validated in code before execution.

### Bound the action set in code

Only offer legal actions. [sorrycc/typesafe-snake](https://github.com/sorrycc/typesafe-snake) generates legal moves and facts in code and lets Jev pick. This removes an entire class of failure (the model choosing an impossible action) without relying on the model to know the rules.

### Budget the loop to the deadline

[jev-trader](https://github.com/jarrodwatts/jev-trader) makes exactly two RPC round trips per block. Know your deadline and design the loop to fit inside it with margin.

---

## When real-time is the wrong goal

Be honest about whether you need this. If the decision happens once per user request and the user is already waiting on a network round trip, 400 ms of Jev is fine and 200 ms is not meaningfully better. The real-time category matters when:

- The decision is in a **control loop** (robotics, trading, games)
- The decision is in a **UI interaction path** (voice, autocomplete, live suggestions)
- The decision happens **per frame or per tick**, many times per second
- The decision must happen **inside a request handler** with its own latency budget

Otherwise, the cost advantage is the reason to use Jev, not the latency.

---

## Pitfalls

| Pitfall | Symptom | Fix |
| --- | --- | --- |
| Letting Jev own safety | Probabilistic layer makes hard decisions | Deterministic reflex layer, code vetoes |
| Calling every tick | Unnecessary cost and load | Skip when there is nothing to decide |
| No state fingerprinting | Redundant calls on identical states | Cache verdicts |
| Feeding raw images or pixels | Jev takes text only | Pre-process to symbolic state |
| Unbounded action set | Model proposes impossible actions | Generate legal actions in code |
| Ignoring the loop deadline | Missed blocks, dropped frames | Budget round trips to the deadline |

---

## Related

- [09-browser-and-computer-use.md](09-browser-and-computer-use.md) - the same loop applied to a screen
- [03-agent-harness-engineering.md](03-agent-harness-engineering.md) - the same loop applied to an agent
- [11-frontier-and-fun.md](11-frontier-and-fun.md) - the demos this category grew out of
