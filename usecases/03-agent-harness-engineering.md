# Agent harness engineering

**Decision shape:** `Choice` + `Noul` fired on every tool call, every context decision, and every turn boundary.

**Reach for it when:** you run a coding agent or an autonomous agent and you want a fast semantic supervisor that costs less than the tokens it saves.

This is where the community concentrated its effort in the first 72 hours. The largest cluster of Jev projects does not put the model *inside* the agent - it puts it *around* the agent, as a cheap judgment layer.

---

## Why this exploded first

A coding agent has a structural problem: it makes many small decisions that are hard to express as code and too cheap to justify a frontier call.

- Is this tool call safe to auto-approve?
- Does this tool result matter for the task at hand?
- Is the agent stuck in a retry loop?
- Did it actually finish, or did it just say it did?
- Which of the 180 installed skills applies here?

Every one of these is a narrow semantic judgment. Every one repeats constantly. Every one costs more to get wrong than to check. That is the exact profile for a System One model.

And the economics are decisive. [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) measured **~$0.00004 and 0.3 s per judgment**, "which is why it can fire on every guarded call."

---

## The harness surface

```
                     +----------------------------------------+
   agent turn -----> | skill routing         (Choice)         |   which skill to load
                     | action guard          (Choice)         |   allow / ask / deny
                     | context sieve         (Noul per block) |   keep or evict
                     | slop check            (Noul)           |   is this code garbage
                     | stuck detection       (Noul)           |   same strategy repeating
                     | done verification     (Noul)           |   is the claim evidenced
                     +----------------------------------------+
                                        |
                                   agent proceeds
```

Each is independent. Each fires in parallel with the others over the same state. Each returns a typed answer your harness code thresholds.

---

## The six guards, with real implementations

### 1. Action guard - deny / ask / allow

Risk-score every tool call with session context before it runs.

```python
questions={
    "is_irreversible": Noul(
        "Would `proposed.call` permanently destroy or overwrite data "
        "that cannot be recovered?"
    ),
    "is_off_task": Noul(
        instructions={
            "question": "Is `proposed.call` unrelated to `task.goal`?",
            "compare": ["`proposed.call`", "`task.goal`"],
        },
    ),
    "touches_secrets": Noul(
        "Does `proposed.call` read or transmit credentials or environment files?"
    ),
    "risk": Score(
        instructions="How much damage would `proposed.call` cause if wrong?",
        criteria=["Read-only or easily reverted",
                  "Modifies project files",
                  "Irreversible or affects external systems"],
    ),
}
```

**Real implementations:** [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) (with the 6-vs-0 measured result and 42 held calls across 17,160 guarded calls), [y0usaf/pi-jev](https://github.com/y0usaf/pi-jev), [leepokai/jev-guard](https://github.com/leepokai/jev-guard), [jomatsu/pi-jev-auto-mode](https://github.com/jomatsu/pi-jev-auto-mode).

**The key design detail from pi-warden:** it *steers* the agent instead of interrupting the user. The verdict and the violated rule get quoted back into the agent's own context, so the agent re-plans. You keep working. The measured result - 6 rule breaks without the guard, 0 with it - is a real, if small, controlled comparison.

### 2. Context sieve - keep or evict

Every large tool result is judged before it enters the context window. Jev answers one yes/no question per block: *is this block needed for the current task?* Confident-no blocks are replaced with a stub that points at a recall mechanism.

**Real implementations:**
- [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) (848★) replaces Claude Code's compaction summary with Jev decisions. It never rewrites anything - it only deletes tool calls and results Jev says are no longer needed, and user/assistant text stays verbatim.
- [GhalebDweikat/winnow](https://github.com/GhalebDweikat/winnow) splits a result into ~25-line blocks and asks one Noul per block, keeping confident-yes and uncertain blocks verbatim and stubbing confident-no blocks with a recall key.
- [compozy/yoshi](https://github.com/compozy/yoshi) is a context-pruning proxy for Claude Code and Codex.

**Why it works:** a compaction summary is lossy. A file path, exact error, or constraint can disappear even when it matters later. Deletion-plus-recall is not lossy - the full text is cached and restored on demand. That is a better contract than summarization, and Jev makes the keep/evict decision cheap enough to run on every result.

### 3. Skill routing - pick the one that matters

With a large skill library, *choosing* is itself a task. Jev ranks installed skills against live session context and names the one worth loading.

**Real implementations:**
- [Dicklesworthstone/skillranker](https://github.com/Dicklesworthstone/skillranker) - a Rust CLI with Claude Code hooks, TUI, and local calibration.
- [ShivamPansuriya/jev-skill-gate](https://github.com/ShivamPansuriya/jev-skill-gate) reports cutting Claude Code's skill manifest by ~75% by scoring every installed skill for relevance and hiding the rest.
- [DECRUX9812/typesafe-skill-router](https://github.com/DECRUX9812/typesafe-skill-router) for the Hermes agent, ~$0.001 per route.
- [kitze/skillbox](https://github.com/kitze/skillbox) adds optional Jev recommendations to a self-hosted skill library.

**The TypeSafe cookbook version** is the cleanest reference: pick at most one skill for an agent turn out of the 182 in Nous Research's Hermes catalog. One request ranks every skill *and* asks whether the turn needs one at all; a second reads the top three properly and can reject all of them. The Choice picks a skill; the Nouls decide whether to suggest one at all. Source: [skill suggestion cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion)

That two-stage design is worth internalizing: **a `Choice` is relative** (settles which option wins) while a `Noul` is absolute (can be low for all options). You need both when "none of these" is a real possibility.

### 4. Slop detection - name the pattern

[DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) names stubs, restating comments, dead code, hedging, and padded replies, then quotes the specific problem back so the agent fixes it on the next edit.

[huntedman/JevLint](https://github.com/huntedman/JevLint) does configurable semantic linting with file-level `Noul` judgments and a magic-strings plugin. [BunsDev/clarity-judge](https://github.com/BunsDev/clarity-judge) is a multi-axis writing quality checker where each named check gets its own verdict and confidence. [opaielsheikh/typesafe-migration-guard](https://github.com/opaielsheikh/typesafe-migration-guard) reviews database migration safety.

This is *semantic* linting - the checks you could never write as regexes, like "is this a stub" or "does this comment merely restate the code".

### 5. Stuck detection - break the loop

Notice when the agent has failed the same way with the same strategy and ask for a new hypothesis.

```python
questions={
    "same_strategy_failing": Noul(
        "Have the last three failures used the same approach?"
    ),
    "new_hypothesis_needed": Noul(
        "Does `recent_attempts` suggest the current approach cannot succeed?"
    ),
}
```

Cheap, and it converts a long expensive loop into one correction.

### 6. Done verification - evidence, not claims

Catch "done" claims after code changes when no test, build, or lint actually passed.

```python
questions={
    "tests_actually_ran": Noul(
        "Does `session.evidence` show a test, build, or lint command "
        "completing successfully after the last code change?"
    ),
    "claim_is_evidenced": Noul(
        "Is `agent.final_message` supported by `session.evidence`?"
    ),
    "work_is_complete": Noul(
        "Does `session.evidence` show the original `task.goal` was achieved?"
    ),
    "work_off_track": Noul(
        "Has the work diverged from `task.goal`?"
    ),
}
```

**Real implementations:** [thruwire/foreman](https://github.com/thruwire/foreman) (200★) runs a "software factory" pattern where Codex workers do the engineering and Foreman independently assesses completion, requirement satisfaction, test sufficiency, and whether the worker is stuck or off track. [qkal/Canny](https://github.com/qkal/Canny) focuses specifically on unevidenced done claims. [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) has this as its "done-check" guard. [alexshpunt/pi-agent-foreman](https://github.com/alexshpunt/pi-agent-foreman) sends agents back to work when they stop early.

Foreman's own framing is the most honest in the ecosystem:

> Foreman is an architectural experiment, not a claim that this design is already better than a conventional coding-agent harness.

That is the right way to present a launch-week harness project.

---

## What the harness projects have in common

Every one of them, without exception:

1. **Code owns the loop.** Jev answers a question; the harness decides what to do with the answer.
2. **Jev advises, code enforces.** Even where Jev can veto, a deterministic layer can override it.
3. **It fires constantly and costs almost nothing.** $0.00004 per call is what makes the design possible.
4. **It steers rather than interrupts.** The result goes back into the agent's context, not into a user dialog.
5. **It fails closed.** A failed guard denies or asks; it does not silently allow.

---

## Design notes specific to harness engineering

### Fire on every relevant event, not on a sample

The whole advantage is that a judgment is cheaper than the tokens it saves. If you are sampling, you are leaving value on the table and you are inconsistent. [DevMortimer/pi-warden](https://github.com/DevMortimer/pi-warden) fires on every guarded call across 17,160 calls.

### Cache by state fingerprint

If the situation has not changed, reuse the last judgment. [RomanSlack/jev-drone](https://github.com/RomanSlack/jev-drone) fingerprints scenes so an unchanged situation reuses the last verdict - a typical 65-second flight costs about 110 calls instead of thousands.

### Do not ask Jev to decide what code can decide

The harness should check the cheap deterministic conditions first: is the command on the allowlist, is the path inside the repo, has the test file changed. Jev handles the fuzzy residue that rules cannot express.

### Put the verdict back into the agent's context

The measured difference between a guard that *tells the agent what rule it broke* and one that just blocks is the difference between a self-correcting agent and a stuck one. Naming the violation is what makes the correction cheap.

### Measure the guard

pi-warden's 150 paired headless runs, 6 violations without the guard and 0 with it, is the only controlled measurement in the category and it is why that project is credible. If you ship a guard, A/B it. "We added a guard" is not evidence.

---

## Pitfalls

| Pitfall | Symptom | Fix |
| --- | --- | --- |
| Interrupting the user instead of steering the agent | Dialog fatigue | Feed the verdict back into agent context |
| Failing open | Guard silently disabled on error | Fail closed; error → deny or ask |
| No caching | Redundant calls on unchanged state | Fingerprint the state, reuse verdicts |
| Guarding with a frontier model | Cost exceeds the value | Jev is the point; keep it cheap |
| Unmeasured guards | Cannot prove it helps | A/B paired runs |
| Letting Jev own the loop | Goes off the rails slowly | Code owns control flow, always |

---

## Related

- [02-llm-guardrails-and-verification.md](02-llm-guardrails-and-verification.md) - the guardrail recipes
- [04-search-reranking-and-rag.md](04-search-reranking-and-rag.md) - the retrieval half of context management
- [Reference: ecosystem](../reference/ecosystem.md) - the full inventory of harness projects
