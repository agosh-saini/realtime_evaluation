# Real-Time Human Task Evaluation (Local/VLM)

**A local system for evaluating human tasks in real-time on Apple Silicon using Multi-modal LLMs (VLM).**

This system observes video frames from a web client, processes them through a local VLM (Vision-Language Model) to generate a textual description, and then maps those observations to a predefined list of task steps (using the same VLM/LLM).

## Architecture

*   **Frontend:** Next.js (React) application. Captures video, allows User to define tasks (steps), and displays real-time feedback.
*   **Backend:** FastAPI server.
    *   **Inference Engine:** Uses `mlx_vlm` to run Quantized Qwen2-VL-2B locally on Mac (M-series chips).
    *   **Task Logic:** A Python based state machine (`TaskManager`) that tracks observed steps, enforces sequential order (optional), and determines task completion.

### Key Features
*   **Local Inference:** Runs entirely on your Mac. No data leaves your machine.
*   **Real-time(?):** ~0.5 - 1 FPS depending on model/hardware (optimized for Apple Silicon).
*   **Dynamic Tasks:** You define the steps in the UI (e.g. "Prepare Coffee", "Assemble Setup").
*   **Narrative Generation:** Keeps a log of "What Happened" based on visual observations.

## Quick Start

### 1. Backend Setup (FastAPI + MLX)
**Prerequisites:** Mac with Apple Silicon (M1/M2/M3), Python 3.10+, 16GB+ RAM recommended.

1.  Navigate to project root:
    ```bash
    cd real_time_local
    ```
2.  Create virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure key libs are installed: `mlx`, `mlx_vlm`, `fastapi`, `uvicorn`, `pillow`)*

4.  Run the server:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *First run will download the ~2GB model from Hugging Face.*

### 2. Frontend Setup (Next.js)

1.  Navigate to web-client:
    ```bash
    cd web-client
    ```
2.  Install packages:
    ```bash
    npm install
    ```
3.  Run the dev server:
    ```bash
    npm run dev
    ```
4.  Open [http://localhost:3000](http://localhost:3000)

## Usage

1.  **Define Task:** Enter a Task Name (e.g. "Pour Water") and Steps (e.g. "Pick up glass", "Fill glass from pitcher", "Place glass down").
2.  **Start:** Click "Start Task Monitoring".
3.  **Perform:** Perform the actions in front of the camera.
4.  **Observe:** Watch the "Live Evaluation" panel update as steps are detected.

## Note on "Sequential" Mode
In the UI, if "Sequential" is checked, the system will warn/fail if steps are done out of order. If unchecked, steps can be done in any order.

## License
MIT
