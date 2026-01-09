export interface TaskDefinition {
  task_name: string;
  steps: string[];
  sequential: boolean;
}

export interface TaskState {
  task_name: string;
  status: 'idle' | 'in_progress' | 'completed' | 'failed';
  current_activity?: string;
  next_expected_step?: string;
  observed_steps: string[];
  missing_steps: string[];
  what_happened: string[];
  explanation?: string;
}

export interface EvaluateFrameRequest {
  task_name: string;
  image_base64: string;
  timestamp: number;
}

const API_BASE_URL = 'http://localhost:8000';

export async function registerTask(def: TaskDefinition): Promise<TaskState> {
  const res = await fetch(`${API_BASE_URL}/task/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(def),
  });
  if (!res.ok) throw new Error('Failed to register task');
  return res.json();
}

export async function evaluateFrame(req: EvaluateFrameRequest): Promise<TaskState> {
  const res = await fetch(`${API_BASE_URL}/frame/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error('Failed to evaluate frame');
  return res.json();
}
