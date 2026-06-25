from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Plan, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
available_minutes = st.number_input(
    "Time available today (minutes)", min_value=0, max_value=600, value=60
)

# Create the Owner + Pet once and keep them in the session "vault" so they
# survive Streamlit's reruns; otherwise added tasks would be wiped each click.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(st.session_state.pet)

owner = st.session_state.owner
pet = st.session_state.pet

# Keep the persistent objects in sync with the input boxes.
owner.name = owner_name
owner.set_available_time(int(available_minutes))
pet.name = pet_name
pet.species = species

# One Scheduler drives the display methods (sorting + conflict detection).
scheduler = Scheduler(available_minutes=owner.available_minutes)

st.markdown("### Tasks")
st.caption("Add a few tasks. These feed directly into your scheduler.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    preferred_time = st.time_input("Preferred time", value=time(8, 0))

if st.button("Add task"):
    pet.add_task(
        Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            preferred_time=preferred_time.strftime("%H:%M"),
        )
    )
    st.success(f"Added “{task_title}” at {preferred_time.strftime('%H:%M')}.")

# --- Sorted + filtered task list -----------------------------------------
all_tasks = owner.all_tasks()
if all_tasks:
    st.markdown("#### Current tasks")
    status_filter = st.radio(
        "Show",
        ["All", "Pending", "Completed"],
        horizontal=True,
    )
    completed = {"All": None, "Pending": False, "Completed": True}[status_filter]

    # filter_tasks() narrows by status; sort_by_time() orders chronologically.
    visible = owner.filter_tasks(completed=completed)
    visible = scheduler.sort_by_time(visible)

    if visible:
        st.table(
            [
                {
                    "Time": t.preferred_time or "—",
                    "Task": t.title,
                    "Pet": t.pet.name if t.pet else "",
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Status": "✅ done" if t.completed else "⏳ pending",
                }
                for t in visible
            ]
        )
    else:
        st.info(f"No {status_filter.lower()} tasks to show.")

    # --- Conflict detection ----------------------------------------------
    conflicts = scheduler.detect_conflicts(all_tasks)
    if conflicts:
        st.markdown("#### ⚠️ Scheduling conflicts")
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts — every task has its own time slot.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Calls your Scheduler to plan the owner's day from their pending tasks.")

if st.button("Generate schedule"):
    plan = scheduler.plan_for_owner(owner)

    if plan.scheduled_items:
        st.success(
            f"Scheduled {len(plan.scheduled_items)} task(s) using "
            f"{plan.total_minutes_used} of {owner.available_minutes} available minutes."
        )
        st.markdown("### Today's plan")
        st.table(plan.to_table())
        st.metric("Minutes used", f"{plan.total_minutes_used} / {owner.available_minutes}")
    else:
        st.info("No tasks could be scheduled. Add tasks or increase available time.")

    if plan.deferred_tasks:
        st.warning(
            "Deferred (didn't fit the time budget): "
            + ", ".join(f"{t.title} ({t.duration_minutes} min)" for t in plan.deferred_tasks)
        )

    st.markdown("### Why this plan")
    st.info(plan.explain())
