# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

PawPal+ is built around three core actions a pet owner can perform:

1. **Add or edit a pet care task.** The owner records a care task — such as a walk, feeding, medication, grooming, or enrichment — and gives it at least a duration (how long it takes) and a priority (how important it is). These tasks are the raw input the app plans around, so the owner can add new ones or edit existing ones as their pet's needs change.

2. **Generate a daily plan.** The owner asks the app to build a schedule for the day. The scheduler takes all the tasks and fits them into the time the owner has available, ordering them by priority and setting aside or deferring lower-priority tasks when there isn't enough time for everything. This is the app's main job: turning a loose list of tasks into a realistic plan.

3. **View the plan and its reasoning.** The owner sees the finished schedule laid out clearly — for example, a timed list showing each task, its duration, and its priority — along with an explanation of why the app chose that plan (which tasks it included, which it dropped, and why). This lets the owner trust and act on the plan instead of just receiving an opaque list.

A supporting action is entering basic owner and pet info, which gives the plan context (whose pet it is and any owner preferences).

**a. Initial design**

My initial UML had five classes, each with a single clear responsibility:

- **Task** — represents one pet care task. It holds the data the scheduler needs (title, duration, priority) plus optional details (category, preferred time, recurring). It is responsible for answering questions about itself: how important it is (`priority_rank`), whether it still fits in the remaining time (`fits_in`), and how to describe itself (`summary`).
- **Pet** — represents an animal (name, species) and owns the list of tasks for that pet. It is responsible for managing its own tasks (`add_task`, `edit_task`, `remove_task`, `list_tasks`).
- **Owner** — represents the person using the app. It holds the owner's name, available time, and preferences, and owns the list of pets. It is responsible for managing pets and the constraints the owner controls (`add_pet`, `set_available_time`, `set_preference`).
- **Scheduler** — the "brain." It takes a list of tasks plus constraints and is responsible for the planning algorithm: ordering tasks by priority (`sort_tasks`), choosing which fit the time budget (`select_tasks`), handling conflicts (`resolve_conflicts`), and assembling the result (`build_plan`).
- **Plan** — the output the owner views. It holds the scheduled items, the deferred (dropped) tasks, total time used, and the reasoning. It is responsible for presenting itself (`to_table`) and explaining the choices (`explain`).

The key design decision was separating the **algorithm** (Scheduler) from the **result** (Plan), so the scheduler can be unit-tested in isolation — give it tasks, assert the plan — without involving the UI or storage. Relationships: an Owner has many Pets, a Pet has many Tasks, and the Scheduler reads Tasks to produce a Plan.

**b. Design changes**

After drafting the skeleton I reviewed it for missing relationships and bottlenecks and made two changes:

1. **Added a `Task → Pet` back-reference.** Originally a Task had no link to its Pet, but the Scheduler flattens tasks from multiple pets into one list and the Plan only stored `(time, task)`. That meant a generated plan couldn't say *whose* task it was (e.g. "walk Mochi"). I added a `pet` attribute on `Task` (set by `Pet.add_task`) so ownership survives into the plan. This makes the relationship navigable in both directions, which matters once an owner has more than one pet.

2. **Added a clock-time source to the Scheduler.** The sample output shows tasks at real times (`08:00 — Morning walk`) and `Plan.add_item` expects a time, but nothing in the design computed one. I added a `day_start` attribute on `Scheduler` and a `start_time` parameter on `build_plan`, so scheduled tasks can be assigned clock times rolled forward by their durations. Without this the scheduler could order and select tasks but never actually place them on a clock.

I also noticed that **owner preferences never reach the Scheduler** (`build_plan` only receives tasks and a time budget). I chose *not* to fix this yet — basic priority-and-time scheduling works without it, and I'd rather add preference handling once the core algorithm is proven, in line with the "implement in small increments" approach. I've noted it as a known limitation to revisit.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler weighs four constraints: **available time** (the owner's daily minute budget), **task priority** (high / medium / low), **preferred time** (an optional `"HH:MM"` slot), and **frequency** (daily / weekly / once, which drives recurrence). Owner *preferences* exist as a field but don't yet influence the plan — I left that as a known limitation rather than half-implement it.

I decided **time and priority mattered most** because they define the app's core job: a busy owner has a fixed amount of time and more tasks than will fit, so the scheduler's real value is choosing *which* tasks happen and *in what order*. That's why `build_plan` sorts by priority (high → low, ties broken by shorter duration) and then fills the time budget, deferring whatever doesn't fit. Preferred time and frequency are "smarter" refinements layered on top — they improve sorting, conflict warnings, and recurrence, but the plan is still useful without them. Ordering the constraints this way kept each build increment shippable: priority-and-time scheduling worked end to end before I added the more situational features.

**b. Tradeoffs**

One deliberate tradeoff is in how `Scheduler.detect_conflicts` flags scheduling clashes: **it only catches tasks that request the exact same `preferred_time`, not tasks whose durations overlap.** The implementation groups tasks by their `"HH:MM"` string and warns about any slot claimed by two or more tasks. So a 30-minute walk at 08:00 and a feeding at 08:30 are treated as conflict-free, even though the walk actually runs until 08:30 and the two overlap in real time. A true overlap check would convert each task to a `(start, end)` interval and compare ranges (e.g. `next.start < prev.end`).

This tradeoff is reasonable for the scenario for three reasons. First, it keeps the check **lightweight and non-crashing** — it's a single pass that builds a dict and returns warning strings, with no time arithmetic or edge cases around midnight wraparound, so it can't throw and derail the plan. Second, **exact-match conflicts are the most common and most confusing case** for a pet owner: accidentally typing 08:30 for two different pets' feedings is the mistake people actually make, and that's exactly what the warning surfaces. Third, the conflict check is **advisory, not blocking** — the scheduler still builds a complete plan and rolls tasks forward sequentially so nothing literally double-books the clock; the warning just nudges the owner to review. Given that the plan already separates tasks in time when it lays them out, the cost of missing a duration overlap is low, while the benefit of catching obvious same-time mistakes is high. Full interval-overlap detection is a clear next iteration, but it wasn't worth the added complexity for this version.

---

## 3. AI Collaboration

**a. How you used AI**

I used an AI coding assistant throughout: brainstorming the UML, generating class skeletons from that UML, implementing the scheduling logic in small increments, writing tests, and connecting the logic to the Streamlit UI. The most effective prompts were **specific and bounded** — e.g. "add a `sort_by_time` method that uses a lambda key to sort `"HH:MM"` strings" or "make `mark_complete` spawn the next occurrence using `timedelta`." Vague prompts produced generic code; naming the method, the data shape, and the constraint produced code I could drop in.

**Which AI features were most effective.** Three stood out. First, **agentic, multi-file edits** — the assistant could add a method to `pawpal_system.py`, wire it into `main.py`, and add a test in one pass, which kept the logic, demo, and tests in sync. Second, **running code in the terminal as it went** — it executed `python main.py` and `python -m pytest` after each change and pasted the real output, so I caught problems immediately instead of trusting that the code "looked right." Third, **reading the existing file before editing** — because it inspected the actual class definitions first, new methods matched my existing naming and docstring style instead of inventing a parallel convention.

**How separate chat sessions per phase helped.** I ran each phase (design → skeletons → logic → tests → UI → docs) as its own focused session. This kept each conversation centered on one goal, so the assistant's context wasn't cluttered with unrelated earlier decisions, and it gave me clean checkpoints — I could finish a phase, commit, and start the next session fresh. It also made it easier to *be the reviewer*: with one phase per session, I could read the whole diff for that phase before moving on, rather than losing track inside one giant thread.

**b. Judgment and verification**

**A suggestion I modified.** When I added conflict detection, the assistant's first version grouped tasks purely by `preferred_time`. Running it surfaced a false positive: a *completed* "Morning walk" and the recurring copy it had just spawned both showed at 08:00, so the tool reported a conflict between a task and its own future occurrence. I rejected that behavior and had it refined to **skip completed tasks** in `detect_conflicts`, since a finished task isn't competing for a slot. That single change removed the bogus warning and left only the real cross-pet clash. A second, smaller catch: when AI suggested pushing owner *preferences* into the scheduler early, I declined and logged it as a limitation instead, to keep the core algorithm clean and provable first.

**How I verified AI output.** I never accepted code on appearance alone. I (1) ran `main.py` and read the actual terminal output against what I expected, (2) ran the `pytest` suite after every change, and (3) wrote targeted tests for the riskiest logic — the `timedelta` date math and the conflict grouping — so the behavior was pinned, not assumed. The linter also flagged a stray unused `import date` the AI left behind, which I had it remove. Treating the assistant's output as a *draft to verify* rather than a finished answer is what caught the conflict-detection bug.

---

## 4. Testing and Verification

**a. What you tested**

My `pytest` suite covers six behaviors: task completion flipping status, adding a task increasing a pet's task count, `sort_by_time` returning chronological order with untimed tasks last, completing a daily task spawning a next-day occurrence, `detect_conflicts` flagging two tasks at the same time, and `detect_conflicts` returning an empty list when times are unique. These were important because they're the **core promises of the app** and the places most likely to break silently — the recurrence test pins the `timedelta` date math (an off-by-one would be invisible otherwise), and the two conflict tests guard both the positive and negative cases so a future change can't quietly stop detecting clashes.

**b. Confidence**

I'm **moderately-to-highly confident (about 4/5)**. The happy paths and the trickiest logic are tested and passing, and I verified the end-to-end flow by running `main.py` and reading the output. What holds me back from full confidence is the untested edge cases. If I had more time I'd test: the double-complete guard (completing a task twice should spawn only one successor), `filter_tasks` correctly handling `completed=False` versus `None`, non-recurring (`once`) tasks returning `None`, an over-budget plan deferring the right tasks, a task larger than the entire budget, and month/year rollover for recurrence (Dec 31 → Jan 1). I'd also add a test documenting that overlapping *durations* are intentionally **not** flagged, so that boundary is a conscious contract.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the **clean separation between the algorithm (`Scheduler`) and the result (`Plan`)**. Because the scheduler just takes tasks and returns a plan, I could unit-test the logic in isolation and reuse the exact same backend for both the terminal demo and the Streamlit UI without changing it. The conflict-detection feature also came out well — returning warning *strings* instead of raising kept it lightweight and let both front ends decide how to display the warnings.

**b. What you would improve**

The biggest improvement would be to **actually honor `preferred_time` when building the plan**. Right now the scheduler sorts and detects conflicts by preferred time, but `build_plan` still rolls tasks forward sequentially from `day_start`, so a task asking for 08:00 can land at 08:40. I'd also upgrade conflict detection from exact-match to true **interval overlap** (comparing `(start, end)` ranges), and finally route owner **preferences** into the scheduler so the plan reflects them. Each is a contained next increment rather than a redesign.

**c. Key takeaway**

The biggest thing I learned is what it means to be the **"lead architect" when working with a powerful AI assistant**: the AI is fast at producing code, but *I* own the design decisions, the constraints, and the definition of "correct." My job was to set direction (what to build and in what order), keep the system coherent (rejecting suggestions that muddied the design, like pushing preferences in too early), and verify everything (running tests and reading real output, which is how I caught the conflict-detection false positive). The AI accelerated the *typing and exploration*, but the architecture stayed clean only because I treated its output as a draft to review, not an authority to follow. Leading the AI with small, specific, verifiable tasks — one phase per session — was far more effective than asking it to "build the app" and hoping the pieces fit.
