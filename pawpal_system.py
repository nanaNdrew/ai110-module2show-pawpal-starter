"""PawPal+ logic layer.

Backend classes for the PawPal+ pet care planning assistant. These mirror the
UML in diagrams/uml.mmd:

    Owner  1 --> *  Pet  1 --> *  Task
    Scheduler reads Tasks and produces a Plan (which contains the chosen Tasks).

This module holds data structure only (attributes) plus method stubs. Scheduling
logic is filled in incrementally per the README workflow (step 4).
"""

from __future__ import annotations


class Task:
    """A single pet care task — the raw input to the scheduler."""

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str = "medium",
        category: str | None = None,
        preferred_time: str | None = None,
        recurring: bool = False,
    ) -> None:
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.preferred_time = preferred_time
        self.recurring = recurring

    def priority_rank(self) -> int:
        """Return a sortable rank for this task's priority (higher = more important)."""
        raise NotImplementedError

    def fits_in(self, remaining_minutes: int) -> bool:
        """Return True if this task still fits in the remaining time budget."""
        raise NotImplementedError

    def summary(self) -> str:
        """Return a readable one-line description of the task."""
        raise NotImplementedError


class Pet:
    """An animal the owner cares for; holds the tasks belonging to it."""

    def __init__(self, name: str, species: str = "other") -> None:
        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def edit_task(self, task: Task, **kwargs) -> None:
        """Update fields on an existing task."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        raise NotImplementedError


class Owner:
    """The person using the app; holds preferences and the pets they care for."""

    def __init__(
        self,
        name: str,
        available_minutes: int = 0,
        preferences: dict | None = None,
    ) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: dict = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        raise NotImplementedError

    def set_available_time(self, minutes: int) -> None:
        """Set how many minutes the owner has available for pet care today."""
        raise NotImplementedError

    def set_preference(self, key: str, value) -> None:
        """Set an owner preference that influences the plan."""
        raise NotImplementedError


class Plan:
    """The finished daily plan — what the owner views, plus the reasoning behind it."""

    def __init__(self) -> None:
        self.scheduled_items: list = []  # ordered (time, Task) slots
        self.deferred_tasks: list[Task] = []
        self.total_minutes_used: int = 0
        self.reasoning: str = ""

    def add_item(self, time: str, task: Task) -> None:
        """Add a scheduled task at the given time."""
        raise NotImplementedError

    def explain(self) -> str:
        """Return a human-readable explanation of why tasks were chosen and ordered."""
        raise NotImplementedError

    def to_table(self) -> list:
        """Return the plan as rows suitable for display in the UI."""
        raise NotImplementedError


class Scheduler:
    """Turns a list of tasks plus constraints into an ordered Plan."""

    def __init__(self, available_minutes: int = 0, strategy: str = "priority") -> None:
        self.available_minutes = available_minutes
        self.strategy = strategy

    def build_plan(self, tasks: list[Task], available_minutes: int | None = None) -> Plan:
        """Build and return a daily Plan from the given tasks and time budget."""
        raise NotImplementedError

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (tie-breaking by duration)."""
        raise NotImplementedError

    def select_tasks(self, tasks: list[Task]) -> list[Task]:
        """Choose tasks that fit the time budget; the rest are deferred."""
        raise NotImplementedError

    def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Resolve overlapping fixed-time tasks."""
        raise NotImplementedError
