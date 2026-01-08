# Sequential Task Feature - Complete Implementation Summary

## Overview

Added comprehensive sequential task support to the real-time video task evaluator, allowing tasks to enforce step-by-step completion in a specific order.

## What Changed

### Backend Changes

#### 1. Data Models (`app/models.py`)
- Added `sequential: bool = False` to `TaskDefinition`
- Added `next_expected_step: Optional[str] = None` to `TaskState`

#### 2. Task Manager (`app/task_manager.py`)
- Tracks next expected step for sequential tasks
- Validates step order before accepting observations
- Generates warnings for out-of-order steps
- Updates progress messages to show sequential context

#### 3. Inference Engine (`app/inference.py`)
- Accepts `next_expected_step` and `sequential` parameters
- Enhances prompt with sequential hints for the vision model
- Helps model focus on detecting the current expected action

#### 4. API Endpoint (`app/main.py`)
- Passes sequential context to inference engine
- Sends next_expected_step with each frame evaluation

#### 5. Prompts (`app/prompts.py`)
- Improved to be more encouraging about detecting gestures
- Added specific detection guidelines for common gestures
- Dynamically appends sequential hints when applicable

### Frontend Changes

#### 1. Type Definitions (`web-client/src/lib/api.ts`)
- Added `sequential?: boolean` to `TaskDefinition`
- Added `next_expected_step?: string | null` to `TaskState`

#### 2. Task Form (`web-client/src/components/TaskForm.tsx`)
- Added "Sequential Mode" checkbox with description
- Changed default steps to gesture examples (Wave, Point, ThumbsUp)
- Visual feedback when sequential mode is enabled

#### 3. Evaluation Panel (`web-client/src/components/EvaluationPanel.tsx`)
- **Sequential Mode UI:**
  - Visual progress tracker showing all steps in order
  - Color-coded status (green=done, yellow=current, white=pending)
  - Prominent "Next Expected Step" banner
  - Step numbering and icons (✅⏳⏸️)
- **Non-Sequential Mode UI:**
  - Original two-column layout (Observed / Missing)

## Feature Comparison

| Aspect | Non-Sequential | Sequential |
|--------|---------------|------------|
| **Step Order** | Any order | Must follow defined order |
| **Detection** | Any step counts when seen | Only next expected step counts |
| **UI Display** | Two columns (done/missing) | Progress tracker with numbering |
| **Next Step** | Not shown | Highlighted in yellow banner |
| **Completion** | All steps detected (any order) | All steps detected in order |
| **Use Cases** | Checklists, exercises | Assembly, recipes, training |

## How It Works

### Sequential Task Flow

1. **Task Registration:**
   ```json
   POST /task/register
   {
     "task_name": "Assembly",
     "steps": ["Connect A", "Connect B", "Test"],
     "sequential": true
   }

   Response:
   {
     "next_expected_step": "Connect A",
     "observed_steps": [],
     "missing_steps": ["Connect A", "Connect B", "Test"]
   }
   ```

2. **Frame Evaluation (Step 1):**
   ```
   Vision Model Receives:
   - Image of person connecting A
   - Prompt with hint: "Next expected: Connect A"

   Model Detects: "Connect A"

   Response:
   {
     "next_expected_step": "Connect B",  ← Updated!
     "observed_steps": ["Connect A"],
     "missing_steps": ["Connect B", "Test"]
   }
   ```

3. **Frame Evaluation (Wrong Order):**
   ```
   Vision Model Detects: "Test" (but expecting "Connect B")

   Response:
   {
     "next_expected_step": "Connect B",  ← Unchanged
     "observed_steps": ["Connect A"],    ← Not added
     "explanation": "Warning: Step 'Test' detected, but expecting 'Connect B'"
   }
   ```

4. **Frame Evaluation (Correct Order):**
   ```
   Vision Model Detects: "Connect B"

   Response:
   {
     "next_expected_step": "Test",
     "observed_steps": ["Connect A", "Connect B"],
     "missing_steps": ["Test"]
   }
   ```

5. **Completion:**
   ```
   All steps done in order:
   {
     "next_expected_step": null,
     "observed_steps": ["Connect A", "Connect B", "Test"],
     "missing_steps": [],
     "status": "completed",
     "explanation": "All steps completed in correct order."
   }
   ```

## Files Modified

### Backend
- ✅ `app/models.py` - Added sequential fields
- ✅ `app/task_manager.py` - Sequential validation logic
- ✅ `app/inference.py` - Sequential prompt enhancement
- ✅ `app/main.py` - Pass sequential context
- ✅ `app/prompts.py` - Improved gesture detection

### Frontend
- ✅ `web-client/src/lib/api.ts` - Type definitions
- ✅ `web-client/src/components/TaskForm.tsx` - Sequential checkbox
- ✅ `web-client/src/components/EvaluationPanel.tsx` - Progress UI

### Documentation
- ✅ `SEQUENTIAL_TASKS.md` - Feature documentation
- ✅ `FRONTEND_CHANGES.md` - UI changes
- ✅ `test_sequential.py` - Example usage script

## Testing

### Backend Test
```bash
python test_sequential.py
```

This registers both sequential and non-sequential tasks to demonstrate the difference.

### Frontend Test
1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `cd web-client && npm run dev`
3. Open http://localhost:3000
4. Check "Sequential Mode" checkbox
5. Enter steps: Wave, Point, ThumbsUp
6. Start task and perform gestures in order
7. Watch the yellow highlight move through the steps

### API Test
```bash
# Register sequential task
curl -X POST http://localhost:8000/task/register \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "Test",
    "steps": ["Wave", "Point"],
    "completion_criteria": "Both gestures",
    "sequential": true
  }'

# Response includes next_expected_step: "Wave"
```

## Benefits

1. **Clearer User Guidance**: Users know exactly what to do next
2. **Order Enforcement**: Prevents skipping critical steps
3. **Better Feedback**: Visual progress makes status obvious
4. **Flexible System**: Supports both sequential and non-sequential workflows
5. **Enhanced Detection**: Model receives hints about expected actions

## Backward Compatibility

- All existing code continues to work
- `sequential` defaults to `false`
- Non-sequential tasks display in original format
- No breaking changes to API

## Future Enhancements

Potential improvements:
- Step timing requirements (min/max duration)
- Optional vs required steps
- Conditional branching (if X then Y, else Z)
- Step dependencies graph
- Partial credit for incomplete sequences
- Retry mechanism for failed steps

## Quick Start

**For a sequential task:**
```python
task = {
    "task_name": "Coffee Making",
    "steps": ["Grind Beans", "Heat Water", "Brew", "Pour"],
    "sequential": True  # ← Enable sequential mode
}
```

**Result:**
- User must grind beans first
- Then heat water
- Then brew
- Finally pour
- Skipping any step triggers a warning
