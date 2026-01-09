# Web Client: Real-Time Evaluator

Next.js frontend for capturing video and displaying real-time task evaluation feedback.

## Features

*   **Task Registration:** Define custom tasks with specific steps via the UI.
*   **Live Capture:** Captures video from webcam at ~0.5 FPS (optimized for local inference).
*   **Real-time Feedback:** Displays current progress, latched steps, and AI observations.
*   **Sequential Tracking:** Visual indicator for current step vs completed steps.

## Setup

1.  Install dependencies:
    ```bash
    npm install
    ```

2.  Run development server:
    ```bash
    npm run dev
    ```

3.  Access at [http://localhost:3000](http://localhost:3000).

## Configuration

The client connects to the backend at `http://localhost:8000` by default. This is configured in `src/lib/api.ts`.
