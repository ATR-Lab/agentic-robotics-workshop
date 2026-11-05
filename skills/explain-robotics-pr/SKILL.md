---
name: explain-robotics-pr
description: Explain a robotics or general software PR through concrete inputs, code paths, and verification evidence so its reviewer can understand the behavior before deciding.
---

Treat this as a read-only understanding pass unless the user also requests changes. Read the requested diff and surrounding implementation, not just its description. Obtain the intended contract and relevant executed-check evidence.

Describe behavior before and after the change with code references. Trace a normal input and a consequential failure case through the changed paths. In robotics, make unit conversions, coordinate transforms, timestamp/clock assumptions, data validity, and command output explicit. For general software, trace the equivalent API/data/error boundaries.

When the reviewer is unclear, identify the specific gap and change the explanation: a numeric walkthrough, small call graph, before/after table, or focused source excerpt. Spending tokens on an unresolved question is useful when it improves understanding. Stop repeated reassurance once the reviewer can explain the change and predict a new case.

Separate observed test output from inference. Agent agreement does not establish correct behavior. For a finding, provide the trigger, expected behavior, affected path, and a way to reproduce. Do not invent a defect just to populate a report.

The talk's motivating example is [Theo Browne's PR-explanation passage around 20:34](https://www.youtube.com/watch?v=q1D90-uGvBg&t=1234); this skill adapts that practice rather than quoting a universal process.

Deliver an explanation, evidence/limitations, and any unresolved decision. Do not approve or merge the PR on the user's behalf unless explicitly requested.
