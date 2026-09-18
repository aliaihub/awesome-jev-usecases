# Browser and computer use

**Decision shape:** `Choice` over a bounded action set, `Noul` for state predicates, one call per step.

**Reach for it when:** a screen must become an action, and sending a screenshot to a frontier model for every step is too slow or too expensive.

This category has the most dramatic published cost and latency numbers in the entire ecosystem, and it also contains the single best piece of architectural advice in the repo.

---

## The insight

Frontier-model computer use is capable and expensive: every step ships a screenshot and waits several seconds for a plan. **Most steps do not need a plan. They need one choice from a short list, made quickly and cheaply, with a confidence you can gate on.**

So the architecture splits:

```
screen -> deterministic read (DOM / accessibility tree / OCR) -> element table
        -> Jev: which operation, on which element? (one call)
        -> code executes the action
        -> a small LLM runs ONLY when free text must be typed
```

The writing model handles text. Jev handles the decision. Code handles the browser.

---

## The measured results

### Browser agent: Zürich → London in 7.1 seconds for $0.0039

[**browser-use/jev-ultrafast**](https://github.com/browser-use/jev-ultrafast) (2,303★, Python) is the flagship project of this category. It builds a browser agent with a dynamic, indexed action space.

Every observation produces a new element table:

```text
[1] button Change ticket type · Round trip
[2] combobox Where from? · San Francisco
[3] combobox Where to? · empty
[4] textbox Departure · empty
...
```

The operations are `CLICK`, `TYPE_TEXT`, `SELECT`, `SCROLL_UP`, `SCROLL_DOWN`, `WAIT`, `DONE`, and `BLOCKED`. Only supported operations and targets are offered.

The design trick is speculative fan-out applied to actions:

```text
                      one TypeSafe request
                     +---------------------------+
page -> element table -> operation                 |
                     | click_target              |
                     | type_text_target          |
                     | select_target, if present |
                     +-------------+-------------+
                         use the matching target
                                   |
                    CLICK [7] -----+---> browser
                TYPE_TEXT [3] -----+
                          |
                   small LLM -> text -> browser
```

Click, type, and select targets are all asked in the same round trip. Only the one matching the chosen operation executes. **Two decisions, one network call.**

**Measured: Zürich to London on real Google Flights in 7.1 seconds, $0.0039**, page loads included.

There are no site-specific action scripts or prepared field strings in the policy. The policy is genuinely general.

### Computer use: $0.0002 per step

[**awlevin/typesafe-computer-use**](https://github.com/awlevin/typesafe-computer-use) (169★, Python, macOS) drives a Mac toward a plain-English goal without sending screenshots to a large model. OCR reads the screen, Jev picks the next action, and a writing model is called only for free text.

Measured on the same screenshot and goal, one decision each:

| | Jev | Claude Opus 5 (bare screenshot) |
| --- | ---: | ---: |
| Input tokens | 4,882 | 4,785 |
| Cost per decision | **$0.0002** | $0.032 |
| Cost per 12-step task | **$0.003** | $0.40–$0.90 |
| Model latency | **0.13–0.38 s** | 5.2 s |
| End-to-end step | **~1.5 s** | ~5.5 s |

Same input size, ~160x cheaper per decision, and the same order of magnitude fewer tokens. The saving comes entirely from how the input is represented - an OCR text representation instead of pixels - and from what is asked (a bounded choice instead of an open plan).

### The caveat that matters most

The author's own note is the most useful line in the entire ecosystem:

> Every piece of reasoning the frontier model does for free has to be rebuilt here as deterministic state.

Specifically: the frontier model read event dates off the pixels and compared them unaided, while the Jev pipeline needed explicit date parsing built around it.

This is the real cost of the approach. Budget for it explicitly before you choose it.

Source: [Valyu AI practical guide](https://dev.to/valyuai/how-to-use-jev-a-practical-guide-to-typesafes-system-one-model-g5e)

---

## The pattern

```python
def step(goal, page):
    # 1. deterministic read of the screen -> element table
    elements = read_elements(page) # DOM, a11y tree, or OCR
    table = format_table(elements) # "[1] button Submit"

    # 2. code computes the legal action space
    operations = ["CLICK", "TYPE_TEXT", "SELECT", "SCROLL_UP",
                  "SCROLL_DOWN", "WAIT", "DONE", "BLOCKED"]

    # 3. one call: operation + every possible target, in parallel
    r = jev.system_one(
        state={
            "goal": goal,
            "page": {"url": page.url, "elements": table},
            "history": recent_actions,
            "operations": operations,
        },
        questions={
            "operation": Choice(
                instructions="Which operation advances `goal` on this page?",
                criteria={
                    "CLICK": "Activate a button, link, or control",
                    "TYPE_TEXT": "Enter free text into a field",
                    "SELECT": "Choose an option from a dropdown",
                    "SCROLL_UP": "The target is above the visible area",
                    "SCROLL_DOWN": "The target is below the visible area",
                    "WAIT": "The page is still loading; no action is correct yet",
                    "DONE": "`goal` has been achieved",
                    "BLOCKED": "`goal` cannot be achieved from this state",
                },
            ),
            "click_target": Choice(
                instructions="If the operation is CLICK, which element?",
                criteria={str(e.id): e.label for e in elements if e.clickable},
            ),
            "type_text_target": Choice(
                instructions="If the operation is TYPE_TEXT, which field?",
                criteria={str(e.id): e.label for e in elements if e.typeable},
            ),
            "select_target": Choice(
                instructions="If the operation is SELECT, which dropdown?",
                criteria={str(e.id): e.label for e in elements if e.selectable},
            ),
        },
    )
    a = r.answers

    # 4. code executes - only the matching target matters
    if a["operation"].confidence < 0.6:
        return ask_human_or_replan(goal, page)

    op = a["operation"].choice
    if op == "CLICK":
        page.click(element(a["click_target"].choice))
    elif op == "TYPE_TEXT":
        page.type(element(a["type_text_target"].choice), write_text(goal)) # LLM here
    elif op == "SELECT":
        page.select(element(a["select_target"].choice))
    elif op == "SCROLL_DOWN":
        page.scroll_down()
    elif op == "DONE":
        return done()
    elif op == "BLOCKED":
        return blocked(page)
```

Three things to internalize:

1. **Only legal operations and elements are offered.** The model cannot choose an impossible action because the option set does not contain one.
2. **Targets are speculative.** Three target questions are asked; only the one matching the chosen operation is read. That is free except for tokens.
3. **The writing model only runs on `TYPE_TEXT`.** The expensive per-step model call is eliminated for every other operation.

---

## What the community built

### Browser automation

- [**jkudish/jev-browser**](https://github.com/jkudish/jev-browser) - browser use built on Jev.
- [**Ying-Kai-Liao/jev-browser**](https://github.com/Ying-Kai-Liao/jev-browser) - an LLM plans, Jev decides. Library, CLI, and MCP server.
- [**tontoko/jev-browser**](https://github.com/tontoko/jev-browser) - a grounded Jev/Playwright core with a typed SDK, persistent CLI, and MCP server.
- [**romaluev/jev-ego**](https://github.com/romaluev/jev-ego) - one TypeSafe request per step for the ego lite browser agent.
- [**KesavanKing/jev-browser**](https://github.com/KesavanKing/jev-browser) - local browser automation UI where Jev chooses bounded page actions and a text model supplies field values.
- [**CorieW/JevTest**](https://github.com/CorieW/JevTest) and [**juancristobalgd1/jevRemote**](https://github.com/juancristobalgd1/jevRemote) - reproducible text-first browser automation with deterministic assertions.
- [**ranjan2829/AskJev**](https://github.com/ranjan2829/AskJev) - Jev autopilot for any website, with a guard on irreversible clicks.

**The recurring architecture across all of them:** an LLM plans, Jev decides, code executes. [Ying-Kai-Liao/jev-browser](https://github.com/Ying-Kai-Liao/jev-browser) states it in the tagline.

### Browser extensions

- [**kitze/unclutter**](https://github.com/kitze/unclutter) (49★) - a WXT browser extension for Jev-powered page clutter removal with reusable template rules.
- [**realZachi/typesafe-adblock**](https://github.com/realZachi/typesafe-adblock) - a Chrome extension that asks Jev "is this DOM element an ad?" and pops it off the page.
- [**piyush97/focus-tube**](https://github.com/piyush97/focus-tube) - a distraction-free YouTube learning feed.

These are worth noting for the *shape*: a per-element binary judgment, run over many elements, cheap enough to fire on every DOM mutation. That is the same pattern as the [context sieve](03-agent-harness-engineering.md#2-context-sieve--keep-or-evict) applied to a web page.

### PS2 and other platforms

[opaielsheikh/ps2-ai-agent](https://github.com/opaielsheikh/ps2-ai-agent) is an autonomous PlayStation 2 agent with a real-time visual telemetry HUD.

---

## Design notes specific to browser and computer use

### Text representation beats pixels, every time

Both flagship projects read the page deterministically - DOM, accessibility tree, or OCR - and send text. Jev takes text only, and the token cost of a structured text table is far lower than an image. This is not just a Jev constraint; it is the reason the cost numbers are so good.

### Offer only legal actions

If the model cannot choose an impossible action, you have removed an entire failure class without relying on the model to know the rules. This is the same principle as [sorrycc/typesafe-snake](https://github.com/sorrycc/typesafe-snake) generating legal moves in code.

### Speculate on targets

Ask for click, type, and select targets in the same call and read only the one that matches. Two or more decisions, one round trip. This is [Pattern 1](../docs/patterns.md#pattern-1--speculative-fan-out) applied to actions.

### Add an explicit `WAIT` and an explicit `BLOCKED`

`WAIT` prevents the model from taking a destructive action on a half-loaded page. `BLOCKED` gives it an honest exit instead of forcing it to act. Without `BLOCKED`, a stuck agent will keep clicking.

### Gate irreversible actions higher

[ranjan2829/AskJev](https://github.com/ranjan2829/AskJev) guards specifically on irreversible clicks. A `Noul` for "would this action be irreversible or costly to undo?" deserves a much higher threshold than navigation.

### Rebuild the reasoning the frontier model got for free

This is the cost of the approach. Inventory the implicit computations the LLM was doing - reading values, comparing them, noticing implausibility - and confirm you can compute each in code. If you cannot, that step needs a different tool.

### Keep the step count visible

Track steps per task and cost per task, not just per decision. $0.0002 per step is only meaningful against how many steps a task takes.

---

## Pitfalls

| Pitfall | Symptom | Fix |
| --- | --- | --- |
| Sending screenshots | Expensive and slower | Read DOM / OCR into a text table |
| Open-ended action space | Invalid or destructive actions | Enumerate legal operations in code |
| No `WAIT` action | Acts on a half-loaded page | Include it explicitly |
| No `BLOCKED` action | Stuck agent keeps clicking | Include an honest exit |
| Same threshold for navigation and clicks | Accidental commits or submissions | Higher confidence bar for irreversible |
| Ignoring rebuilt reasoning | Silent failures on values | Inventory and reimplement in code |
| Not tracking steps | Cost surprises | Measure cost per task, not per step |

---

## Related

- [08-real-time-and-games.md](08-real-time-and-games.md) - the same tight loop in a simulation
- [02-llm-guardrails-and-verification.md](02-llm-guardrails-and-verification.md) - guarding the actions before they run
- [../docs/patterns.md](../docs/patterns.md#pattern-1--speculative-fan-out) - the target-speculation pattern
