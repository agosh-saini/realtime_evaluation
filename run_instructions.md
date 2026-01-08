# Local Video Task Evaluation System

## Prerequisites
- macOS with Apple Silicon (M1/M2/M3)
- Python 3.11+
- Node.js 18+

## 1. Backend Setup

The backend handles the core logic, state management, and MLX inference.

1. **Navigate to project root**:
   ```bash
   cd /Users/agoshsaini/Documents/Projects/real_time_local
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: This installs `fastapi`, `uvicorn`, `pillow`, and the `mlx` libraries.*

4. **Start the Backend Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The backend will be running at `http://localhost:8000`.

## 2. Frontend Setup

The frontend is a Next.js web application for video capture and live feedback.

1. **Navigate to the web client directory**:
   OPEN A NEW TERMINAL TAB.
   ```bash
   cd web-client
   ```

2. **Install Node Dependencies**:
   ```bash
   npm install
   ```

3. **Start the Frontend Development Server**:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`.

## 3. Usage Guide

1. Open your browser to **[http://localhost:3000](http://localhost:3000)**.
2. Grant **Camera Permissions** when prompted.
3. **Define Your Task**:
   - Enter a **Task Name** (e.g., "Wash Dishes").
   - Define **Steps** (one per line).
   - *Tip: Specific steps help the AI map observations accurately.*
4. Click **"Start Task Evaluation"**.
5. Perform the task in view of the camera.
6. Watch the **Live Evaluation** panel:
   - **Status**: Updates from "In Progress" to "Completed".
   - **What Happened**: A real-time chronological narrative of your actions.
   - **Observed Steps**: Green checkmarks as you complete steps.

## Troubleshooting

- **Backend Error: `ModuleNotFoundError`**: Ensure you activated the virtual environment (`source venv/bin/activate`) before running `uvicorn`.
- **Camera Not Working**: Check browser permissions or try a different browser.
- **Inference is Slow**: MLX should run efficiently on Apple Silicon. If it's very slow, ensure you are not running other GPU-intensive tasks.
