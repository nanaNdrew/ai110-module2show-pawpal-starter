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

    # 3. Add tasks with different durations, priorities, and preferred times.
    biscuit.add_task(
        Task("Morning walk", duration_minutes=30, priority="high", preferred_time="08:00")
    )
    biscuit.add_task(
        Task("Feeding", duration_minutes=10, priority="high", preferred_time="08:30")
    )
    mochi.add_task(
        Task("Feeding", duration_minutes=10, priority="high", preferred_time="08:30")
    )
    mochi.add_task(
        Task("Litter cleanup", duration_minutes=15, priority="medium")
    )
    mochi.add_task(
        Task("Enrichment play", duration_minutes=25, priority="low")
    )

    # 4. Build today's plan and print it to the terminal.
    scheduler = Scheduler(day_start="08:00")
    plan = scheduler.plan_for_owner(owner)

    print(f"Today's Schedule for {owner.name}")
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
