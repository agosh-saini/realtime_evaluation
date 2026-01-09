# Backend Service

FastAPI service for local VLM inference.

## Files

*   `main.py`: Entry point. API endpoints for `register` and `evaluate`.
*   `inference.py`: Wraps `mlx_vlm`. Loads `Qwen2-VL-2B-Instruct-4bit`. Handles prompt engineering and image processing.
*   `models.py`: Pydantic data models (`TaskDefinition`, `FrameObservation`, `TaskState`).
*   `task_manager.py`: State machine. Tracks progress against registered tasks.
*   `prompts.py`: System prompts used for the VLM to ensure consistent JSON output.

## API Reference

### `POST /task/register`
Initialize a new task tracking session.
```json
{
  "task_name": "My Task",
  "steps": ["Step 1", "Step 2"],
  "sequential": true
}
```

### `POST /frame/evaluate`
Send a frame for analysis.
```json
{
  "task_name": "My Task",
  "image_base64": "<base64_string>",
  "timestamp": 123456789.0
}
```
Returns: `TaskState` object (status, current step, history).
