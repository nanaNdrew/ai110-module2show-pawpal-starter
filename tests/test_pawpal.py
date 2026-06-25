"""Tests for the PawPal+ logic layer."""

from datetime import timedelta

from pawpal_system import Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip the task's status to completed."""
    task = Task("Walk the dog", duration_minutes=30, frequency="once")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count."""
    pet = Pet("Rex", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feed", duration_minutes=10))

    assert len(pet.tasks) == 1


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should order tasks chronologically, untimed ones last."""
    scheduler = Scheduler()
    evening = Task("Evening walk", 30, preferred_time="18:00")
    morning = Task("Morning walk", 30, preferred_time="08:00")
    midday = Task("Midday feed", 10, preferred_time="12:30")
    untimed = Task("Enrichment", 25)  # no preferred_time -> sorts last

    ordered = scheduler.sort_by_time([evening, untimed, midday, morning])

    assert ordered == [morning, midday, evening, untimed]


def test_daily_task_recurrence_creates_next_day_task():
    """Completing a daily task should spawn a new task due the following day."""
    pet = Pet("Biscuit", species="dog")
    walk = pet.add_task(
        Task("Morning walk", 30, frequency="daily", preferred_time="08:00")
    )

    next_walk = walk.mark_complete()

    # Original is done; a fresh occurrence now exists on the same pet.
    assert walk.completed is True
    assert next_walk is not None
    assert len(pet.tasks) == 2
    # The new task is due exactly one day after the original and starts pending.
    assert next_walk.due_date == walk.due_date + timedelta(days=1)
    assert next_walk.completed is False
    assert next_walk.title == "Morning walk"


def test_detect_conflicts_flags_duplicate_times():
    """detect_conflicts() should warn when two tasks share a preferred_time."""
    scheduler = Scheduler()
    feeding = Task("Feeding", 10, preferred_time="08:30")
    medication = Task("Medication", 5, preferred_time="08:30")
    walk = Task("Walk", 30, preferred_time="09:00")  # no clash

    warnings = scheduler.detect_conflicts([feeding, medication, walk])

    assert len(warnings) == 1
    assert "08:30" in warnings[0]


def test_detect_conflicts_returns_empty_when_no_clash():
    """detect_conflicts() should return an empty list when times are unique."""
    scheduler = Scheduler()
    tasks = [
        Task("Feeding", 10, preferred_time="08:30"),
        Task("Walk", 30, preferred_time="09:00"),
    ]

    assert scheduler.detect_conflicts(tasks) == []
