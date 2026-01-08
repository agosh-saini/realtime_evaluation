from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import TaskDefinition, EvaluateFrameRequest, TaskState
from app.task_manager import manager
from app.inference import engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Local Video Task Evaluator", description="Real-time human task evaluation on Apple Silicon")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Load the model on startup to avoid delays on first request"""
    logging.info("Loading model on startup...")
    try:
        engine.load_model()
        logging.info("Model loaded successfully on startup!")
    except Exception as e:
        logging.error(f"Failed to load model on startup: {e}")
        logging.warning("Model will be loaded on first inference request instead.")

@app.post("/task/register", response_model=TaskState)
async def register_task(task_def: TaskDefinition):
    """Register a new task definition and initialize state."""
    manager.register_task(task_def)
    return manager.get_task_state(task_def.task_name)

@app.post("/frame/evaluate", response_model=TaskState)
async def evaluate_frame(request: EvaluateFrameRequest):
    """Evaluate a single frame and update task state."""
    
    # Check if task exists
    current_state = manager.get_task_state(request.task_name)
    if not current_state:
        raise HTTPException(status_code=404, detail=f"Task '{request.task_name}' not found. Register it first.")
    
    # Get task definition for context
    task_def = manager.task_registry[request.task_name]
    
    # Run Inference
    observation = engine.evaluate_frame(
        image_base64=request.image_base64,
        task_name=request.task_name,
        steps=task_def.steps,
        timestamp=request.timestamp,
        next_expected_step=current_state.next_expected_step,
        sequential=task_def.sequential
    )
    
    logging.info(f"Frame evaluated: {observation}")
    
    # Update State
    new_state = manager.update_with_observation(request.task_name, observation)
    
    return new_state

@app.get("/task/status", response_model=TaskState)
async def get_status(task_name: str):
    """Get the current status of a task."""
    state = manager.get_task_state(task_name)
    if not state:
        raise HTTPException(status_code=404, detail="Task not found")
    return state

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
