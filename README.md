# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

PawPal+ turns a loose list of pet care tasks into an explained daily plan. The
implemented features and the algorithms behind them:

- **Pet & task management** — register an owner, add multiple pets, and attach care tasks (title, duration, priority, preferred time, frequency) to each pet.
- **Priority scheduling** — `Scheduler.build_plan()` orders tasks high → low priority (ties broken by shorter duration) and fits them into the owner's available-minutes budget, deferring whatever doesn't fit.
- **Sorting by time** — `Scheduler.sort_by_time()` lists tasks in chronological order by their `"HH:MM"` preferred time, with untimed tasks placed last.
- **Filtering by pet or status** — `Owner.filter_tasks()` narrows tasks by pet name and/or completion status (all / pending / completed).
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags any time slot claimed by two or more tasks (within one pet or across pets) and returns human-readable warnings instead of crashing.
- **Daily / weekly recurrence** — completing a recurring task (`Task.mark_complete()`) automatically spawns the next occurrence, advancing the due date with `datetime.timedelta` (daily → +1 day, weekly → +7 days).
- **Plan reasoning** — every plan explains which tasks were scheduled, how much time was used, and what was deferred and why (`Plan.explain()`).
- **Two front ends** — an interactive Streamlit UI (`app.py`) and a terminal demo (`main.py`), both driven by the same logic layer.
- **Automated tests** — a `pytest` suite covering the core behaviors (see [Testing PawPal+](#-testing-pawpal)).

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Running PawPal+

```bash
streamlit run app.py   # interactive web UI
python main.py         # terminal demo (sample output below)
```

See the [Demo Walkthrough](#-demo-walkthrough) for a full example run and annotated CLI output.

## 🧪 Testing PawPal+

Run the automated test suite from the project root:

```bash
python -m pytest
```

**What the tests cover** ([`tests/test_pawpal.py`](tests/test_pawpal.py)):

- **Task completion** — `mark_complete()` flips a task's status to done.
- **Task addition** — adding a task to a `Pet` increases that pet's task count.
- **Sorting correctness** — `Scheduler.sort_by_time()` returns tasks in chronological order, with untimed tasks placed last.
- **Recurrence logic** — completing a `daily` task spawns a new occurrence on the same pet, due exactly one day later and still pending.
- **Conflict detection** — `Scheduler.detect_conflicts()` flags two tasks that share the same `preferred_time`, and returns an empty list when all times are unique.

**Successful test run:**

```
============================= test session starts ==============================
platform darwin -- Python 3.10.9, pytest-7.1.3, pluggy-1.0.0
rootdir: /Users/andrewansah/Desktop/school work/CodePath/ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 6 items

tests/test_pawpal.py ......                                              [100%]

============================== 6 passed in 0.01s ===============================
```

**Confidence Level: ★★★★☆ (4 / 5)**

All 6 tests pass and cover the core behaviors — sorting, recurrence, conflict detection, and task management — including the trickiest logic (date math via `timedelta` and same-time conflict grouping). I'm holding back the fifth star because a few edge cases aren't covered yet: the double-complete guard, `filter_tasks` status filtering, `once`/non-recurring tasks, over-budget plan deferral, and overlapping-duration conflicts (which `detect_conflicts` intentionally does **not** catch). Adding those would raise confidence to 5/5.

## 📐 Smarter Scheduling

Beyond the basic priority-and-time planner, PawPal+ adds four "smarter" behaviors.
Each is implemented as a focused method in [`pawpal_system.py`](pawpal_system.py):

| Feature | Method | Notes |
|---------|--------|-------|
| Sorting by time | `Scheduler.sort_by_time()` | Chronological order by `preferred_time` |
| Sorting by priority | `Scheduler.sort_tasks()` | High → low, ties broken by shorter duration |
| Filtering by pet / status | `Owner.filter_tasks()` | Filter by `pet_name` and/or `completed` |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns on tasks sharing the same time slot |
| Recurring tasks | `Task.mark_complete()` | Spawns the next daily/weekly occurrence |

### Sorting behavior — `Scheduler.sort_by_time()`

Orders a list of tasks chronologically by their `preferred_time`. Because times are
stored as zero-padded `"HH:MM"` strings, a plain string comparison already matches
clock order, so the sort key is a simple lambda — no parsing into numbers needed.
Tasks with no `preferred_time` sort to the end. The existing
`Scheduler.sort_tasks()` remains available for priority-first ordering (high → low,
tie-broken by shorter duration).

### Filtering behavior — `Owner.filter_tasks(pet_name=None, completed=None)`

Returns tasks across all of an owner's pets, optionally narrowed by **pet name**,
by **completion status**, or both. Each argument is independent and ignored when
left as `None`; passing `completed=False` correctly keeps only pending tasks
(the check uses `is not None`, so `False` still filters rather than being skipped).

### Conflict detection logic — `Scheduler.detect_conflicts()`

A lightweight, non-crashing check: it groups tasks by their `preferred_time` and
returns a **list of warning strings** — one per time slot claimed by two or more
tasks — instead of raising an exception. It catches clashes both within a single
pet and across different pets, and skips tasks that have no preferred time or are
already completed (they can't compete for a slot). An empty list means no
conflicts. By design it only flags *exact* same-time matches, not overlapping
durations (documented as a tradeoff in [`reflection.md`](reflection.md)).

### Recurring task logic — `Task.mark_complete()`

When a recurring task is completed, the next occurrence is created automatically.
`mark_complete()` sets the task done and, for a `"daily"` or `"weekly"` frequency,
builds a fresh `Task` whose `due_date` is advanced with `datetime.timedelta`
(daily → today + 1 day, weekly → today + 7 days) and attaches it to the same pet.
Non-recurring tasks (e.g. `"once"`) return `None`, and completing an
already-completed task is a no-op so an occurrence is never spawned twice.

## 🚶 Demo Walkthrough

### Main UI features (`streamlit run app.py`)

The Streamlit app is a single page where the owner can:

- **Enter owner & pet info** — owner name, pet name, species, and the minutes available today.
- **Add tasks** — title, duration, priority, and a preferred time picker; each click attaches a `Task` to the pet and confirms it with a success message.
- **Browse tasks** — a status filter (All / Pending / Completed) and a table that always shows tasks **sorted chronologically**, with a ✅/⏳ status column.
- **See conflict warnings** — the app continuously checks for two tasks at the same time and shows a warning banner, or a green "no conflicts" confirmation.
- **Generate the daily schedule** — one button builds the plan, shows the timed table, minutes used, deferred tasks, and the plain-language reasoning.

### Example workflow

1. **Add the owner & pet** — enter "Jordan", pet "Mochi" (cat), and `60` minutes available.
2. **Add a task** — "Morning walk", 30 min, high priority, preferred time `08:00`, then **Add task** → a success banner confirms it.
3. **Add a clashing task** — add "Feeding" at `08:00` as well.
4. **Review the list** — the table shows both tasks in time order, and a ⚠️ warning appears: two tasks scheduled at 08:00.
5. **Filter** — switch the filter to "Pending" to hide completed tasks.
6. **Generate schedule** — click **Generate schedule** to see today's timed plan, the minutes used, anything deferred, and why.

### Key Scheduler behaviors shown

- **Sorting by time** — tasks added out of order display chronologically (`08:00 → 08:30 → 12:30 → 18:00`), untimed tasks last.
- **Filtering** — completed vs. pending tasks, and per-pet views.
- **Conflict warnings** — two tasks at `08:30` (Medication for Biscuit, Feeding for Mochi) raise a warning instead of failing.
- **Recurrence** — completing the daily "Morning walk" auto-creates tomorrow's occurrence.
- **Priority + budget planning** — tasks are scheduled high → low until the 90-minute budget runs out; "Enrichment play" is deferred.

### Sample CLI output (`python main.py`)

```
Completing 'Morning walk' (due 2026-06-24, daily)
  -> auto-created next occurrence due 2026-06-25

All tasks sorted by time
========================================
  08:00  [✓] Morning walk for Biscuit (30 min, priority: high)
  08:00  [ ] Morning walk for Biscuit (30 min, priority: high)
  08:30  [ ] Medication for Biscuit (5 min, priority: high)
  08:30  [ ] Feeding for Mochi (10 min, priority: high)
  12:30  [ ] Midday feeding for Biscuit (10 min, priority: medium)
  18:00  [ ] Evening walk for Biscuit (30 min, priority: high)
  --:--  [ ] Enrichment play for Mochi (25 min, priority: low)

Filter — only Mochi's tasks
----------------------------------------
  [ ] Feeding for Mochi (10 min, priority: high)
  [ ] Enrichment play for Mochi (25 min, priority: low)

Filter — completed vs pending
----------------------------------------
  Completed:
    [✓] Morning walk for Biscuit (30 min, priority: high)
  Pending:
    [ ] Morning walk for Biscuit (30 min, priority: high)
    [ ] Medication for Biscuit (5 min, priority: high)
    [ ] Feeding for Mochi (10 min, priority: high)
    [ ] Midday feeding for Biscuit (10 min, priority: medium)
    [ ] Evening walk for Biscuit (30 min, priority: high)
    [ ] Enrichment play for Mochi (25 min, priority: low)

Conflict check
----------------------------------------
  ⚠ Conflict at 08:30: 2 tasks scheduled — Medication (Biscuit), Feeding (Mochi).

Today's Schedule for Jordan
========================================
  08:00 — Medication for Biscuit (5 min) [priority: high]
  08:05 — Feeding for Mochi (10 min) [priority: high]
  08:15 — Evening walk for Biscuit (30 min) [priority: high]
  08:45 — Morning walk for Biscuit (30 min) [priority: high]
  09:15 — Midday feeding for Biscuit (10 min) [priority: medium]
----------------------------------------
Time used: 85 of 90 min
Deferred (did not fit):
  - Enrichment play (25 min, low)
----------------------------------------
Why this plan:
  Scheduled 5 task(s) using 85 of 90 available minutes, ordered by priority (high → low). Deferred 1 task(s) that did not fit the budget: Enrichment play.
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
