EVALUATION_SYSTEM_PROMPT = """
Analyze this image and describe what you see in detail.

Task: {task_name}
Expected Steps: {steps_str}

Look at the image carefully and answer:
1. What is the person doing? Describe their body position, hand gestures, and movements.
2. What objects are visible in the frame?
3. Does the person's action match any of the expected steps? Be specific.

DETECTION GUIDELINES:
- If the person is waving their hand (moving it side to side), map to "Wave"
- If the person is pointing with their finger, map to "Point"
- If the person is showing a thumbs up gesture, map to "ThumbsUp" or "Thumbs Up"
- If the person is clapping their hands together, map to "Clap"
- Be confident in your detections - if you see a gesture, identify it clearly

CRITICAL MATCHING RULES:
- The mapped_step MUST be one of these exact names: {steps_str}
- Match the capitalization and spacing from the list above
- If unsure which exact name to use, pick the closest match from the list
- Do NOT make up new step names - only use names from the Expected Steps list

If you see a clear gesture or action that matches a step, identify it and map it to the exact step name from the list.
If you see activity but it doesn't match any step, describe what you see but set mapped_step to null.
Only set mapped_step to null if there is truly no clear gesture or the gesture doesn't match any step.

Output your response as valid JSON in this exact format:
{{
  "observation": "detailed description of what is happening in the image",
  "mapped_step": "exact step name from the Expected Steps list above, or null if no match",
  "confidence": 0.95
}}
"""
