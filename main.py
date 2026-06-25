"""PawPal+ terminal testing ground.

A quick manual check that the logic layer in pawpal_system.py works end to end.
Run it with:  python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # 1. Create an owner with a daily time budget.
    owner = Owner("Jordan", available_minutes=90)

    # 2. Create at least two pets and add them to the owner.
    biscuit = Pet("Biscuit", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # 3. Add tasks deliberately OUT OF TIME ORDER to prove sort_by_time() works.
    biscuit.add_task(
        Task("Evening walk", duration_minutes=30, priority="high", preferred_time="18:00")
    )
    biscuit.add_task(
        Task("Morning walk", duration_minutes=30, priority="high", preferred_time="08:00")
    )
    mochi.add_task(
        Task("Feeding", duration_minutes=10, priority="high", preferred_time="08:30")
    )
    mochi.add_task(
        Task("Enrichment play", duration_minutes=25, priority="low")  # no preferred time
    )
    biscuit.add_task(
        Task("Midday feeding", duration_minutes=10, priority="medium", preferred_time="12:30")
    )
    # Deliberate clash: Biscuit's medication is set for 08:30, the same slot as
    # Mochi's feeding above — a cross-pet conflict the Scheduler should catch.
    biscuit.add_task(
        Task("Medication", duration_minutes=5, priority="high", preferred_time="08:30")
    )

    # Mark a recurring task done. Because "Morning walk" is daily, completing it
    # auto-creates tomorrow's occurrence and attaches it to Biscuit.
    morning_walk = biscuit.tasks[1]
    print(f"Completing '{morning_walk.title}' (due {morning_walk.due_date}, {morning_walk.frequency})")
    next_walk = morning_walk.mark_complete()
    if next_walk is not None:
        print(f"  -> auto-created next occurrence due {next_walk.due_date}\n")

    # 4. Sorting: show every task ordered chronologically by preferred_time.
    scheduler = Scheduler(day_start="08:00")
    print("All tasks sorted by time")
    print("=" * 40)
    for task in scheduler.sort_by_time(owner.all_tasks()):
        clock = task.preferred_time or "--:--"
        print(f"  {clock}  {task.summary()}")

    # 5. Filtering: by pet name, and by completion status.
    print("\nFilter — only Mochi's tasks")
    print("-" * 40)
    for task in scheduler.sort_by_time(owner.filter_tasks(pet_name="Mochi")):
        print(f"  {task.summary()}")

    print("\nFilter — completed vs pending")
    print("-" * 40)
    print("  Completed:")
    for task in owner.filter_tasks(completed=True):
        print(f"    {task.summary()}")
    print("  Pending:")
    for task in scheduler.sort_by_time(owner.filter_tasks(completed=False)):
        print(f"    {task.summary()}")

    # 6. Conflict detection: warn about tasks competing for the same time slot.
    print("\nConflict check")
    print("-" * 40)
    conflicts = scheduler.detect_conflicts(owner.all_tasks())
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No scheduling conflicts found.")

    # 7. Build today's plan and print it to the terminal.
    plan = scheduler.plan_for_owner(owner)

    print(f"\nToday's Schedule for {owner.name}")
    print("=" * 40)
    if plan.scheduled_items:
        for time, task in plan.scheduled_items:
            pet_name = task.pet.name if task.pet else "?"
            print(
                f"  {time} — {task.title} for {pet_name} "
                f"({task.duration_minutes} min) [priority: {task.priority}]"
            )
    else:
        print("  Nothing scheduled today.")

    print("-" * 40)
    print(f"Time used: {plan.total_minutes_used} of {owner.available_minutes} min")

    if plan.deferred_tasks:
        print("Deferred (did not fit):")
        for task in plan.deferred_tasks:
            print(f"  - {task.title} ({task.duration_minutes} min, {task.priority})")

    print("-" * 40)
    print("Why this plan:")
    print(f"  {plan.explain()}")


if __name__ == "__main__":
    main()
