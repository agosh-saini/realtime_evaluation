'use client';

import { useState, useCallback } from 'react';
import TaskForm from '@/components/TaskForm';
import VideoCapture from '@/components/VideoCapture';
import EvaluationPanel from '@/components/EvaluationPanel';
import { registerTask, evaluateFrame, TaskDefinition, TaskState } from '@/lib/api';

export default function Home() {
  const [taskState, setTaskState] = useState<TaskState | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [taskName, setTaskName] = useState<string>('');

  const handleStartTask = async (def: TaskDefinition) => {
    try {
      // 1. Register
      const initialState = await registerTask(def);
      setTaskState(initialState);
      setTaskName(def.task_name);
      
      // 2. Start Recording
      setIsRecording(true);
    } catch (err) {
      alert(`Error starting task: ${err}`);
    }
  };

  const handleFrameCapture = useCallback(async (base64: string) => {
    if (!taskName) return;

    try {
      const timestamp = Date.now() / 1000;
      const newState = await evaluateFrame({
        task_name: taskName,
        image_base64: base64,
        timestamp
      });
      setTaskState(newState);

      // Stop if complete (optional)
      if (newState.status === 'completed' || newState.status === 'failed') {
        setIsRecording(false);
      }
    } catch (err) {
      console.error("Frame evaluation failed", err);
    }
  }, [taskName]);

  return (
    <main style={{ maxWidth: '900px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Video Task Evaluator</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div>
          <TaskForm onStart={handleStartTask} disabled={isRecording} />
          <EvaluationPanel state={taskState} />
        </div>
        
        <div>
          <h3>2. Monitoring</h3>
          <VideoCapture 
            isRecording={isRecording} 
            onFrameCapture={handleFrameCapture} 
          />
          {isRecording && <div style={{ color: 'red', fontWeight: 'bold' }}>🔴 LIVE - Analyzing...</div>}
        </div>
      </div>
    </main>
  );
}
