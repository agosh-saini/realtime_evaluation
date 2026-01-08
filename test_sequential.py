"""
Example: How to register and test a sequential task

This demonstrates the difference between sequential and non-sequential tasks:
- Sequential: Steps must be completed in order (e.g., "Wave", then "Point", then "Thumbs Up")
- Non-sequential: Steps can be completed in any order
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Example 1: Sequential Task
sequential_task = {
    "task_name": "Greeting Sequence",
    "steps": ["Wave", "Point", "Thumbs Up"],
    "completion_criteria": "All three gestures performed in order",
    "sequential": True  # This makes it sequential!
}

# Example 2: Non-Sequential Task (default)
non_sequential_task = {
    "task_name": "Random Gestures",
    "steps": ["Wave", "Point", "Thumbs Up"],
    "completion_criteria": "All three gestures performed in any order",
    "sequential": False
}

def register_task(task_def):
    """Register a task with the server"""
    response = requests.post(f"{BASE_URL}/task/register", json=task_def)
    print(f"\nRegistered Task: {task_def['task_name']}")
    print(f"Sequential: {task_def.get('sequential', False)}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def get_status(task_name):
    """Get current task status"""
    response = requests.get(f"{BASE_URL}/task/status", params={"task_name": task_name})
    return response.json()

if __name__ == "__main__":
    print("=" * 60)
    print("Sequential Task Management Demo")
    print("=" * 60)

    # Register a sequential task
    print("\n1. Registering SEQUENTIAL task...")
    state = register_task(sequential_task)
    print(f"   Next Expected Step: {state.get('next_expected_step')}")

    # Register a non-sequential task
    print("\n2. Registering NON-SEQUENTIAL task...")
    register_task(non_sequential_task)

    print("\n" + "=" * 60)
    print("Now when you send frames:")
    print("  - Sequential task will only accept 'Wave' first")
    print("  - After 'Wave', it will only accept 'Point'")
    print("  - After 'Point', it will accept 'Thumbs Up'")
    print("  - Non-sequential task accepts any step at any time")
    print("=" * 60)
