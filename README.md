# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

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

## 🖥️ Sample Output

Running the terminal testing ground (`python main.py`) produces the following plan,
which orders tasks across both pets by priority and assigns clock times:

```
Today's Schedule for Jordan
========================================
  08:00 — Feeding for Biscuit (10 min) [priority: high]
  08:10 — Feeding for Mochi (10 min) [priority: high]
  08:20 — Morning walk for Biscuit (30 min) [priority: high]
  08:50 — Litter cleanup for Mochi (15 min) [priority: medium]
  09:05 — Enrichment play for Mochi (25 min) [priority: low]
----------------------------------------
Time used: 90 of 90 min
----------------------------------------
Why this plan:
  Scheduled 5 task(s) using 90 of 90 available minutes, ordered by priority (high → low). All tasks fit within the available time.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
