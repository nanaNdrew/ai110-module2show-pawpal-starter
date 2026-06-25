# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

PawPal+ is built around three core actions a pet owner can perform:

1. **Add or edit a pet care task.** The owner records a care task — such as a walk, feeding, medication, grooming, or enrichment — and gives it at least a duration (how long it takes) and a priority (how important it is). These tasks are the raw input the app plans around, so the owner can add new ones or edit existing ones as their pet's needs change.

2. **Generate a daily plan.** The owner asks the app to build a schedule for the day. The scheduler takes all the tasks and fits them into the time the owner has available, ordering them by priority and setting aside or deferring lower-priority tasks when there isn't enough time for everything. This is the app's main job: turning a loose list of tasks into a realistic plan.

3. **View the plan and its reasoning.** The owner sees the finished schedule laid out clearly — for example, a timed list showing each task, its duration, and its priority — along with an explanation of why the app chose that plan (which tasks it included, which it dropped, and why). This lets the owner trust and act on the plan instead of just receiving an opaque list.

A supporting action is entering basic owner and pet info, which gives the plan context (whose pet it is and any owner preferences).

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
