'use client';

import { useState } from 'react';
import { TaskDefinition } from '@/lib/api';

interface TaskFormProps {
  onStart: (def: TaskDefinition) => void;
  disabled: boolean;
}

export default function TaskForm({ onStart, disabled }: TaskFormProps) {
  const [taskName, setTaskName] = useState('My Task');
  const [steps, setSteps] = useState('Wave\nPoint\nThumbsUp');
  const [criteria, setCriteria] = useState('All steps completed');
  const [sequential, setSequential] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const stepsList = steps.split('\n').filter(s => s.trim() !== '');
    onStart({
      task_name: taskName,
      steps: stepsList,
      completion_criteria: criteria,
      sequential: sequential,
    });
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px', padding: '10px', border: '1px solid #ccc' }}>
      <h3>1. Define Task</h3>
      
      <label>
        Task Name:
        <input 
          type="text" 
          value={taskName} 
          onChange={e => setTaskName(e.target.value)}
          disabled={disabled}
          style={{ width: '100%', padding: '5px', marginTop: '5px' }}
        />
      </label>

      <label>
        Steps (one per line):
        <textarea 
          value={steps} 
          onChange={e => setSteps(e.target.value)}
          disabled={disabled}
          rows={5}
          style={{ width: '100%', padding: '5px', marginTop: '5px' }}
        />
      </label>

      <label>
        Completion Criteria:
        <input
          type="text"
          value={criteria}
          onChange={e => setCriteria(e.target.value)}
          disabled={disabled}
          style={{ width: '100%', padding: '5px', marginTop: '5px' }}
        />
      </label>

      <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
        <input
          type="checkbox"
          checked={sequential}
          onChange={e => setSequential(e.target.checked)}
          disabled={disabled}
          style={{ cursor: disabled ? 'not-allowed' : 'pointer' }}
        />
        <span style={{ fontWeight: 'bold', color: sequential ? '#0070f3' : 'inherit' }}>
          Sequential Mode
        </span>
        <span style={{ fontSize: '0.85em', color: '#666' }}>
          (Steps must be completed in order)
        </span>
      </label>

      <button
        type="submit"
        disabled={disabled}
        style={{ padding: '10px', background: disabled ? '#ccc' : '#0070f3', color: 'white', border: 'none', cursor: disabled ? 'not-allowed' : 'pointer' }}
      >
        {disabled ? 'Task Running...' : 'Start Task Evaluation'}
      </button>
    </form>
  );
}
