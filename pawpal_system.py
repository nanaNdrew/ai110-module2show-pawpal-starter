"""PawPal+ logic layer.

Backend classes for the PawPal+ pet care planning assistant. These mirror the
UML in diagrams/uml.mmd:

    Owner  1 --> *  Pet  1 --> *  Task
    Scheduler retrieves Tasks across an Owner's Pets and produces a Plan.
"""

from __future__ import annotations

from datetime import date, timedelta

# Maps a priority label to a sortable rank (higher = more important).
PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}

# How many days forward each recurring frequency repeats. A frequency not
# listed here (e.g. "once") does not recur.
FREQUENCY_DAYS = {"daily": 1, "weekly": 7}


class Task:
    """A single pet care activity — the raw input to the scheduler."""

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str = "medium",
        frequency: str = "daily",
        preferred_time: str | None = None,
        category: str | None = None,
        completed: bool = False,
        due_date: date | None = None,
    ) -> None:
        """Create a care task with its duration, priority, and scheduling hints."""
        self.title = title  # description of the activity
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.frequency = frequency  # e.g. "daily", "weekly", "once"
        self.preferred_time = preferred_time  # optional fixed time, "HH:MM"
        self.category = category  # e.g. walk, feeding, meds, grooming
        self.completed = completed
        self.due_date = due_date or date.today()  # day this occurrence is due
        self.pet: Pet | None = None  # back-reference, set by Pet.add_task

    def priority_rank(self) -> int:
        """Return a sortable rank for this task's priority (higher = more important)."""
        return PRIORITY_ORDER.get(self.priority.lower(), 0)

    def fits_in(self, remaining_minutes: int) -> bool:
        """Return True if this task still fits in the remaining time budget."""
        return self.duration_minutes <= remaining_minutes

    def mark_complete(self) -> Task | None:
        """Mark this task done; if it recurs, spawn and return the next occurrence.

        A "daily" task's next due date is today + 1 day and a "weekly" task's is
        today + 7 days (computed with timedelta). The new occurrence is attached
        to the same pet. Non-recurring tasks (e.g. "once") return None, and
        completing an already-completed task is a no-op so it never spawns twice.
        """
        if self.completed:
            return None
        self.completed = True

        days = FREQUENCY_DAYS.get(self.frequency.lower())
        if days is None:
            return None  # not a recurring task

        next_task = Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            preferred_time=self.preferred_time,
            category=self.category,
            completed=False,
            due_date=self.due_date + timedelta(days=days),
        )
        if self.pet is not None:
            self.pet.add_task(next_task)
        return next_task

    def mark_incomplete(self) -> None:
        """Mark this task as not yet done."""
        self.completed = False

    def summary(self) -> str:
        """Return a readable one-line description of the task."""
        status = "✓" if self.completed else " "
        owner = f" for {self.pet.name}" if self.pet else ""
        return (
            f"[{status}] {self.title}{owner} "
            f"({self.duration_minutes} min, priority: {self.priority})"
        )

    def __repr__(self) -> str:
        """Return a debug representation of the task."""
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority})"


class Pet:
    """An animal the owner cares for; owns the tasks belonging to it."""

    def __init__(self, name: str, species: str = "other") -> None:
        """Create a pet with a name, species, and an empty task list."""
        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> Task:
        """Attach a care task to this pet and set its back-reference."""
        task.pet = self
        self.tasks.append(task)
        return task

    def edit_task(self, task: Task, **kwargs) -> Task:
        """Update fields on an existing task (e.g. duration_minutes=15)."""
        for key, value in kwargs.items():
            if not hasattr(task, key):
                raise AttributeError(f"Task has no attribute {key!r}")
            setattr(task, key, value)
        return task

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        self.tasks.remove(task)
        task.pet = None

    def list_tasks(self) -> list[Task]:
        """Return all of this pet's tasks."""
        return list(self.tasks)

    def pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def __repr__(self) -> str:
        """Return a debug representation of the pet."""
        return f"Pet({self.name!r}, {self.species}, {len(self.tasks)} tasks)"


class Owner:
    """The person using the app; manages pets and exposes all their tasks."""

    def __init__(
        self,
        name: str,
        available_minutes: int = 0,
        preferences: dict | None = None,
    ) -> None:
        """Create an owner with available time, preferences, and no pets yet."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: dict = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> Pet:
        """Add a pet to this owner."""
        self.pets.append(pet)
        return pet

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        self.pets.remove(pet)

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has available for pet care today."""
        self.available_minutes = minutes

    def set_preference(self, key: str, value) -> None:
        """Set an owner preference that influences the plan."""
        self.preferences[key] = value

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def pending_tasks(self) -> list[Task]:
        """Return every not-yet-completed task across all pets."""
        return [t for t in self.all_tasks() if not t.completed]

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
    ) -> list[Task]:
        """Return tasks across all pets, optionally filtered by pet and/or status.

        Pass pet_name to keep only that pet's tasks, and/or completed=True/False
        to keep only done/not-done tasks. Arguments left as None are ignored.
        """
        tasks = self.all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet and t.pet.name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def __repr__(self) -> str:
        """Return a debug representation of the owner."""
        return f"Owner({self.name!r}, {len(self.pets)} pets)"


class Plan:
    """The finished daily plan — what the owner views, plus the reasoning behind it."""

    def __init__(self) -> None:
        """Create an empty plan with no scheduled or deferred tasks."""
        self.scheduled_items: list[tuple[str, Task]] = []  # ordered (time, Task)
        self.deferred_tasks: list[Task] = []
        self.total_minutes_used: int = 0
        self.reasoning: str = ""

    def add_item(self, time: str, task: Task) -> None:
        """Add a scheduled task at the given clock time."""
        self.scheduled_items.append((time, task))
        self.total_minutes_used += task.duration_minutes

    def explain(self) -> str:
        """Return the human-readable explanation of why tasks were chosen and ordered."""
        return self.reasoning

    def to_table(self) -> list[dict]:
        """Return the plan as rows suitable for display in the UI."""
        return [
            {
                "time": time,
                "task": task.title,
                "pet": task.pet.name if task.pet else "",
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
            }
            for time, task in self.scheduled_items
        ]

    def __str__(self) -> str:
        """Return the plan as a readable multi-line schedule."""
        if not self.scheduled_items:
            return "No tasks scheduled."
        return "\n".join(
            f"{time} — {task.title} ({task.duration_minutes} min) "
            f"[priority: {task.priority}]"
            for time, task in self.scheduled_items
        )


class Scheduler:
    """The brain: retrieves, organizes, and schedules tasks across an owner's pets."""

    def __init__(
        self,
        available_minutes: int = 0,
        strategy: str = "priority",
        day_start: str = "08:00",
    ) -> None:
        """Create a scheduler with a time budget, strategy, and day start time."""
        self.available_minutes = available_minutes
        self.strategy = strategy
        self.day_start = day_start  # clock time the plan starts from

    def get_tasks(self, owner: Owner) -> list[Task]:
        """Retrieve all pending (incomplete) tasks across the owner's pets."""
        return owner.pending_tasks()

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high first), tie-breaking by shorter duration."""
        return sorted(
            tasks,
            key=lambda t: (-t.priority_rank(), t.duration_minutes),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Order tasks chronologically by their 'HH:MM' preferred_time.

        Zero-padded 'HH:MM' strings sort correctly with a plain string compare,
        so the lambda key sorts on preferred_time directly. Tasks with no
        preferred time sort last (the leading bool is False for timed tasks).
        """
        return sorted(
            tasks,
            key=lambda t: (t.preferred_time is None, t.preferred_time or ""),
        )

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a warning message for each preferred_time wanted by 2+ tasks.

        Lightweight, non-crashing check: tasks are grouped by their 'HH:MM'
        preferred_time and any slot claimed more than once becomes a warning
        string. Tasks with no preferred time can't clash, and completed tasks no
        longer compete for a slot, so both are skipped. Returns an empty list
        when there are no conflicts.
        """
        by_time: dict[str, list[Task]] = {}
        for task in tasks:
            if task.preferred_time is None or task.completed:
                continue
            by_time.setdefault(task.preferred_time, []).append(task)

        warnings: list[str] = []
        for time, clashing in sorted(by_time.items()):
            if len(clashing) > 1:
                names = ", ".join(
                    f"{t.title} ({t.pet.name if t.pet else 'no pet'})"
                    for t in clashing
                )
                warnings.append(
                    f"⚠ Conflict at {time}: {len(clashing)} tasks scheduled — {names}."
                )
        return warnings

    def select_tasks(
        self, tasks: list[Task], available_minutes: int
    ) -> tuple[list[Task], list[Task]]:
        """Choose tasks that fit the time budget; return (chosen, deferred)."""
        chosen: list[Task] = []
        deferred: list[Task] = []
        remaining = available_minutes
        for task in tasks:
            if task.fits_in(remaining):
                chosen.append(task)
                remaining -= task.duration_minutes
            else:
                deferred.append(task)
        return chosen, deferred

    def build_plan(
        self,
        tasks: list[Task],
        available_minutes: int | None = None,
        start_time: str | None = None,
    ) -> Plan:
        """Build and return a daily Plan from the given tasks and time budget.

        Tasks are sorted by priority, selected until the time budget runs out,
        and assigned clock times rolled forward from start_time by their durations.
        """
        budget = self.available_minutes if available_minutes is None else available_minutes
        clock = start_time or self.day_start

        ordered = self.sort_tasks(tasks)
        chosen, deferred = self.select_tasks(ordered, budget)

        plan = Plan()
        cursor = clock
        for task in chosen:
            plan.add_item(cursor, task)
            cursor = self._advance(cursor, task.duration_minutes)
        plan.deferred_tasks = deferred
        plan.reasoning = self._explain(chosen, deferred, budget)
        return plan

    def plan_for_owner(self, owner: Owner, start_time: str | None = None) -> Plan:
        """Convenience: retrieve an owner's pending tasks and build their daily plan."""
        budget = owner.available_minutes or self.available_minutes
        return self.build_plan(self.get_tasks(owner), budget, start_time)

    # --- helpers ---------------------------------------------------------

    @staticmethod
    def _advance(time_str: str, minutes: int) -> str:
        """Add minutes to an 'HH:MM' clock time, wrapping at 24h."""
        hours, mins = (int(part) for part in time_str.split(":"))
        total = (hours * 60 + mins + minutes) % (24 * 60)
        return f"{total // 60:02d}:{total % 60:02d}"

    @staticmethod
    def _explain(chosen: list[Task], deferred: list[Task], budget: int) -> str:
        """Build the human-readable reasoning for a plan."""
        used = sum(t.duration_minutes for t in chosen)
        parts = [
            f"Scheduled {len(chosen)} task(s) using {used} of {budget} available "
            f"minutes, ordered by priority (high → low)."
        ]
        if deferred:
            names = ", ".join(t.title for t in deferred)
            parts.append(
                f"Deferred {len(deferred)} task(s) that did not fit the budget: {names}."
            )
        else:
            parts.append("All tasks fit within the available time.")
        return " ".join(parts)
