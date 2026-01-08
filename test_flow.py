import asyncio
import base64
from app.models import TaskDefinition, EvaluateFrameRequest
from app.main import register_task, evaluate_frame, get_status
from app.inference import engine, FrameObservation

# Override inference to return deterministic sequence for testing
class MockEngine:
    def __init__(self):
        self.sequence = [
            FrameObservation(timestamp=0.0, observation="Person is standing at the sink.", mapped_step=None, confidence=0.9),
            FrameObservation(timestamp=1.0, observation="Person picks up a dirty plate.", mapped_step="Pick up dirty dishes", confidence=0.85),
            FrameObservation(timestamp=2.0, observation="Person picks up a dirty plate.", mapped_step="Pick up dirty dishes", confidence=0.88), # Duplicate step
            FrameObservation(timestamp=3.0, observation="Person applies soap to sponge.", mapped_step="Apply soap", confidence=0.9),
            FrameObservation(timestamp=4.0, observation="Scrubbing the plate.", mapped_step="Scrub dishes", confidence=0.82),
        ]
        self.idx = 0

    def evaluate_frame(self, image_base64, task_name, steps, timestamp):
        if self.idx < len(self.sequence):
            obs = self.sequence[self.idx]
            self.idx += 1
            return obs
        return FrameObservation(timestamp=timestamp, observation="Nothing", confidence=0.0)

# Patch the engine
import app.main
app.main.engine = MockEngine()

async def run_test():
    print("--- Starting Test Flow ---")
    
    # 1. Register Task
    task_def = TaskDefinition(
        task_name="Wash dishes",
        steps=["Pick up dirty dishes", "Apply soap", "Scrub dishes", "Rinse dishes", "Place dishes to dry"],
        completion_criteria="All steps done"
    )
    state = await register_task(task_def)
    print(f"Task Registered: {state.task_name}, Status: {state.status}")
    assert state.status == "not_started"

    # 2. Simulate Frames
    dummy_img = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" # 1x1 gif
    
    for i in range(5):
        req = EvaluateFrameRequest(
            task_name="Wash dishes",
            image_base64=dummy_img,
            timestamp=float(i)
        )
        state = await evaluate_frame(req)
        print(f"\nTime {i}s:")
        print(f"  Current Activity: {state.current_activity}")
        print(f"  Observed Steps: {state.observed_steps}")
        print(f"  Narrative: {state.what_happened}")
    
    # 3. Final Checks
    print("\n--- Final State ---")
    print(f"Status: {state.status}")
    print(f"Explanation: {state.explanation}")
    
    # Assertions
    assert "Pick up dirty dishes" in state.observed_steps
    assert "Apply soap" in state.observed_steps
    assert len(state.what_happened) >= 3 # Should have entries for start, pick up, apply soap, scrub
    print("\nTest Passed Successfully!")

if __name__ == "__main__":
    asyncio.run(run_test())
