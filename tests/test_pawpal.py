"""Tests for the PawPal+ logic layer."""

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip the task's status to completed."""
    task = Task("Walk the dog", duration_minutes=30)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count."""
    pet = Pet("Rex", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feed", duration_minutes=10))

    assert len(pet.tasks) == 1
