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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One deliberate tradeoff is in how `Scheduler.detect_conflicts` flags scheduling clashes: **it only catches tasks that request the exact same `preferred_time`, not tasks whose durations overlap.** The implementation groups tasks by their `"HH:MM"` string and warns about any slot claimed by two or more tasks. So a 30-minute walk at 08:00 and a feeding at 08:30 are treated as conflict-free, even though the walk actually runs until 08:30 and the two overlap in real time. A true overlap check would convert each task to a `(start, end)` interval and compare ranges (e.g. `next.start < prev.end`).

This tradeoff is reasonable for the scenario for three reasons. First, it keeps the check **lightweight and non-crashing** — it's a single pass that builds a dict and returns warning strings, with no time arithmetic or edge cases around midnight wraparound, so it can't throw and derail the plan. Second, **exact-match conflicts are the most common and most confusing case** for a pet owner: accidentally typing 08:30 for two different pets' feedings is the mistake people actually make, and that's exactly what the warning surfaces. Third, the conflict check is **advisory, not blocking** — the scheduler still builds a complete plan and rolls tasks forward sequentially so nothing literally double-books the clock; the warning just nudges the owner to review. Given that the plan already separates tasks in time when it lays them out, the cost of missing a duration overlap is low, while the benefit of catching obvious same-time mistakes is high. Full interval-overlap detection is a clear next iteration, but it wasn't worth the added complexity for this version.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
