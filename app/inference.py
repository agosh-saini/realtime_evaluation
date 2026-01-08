import base64
import io
import json
import logging
import traceback
import tempfile
import os
from PIL import Image
from typing import Optional, List

# Try to import MLX VLM. If not available, we might need to fallback or error.
try:
    from mlx_vlm import load, generate
    from mlx_vlm.prompt_utils import apply_chat_template
    from mlx_vlm.utils import load_config
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    logging.warning("mlx_vlm not found. Inference will return mock data.")

from app.models import FrameObservation
from app.prompts import EVALUATION_SYSTEM_PROMPT

# Default model
MODEL_PATH = "mlx-community/Qwen2-VL-2B-Instruct-4bit"

class InferenceEngine:
    def __init__(self):
        self.model = None
        self.processor = None
        self.config = None
        self.is_loaded = False

    def load_model(self):
        if not MLX_AVAILABLE:
            return

        print(f"Loading model: {MODEL_PATH}...")
        try:
            self.model, self.processor = load(MODEL_PATH)
            self.config = load_config(MODEL_PATH)  # Load config once!
            self.is_loaded = True
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            traceback.print_exc()
            raise e
    def evaluate_frame(self, image_base64: str, task_name: str, steps: List[str], timestamp: float, next_expected_step: Optional[str] = None, sequential: bool = False) -> FrameObservation:
        # Mock mode if MLX not present
        if not self.is_loaded:
            if not MLX_AVAILABLE:
                return self._mock_inference(task_name, steps, timestamp)
            else:
                try:
                    self.load_model()
                except Exception as e:
                   return FrameObservation(
                        timestamp=timestamp,
                        observation=f"Model loading failed: {e}",
                        mapped_step=None,
                        confidence=0.0
                    )
        
        # Decode image
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception as e:
            logging.error(f"Image decode failed: {e}")
            raise ValueError("Invalid image data")

        # Save image to temporary file (mlx_vlm.generate expects a file path)
        temp_image_path = None
        try:
            # Create temporary file
            temp_fd, temp_image_path = tempfile.mkstemp(suffix='.jpg')
            os.close(temp_fd)  # Close the file descriptor
            image.save(temp_image_path, 'JPEG')
        except Exception as e:
            logging.error(f"Failed to save temporary image: {e}")
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
            raise ValueError("Failed to prepare image for inference")

        # Prepare Prompt
        steps_str = ", ".join(steps)

        # Add sequential context if applicable
        if sequential and next_expected_step:
            sequential_hint = f"\n\n**IMPORTANT**: This is a SEQUENTIAL task. The next expected step is: '{next_expected_step}'. Pay special attention to detecting this specific action."
            prompt_text = EVALUATION_SYSTEM_PROMPT.format(task_name=task_name, steps_str=steps_str) + sequential_hint
        else:
            prompt_text = EVALUATION_SYSTEM_PROMPT.format(task_name=task_name, steps_str=steps_str)

        # Use chat template format for better results (using cached config)
        formatted_prompt = apply_chat_template(
            self.processor,
            self.config,
            prompt_text,
            num_images=1
        )

        try:
            # Use keyword arguments to ensure correct mapping
            output = generate(
                model=self.model,
                processor=self.processor,
                image=temp_image_path,
                prompt=formatted_prompt,
                max_tokens=300,
                verbose=False
            )
            
            # Handle GenerationResult object from newer mlx-vlm
            if not isinstance(output, str):
                # Try to extract text from common attributes or convert to string
                if hasattr(output, 'text'):
                    output = output.text
                elif hasattr(output, 'generation'):
                    output = output.generation
                else:
                    print(f"Unknown output type: {type(output)}, attributes: {dir(output)}")
                    output = str(output)

            # Remove markdown code blocks if present
            clean_output = output.replace("```json", "").replace("```", "").strip()

            # Robust JSON extraction: Find first '{' and last '}'
            start_idx = clean_output.find('{')
            end_idx = clean_output.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                clean_output = clean_output[start_idx:end_idx+1]
            else:
                logging.warning(f"No JSON object found in output: {clean_output}")

            # --- DEBUG LOGGING (PRINT) ---
            print(f"\n\n==================== RAW MODEL OUTPUT ====================\n{output}\n==========================================================\n")
            # ---------------------

            data = json.loads(clean_output)

            # Normalize and match the mapped_step to an actual step from the list
            mapped_step_raw = data.get("mapped_step")
            matched_step = None

            if mapped_step_raw and mapped_step_raw != "null":
                # Normalize for comparison
                def normalize(s: str) -> str:
                    return s.lower().strip().replace(" ", "").replace("_", "")

                normalized_mapped = normalize(mapped_step_raw)

                # Find best match from the steps list
                for step in steps:
                    if normalize(step) == normalized_mapped:
                        matched_step = step
                        logging.info(f"✓ Matched '{mapped_step_raw}' to '{step}'")
                        break

                if not matched_step:
                    logging.warning(f"⚠ Could not match '{mapped_step_raw}' to any step in {steps}")

            # --- DEBUG LOGGING (PRINT) ---
            print(f"Parsed Observation: {data.get('observation')} | Mapped: {mapped_step_raw} -> {matched_step} | Conf: {data.get('confidence')}\n")
            # ---------------------

            result = FrameObservation(
                timestamp=timestamp,
                observation=data.get("observation", "No observation"),
                mapped_step=matched_step,
                confidence=float(data.get("confidence", 0.0))
            )

            # Cleanup temporary file
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)

            return result

        except Exception as e:
            logging.error(f"Inference failed: {e}")

            # Cleanup temporary file
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)

            # Fallback for stability
            return FrameObservation(
                timestamp=timestamp,
                observation="Error processing frame",
                confidence=0.0
            )

    def _mock_inference(self, task_name: str, steps: List[str], timestamp: float) -> FrameObservation:
        # Return a neutral, "no activity" observation to prevent false positives
        return FrameObservation(
            timestamp=timestamp,
            observation="Model not loaded. No activity detected.",
            mapped_step=None,
            confidence=0.0
        )

engine = InferenceEngine()
