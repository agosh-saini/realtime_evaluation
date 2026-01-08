# Frontend Sequential Task Support - Summary

## Changes Made

### 1. **API Types** (`web-client/src/lib/api.ts`)

Added sequential support to TypeScript interfaces:

```typescript
export interface TaskDefinition {
  task_name: string;
  steps: string[];
  completion_criteria: string;
  sequential?: boolean;  // ← NEW
}

export interface TaskState {
  // ... existing fields ...
  next_expected_step?: string | null;  // ← NEW
}
```

### 2. **Task Form** (`web-client/src/components/TaskForm.tsx`)

**Added:**
- Sequential mode checkbox
- Default gesture steps (Wave, Point, ThumbsUp)
- Visual indicator when sequential is enabled

**UI Changes:**
```tsx
<label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
  <input type="checkbox" checked={sequential} onChange={...} />
  <span style={{ fontWeight: 'bold', color: sequential ? '#0070f3' : 'inherit' }}>
    Sequential Mode
  </span>
  <span style={{ fontSize: '0.85em', color: '#666' }}>
    (Steps must be completed in order)
  </span>
</label>
```

### 3. **Evaluation Panel** (`web-client/src/components/EvaluationPanel.tsx`)

**Major UI Enhancement:**

#### For Sequential Tasks:
- **Visual Progress Tracker**: Shows all steps in order with status indicators
  - ✅ Completed steps (green background)
  - ⏳ Current expected step (yellow background, bold border)
  - ⏸️ Pending steps (white background)

- **Next Expected Step Banner**: Prominent yellow banner showing what action to perform next

#### For Non-Sequential Tasks:
- Original two-column layout (Observed / Missing)

**Visual Design:**
```tsx
{isSequential && (
  <div style={{ /* Sequential progress tracker */ }}>
    {allSteps.map((step, index) => (
      <div style={{
        background: isCompleted ? '#d4edda' : isCurrent ? '#fff3cd' : '#fff',
        border: isCurrent ? '2px solid #ffc107' : '1px solid #ddd',
      }}>
        {index + 1}. {step} {icon}
      </div>
    ))}
  </div>
)}
```

## User Experience

### Before Sequential Mode

Users would:
1. Define task steps
2. Perform steps in any order
3. See checkmarks as each step is detected

### After Sequential Mode

Users can now:
1. **Enable Sequential Mode** via checkbox
2. See **which step should come next** in real-time
3. View **visual progress** through the sequence
4. Get **warnings** if steps are performed out of order

## Visual Indicators

| Icon | Meaning | Background Color |
|------|---------|-----------------|
| ✅ | Step completed | Green (#d4edda) |
| ⏳ | Current expected step | Yellow (#fff3cd) |
| ⏸️ | Pending step | White |

## Example Usage

### Sequential Task: "Greeting Sequence"
```
Steps: ["Wave", "Point", "Thumbs Up"]
Sequential: ✅ Enabled

UI Shows:
┌─────────────────────────────────────┐
│ ⏭️ Next Expected Step: Wave        │  ← Yellow banner
└─────────────────────────────────────┘

📋 Sequential Progress
┌─────────────────────────────────┐
│ 1. Wave        ⏳              │  ← Yellow, bold
│ 2. Point       ⏸️              │  ← Gray
│ 3. Thumbs Up   ⏸️              │  ← Gray
└─────────────────────────────────┘

[After waving]

┌─────────────────────────────────────┐
│ ⏭️ Next Expected Step: Point       │
└─────────────────────────────────────┘

📋 Sequential Progress
┌─────────────────────────────────┐
│ 1. Wave        ✅              │  ← Green
│ 2. Point       ⏳              │  ← Yellow, bold
│ 3. Thumbs Up   ⏸️              │  ← Gray
└─────────────────────────────────┘
```

### Non-Sequential Task: "Random Gestures"
```
Steps: ["Wave", "Point", "Thumbs Up"]
Sequential: ❌ Disabled

UI Shows:
✅ Observed Steps    ⬜ Missing Steps
- Thumbs Up         - Wave
                    - Point

[Traditional two-column layout]
```

## Testing the Frontend

1. **Start the dev server:**
   ```bash
   cd web-client
   npm run dev
   ```

2. **Test Sequential Mode:**
   - Check "Sequential Mode" checkbox
   - Enter steps: Wave, Point, ThumbsUp
   - Start task
   - Perform gestures IN ORDER
   - Watch the progress tracker update

3. **Test Non-Sequential Mode:**
   - Uncheck "Sequential Mode"
   - Enter same steps
   - Start task
   - Perform gestures IN ANY ORDER
   - See traditional checklist

## Integration with Backend

The frontend now sends `sequential: true/false` when registering tasks, and receives:
- `next_expected_step` in the task state
- Updated `explanation` with sequential context

All changes are backward compatible - existing tasks without sequential will work as before.
