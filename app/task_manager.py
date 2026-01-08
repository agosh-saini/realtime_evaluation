from typing import Dict, List, Optional
import logging
from app.models import TaskDefinition, TaskState, FrameObservation, TaskStatus

class TaskManager:
    def __init__(self):
        self.task_registry: Dict[str, TaskDefinition] = {}
        self.active_sessions: Dict[str, TaskState] = {}
        # Keep track of detailed history for logic that doesn't fit into the summary state
        self.session_history: Dict[str, List[FrameObservation]] = {}

    def register_task(self, task_def: TaskDefinition):
        self.task_registry[task_def.task_name] = task_def
        # Initialize empty state
        self.reset_session(task_def.task_name)

    def reset_session(self, task_name: str):
        if task_name in self.task_registry:
            task_def = self.task_registry[task_name]
            next_step = task_def.steps[0] if task_def.sequential and task_def.steps else None
            self.active_sessions[task_name] = TaskState(
                task_name=task_name,
                status=TaskStatus.NOT_STARTED,
                what_happened=[],
                observed_steps=[],
                missing_steps=task_def.steps.copy(),
                confidence=0.0,
                next_expected_step=next_step
            )
            self.session_history[task_name] = []

    def get_task_state(self, task_name: str) -> Optional[TaskState]:
        return self.active_sessions.get(task_name)

    def update_with_observation(self, task_name: str, observation: FrameObservation) -> TaskState:
        if task_name not in self.active_sessions:
            raise ValueError(f"Task {task_name} not registered or initialized.")
        
        state = self.active_sessions[task_name]
        task_def = self.task_registry[task_name]
        history = self.session_history[task_name]

        # 1. Update basic fields
        state.current_activity = observation.observation
        state.confidence = observation.confidence # Simple latest confidence for now

        # Update status to in_progress if not already
        if state.status == TaskStatus.NOT_STARTED:
            state.status = TaskStatus.IN_PROGRESS

        # 2. Step Mapping Logic
        # Normalize step names for matching (case-insensitive, strip whitespace)
        def normalize_step(step: str) -> str:
            return step.lower().strip().replace(" ", "").replace("_", "")

        normalized_steps = {normalize_step(s): s for s in task_def.steps}
        observed_step_name = None

        if observation.mapped_step:
            normalized_mapped = normalize_step(observation.mapped_step)
            # Try to find a match
            if normalized_mapped in normalized_steps:
                observed_step_name = normalized_steps[normalized_mapped]

            # Log for debugging
            logging.info(f"Mapped step: '{observation.mapped_step}' -> Normalized: '{normalized_mapped}' -> Matched: {observed_step_name}")
            logging.info(f"Available steps: {task_def.steps}")
            logging.info(f"Next expected: {state.next_expected_step}")

        if observed_step_name and observed_step_name not in state.observed_steps:
            # New step observed!

            # For sequential tasks, check if this is the expected next step
            if task_def.sequential:
                # Use normalized comparison for next expected step
                if state.next_expected_step and normalize_step(observed_step_name) == normalize_step(state.next_expected_step):
                    # Correct sequential step!
                    logging.info(f"✓ Sequential step matched! Adding '{observed_step_name}'")
                    state.observed_steps.append(observed_step_name)
                    if observed_step_name in state.missing_steps:
                        state.missing_steps.remove(observed_step_name)

                    # Update next expected step
                    current_index = task_def.steps.index(observed_step_name)
                    if current_index + 1 < len(task_def.steps):
                        state.next_expected_step = task_def.steps[current_index + 1]
                        logging.info(f"Next expected step updated to: '{state.next_expected_step}'")
                    else:
                        state.next_expected_step = None  # All steps done
                        logging.info("All steps completed!")
                else:
                    # Out of order step detected - mark as warning
                    expected_idx = task_def.steps.index(state.next_expected_step) if state.next_expected_step else -1
                    observed_idx = task_def.steps.index(observed_step_name)
                    state.explanation = f"Warning: Step '{observed_step_name}' detected, but expecting '{state.next_expected_step}' (step {expected_idx + 1})"
                    logging.warning(state.explanation)
            else:
                # Non-sequential task - any step is fine
                logging.info(f"✓ Non-sequential step matched! Adding '{observed_step_name}'")
                state.observed_steps.append(observed_step_name)
                if observed_step_name in state.missing_steps:
                    state.missing_steps.remove(observed_step_name)
        
        # 3. "What Happened" Narrative Logic (Deduplication)
        should_add_to_narrative = False
        
        if not history:
             should_add_to_narrative = True
        else:
            last_obs = history[-1]
            # Simple heuristic: if the observation is significantly different or a new step is detected
            # For now, we rely on mapped_step change OR semantic difference (todo)
            # here we just check if the mapped description allows us to add a new narrative entry.
            
            # If the step changed, definitely add it
            if observation.mapped_step != last_obs.mapped_step:
                should_add_to_narrative = True
            
            # If step is same, but observation text is very different? 
            # (Skipping for now to avoid spam, assuming step-level granularity is king)

        if should_add_to_narrative:
            # Construct a natural language sentence
            # Ideally this comes from the LLM, but we can construct it or just use the observation
            narrative_entry = f"At {observation.timestamp}s: {observation.observation}"
            state.what_happened.append(narrative_entry)

        # 4. Completion Check
        # Strict: all steps observed
        if not state.missing_steps:
            state.status = TaskStatus.COMPLETED
            if task_def.sequential:
                state.explanation = "All steps completed in correct order."
            else:
                state.explanation = "All steps have been observed."
        else:
            if task_def.sequential and state.next_expected_step:
                state.explanation = f"Sequential task: waiting for step '{state.next_expected_step}' ({len(state.observed_steps)}/{len(task_def.steps)} completed)"
            else:
                state.explanation = f"Observed {len(state.observed_steps)}/{len(task_def.steps)} steps. Missing: {', '.join(state.missing_steps)}"

        # Save history
        history.append(observation)
        self.active_sessions[task_name] = state
        
        return state

# Global instance
manager = TaskManager()
