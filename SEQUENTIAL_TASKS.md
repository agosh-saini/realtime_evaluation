# Sequential Task Tracking

This document explains how to use the sequential task feature to ensure steps are completed in a specific order.

## Overview

The system now supports two types of tasks:

1. **Non-Sequential Tasks** (default): Steps can be completed in any order
2. **Sequential Tasks**: Steps must be completed in a specific order

## How Sequential Tasks Work

### Task Registration

When registering a task, set `sequential: true` to enable sequential mode:

```json
{
  "task_name": "Morning Routine",
  "steps": ["Wake Up", "Brush Teeth", "Get Dressed"],
  "completion_criteria": "All steps completed in order",
  "sequential": true
}
```

### Sequential Behavior

When `sequential: true`:

1. **Next Expected Step**: The system tracks which step should happen next
2. **Order Enforcement**: Only the next expected step will be counted
3. **Out-of-Order Detection**: If a later step is detected too early, a warning is generated
4. **Progress Tracking**: The system shows which step is currently expected

### Example Flow

**Task**: "Greeting Sequence" with steps: `["Wave", "Point", "Thumbs Up"]`

**Sequential Mode (`sequential: true`)**:
```
Initial State:
  next_expected_step: "Wave"
  observed_steps: []

Frame 1: Person waves
  ✓ Correct! "Wave" is the expected step
  next_expected_step: "Point"
  observed_steps: ["Wave"]

Frame 2: Person shows thumbs up
  ✗ Warning! Expected "Point" but got "Thumbs Up"
  next_expected_step: "Point" (unchanged)
  observed_steps: ["Wave"] (not added)

Frame 3: Person points
  ✓ Correct! "Point" is the expected step
  next_expected_step: "Thumbs Up"
  observed_steps: ["Wave", "Point"]

Frame 4: Person shows thumbs up
  ✓ Correct! Final step completed
  next_expected_step: null
  observed_steps: ["Wave", "Point", "Thumbs Up"]
  status: COMPLETED
```

**Non-Sequential Mode (`sequential: false` or omitted)**:
```
Initial State:
  observed_steps: []

Frame 1: Person shows thumbs up
  ✓ Any step is fine!
  observed_steps: ["Thumbs Up"]

Frame 2: Person waves
  ✓ Any step is fine!
  observed_steps: ["Thumbs Up", "Wave"]

Frame 3: Person points
  ✓ All steps completed!
  observed_steps: ["Thumbs Up", "Wave", "Point"]
  status: COMPLETED
```

## API Response Fields

### TaskState with Sequential Support

```json
{
  "task_name": "Greeting Sequence",
  "status": "in_progress",
  "observed_steps": ["Wave"],
  "missing_steps": ["Point", "Thumbs Up"],
  "next_expected_step": "Point",
  "explanation": "Sequential task: waiting for step 'Point' (1/3 completed)",
  "confidence": 0.92
}
```

**New Fields**:
- `next_expected_step`: The step that should happen next (null if non-sequential or all done)
- `explanation`: Updated to show sequential progress

## Prompt Enhancement

When a task is sequential, the vision model receives additional context:

```
**IMPORTANT**: This is a SEQUENTIAL task. The next expected step is: 'Point'.
Pay special attention to detecting this specific action.
```

This helps the model focus on detecting the correct next step.

## Use Cases

### Sequential Tasks
- Assembly instructions (step 1, then step 2, then step 3)
- Dance routines (specific movement sequence)
- Safety procedures (must be done in order)
- Training workflows (progressive steps)
- Recipes (preparation order matters)

### Non-Sequential Tasks
- Checklist items (any order is fine)
- Exercise routines (flexible order)
- Room cleanup (tasks can be done in any order)
- Feature demonstrations (show any feature)

## Testing

Run the test script to see both modes in action:

```bash
python test_sequential.py
```

This will register both sequential and non-sequential tasks so you can compare their behavior.

## Implementation Details

### Model Changes

**TaskDefinition** (`app/models.py`):
```python
class TaskDefinition(BaseModel):
    task_name: str
    steps: List[str]
    completion_criteria: str
    sequential: bool = False  # NEW: Enable sequential mode
```

**TaskState** (`app/models.py`):
```python
class TaskState(BaseModel):
    # ... existing fields ...
    next_expected_step: Optional[str] = None  # NEW: Track next step
```

### Manager Logic

The `TaskManager` (`app/task_manager.py`) now:
- Initializes `next_expected_step` for sequential tasks
- Validates step order before accepting observations
- Updates `next_expected_step` after each correct step
- Generates warnings for out-of-order steps

### Inference Enhancement

The `InferenceEngine` (`app/inference.py`) now:
- Accepts `next_expected_step` and `sequential` parameters
- Adds sequential hints to the prompt
- Helps the vision model focus on the expected action

## Example Code

```python
import requests

# Register a sequential task
sequential_task = {
    "task_name": "Hand Washing Steps",
    "steps": ["Wet Hands", "Apply Soap", "Scrub", "Rinse", "Dry"],
    "completion_criteria": "Proper hand washing sequence",
    "sequential": True
}

response = requests.post(
    "http://localhost:8000/task/register",
    json=sequential_task
)

state = response.json()
print(f"Next expected: {state['next_expected_step']}")
# Output: Next expected: Wet Hands

# Later, after sending frames...
status = requests.get(
    "http://localhost:8000/task/status",
    params={"task_name": "Hand Washing Steps"}
).json()

print(f"Progress: {len(status['observed_steps'])}/{len(sequential_task['steps'])}")
print(f"Waiting for: {status['next_expected_step']}")
```

## Tips

1. **Clear Step Names**: Use descriptive, unambiguous step names (e.g., "Wave Left Hand" vs "Wave")
2. **Reasonable Sequence Length**: Keep sequential tasks to 3-7 steps for best results
3. **Visual Distinction**: Ensure each step is visually distinct from others
4. **Timing**: Allow enough time between steps for detection
5. **Feedback**: Monitor `explanation` field for progress and warnings
