'use client';

import { TaskState } from '@/lib/api';

interface EvaluationPanelProps {
  state: TaskState | null;
}

export default function EvaluationPanel({ state }: EvaluationPanelProps) {
  if (!state) return null;

  // Determine if this is a sequential task
  const isSequential = state.next_expected_step !== undefined;
  const allSteps = [...state.observed_steps, ...state.missing_steps];

  return (
    <div style={{ border: '1px solid #ccc', padding: '10px' }}>
      <h3>3. Live Evaluation</h3>
      
      <div style={{ marginBottom: '10px' }}>
        <strong>Status: </strong> 
        <span style={{ 
          color: state.status === 'completed' ? 'green' : 
                 state.status === 'in_progress' ? 'orange' : 'black' 
        }}>
          {state.status.toUpperCase()}
        </span>
      </div>

      <div style={{ marginBottom: '10px' }}>
        <strong>Current Activity: </strong> {state.current_activity || 'None observed'}
      </div>

      {state.next_expected_step && (
        <div style={{
          marginBottom: '10px',
          padding: '10px',
          background: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px',
          color: '#856404'
        }}>
          <strong>⏭️ Next Expected Step: </strong>
          <span style={{ fontSize: '1.1em', fontWeight: 'bold' }}>
            {state.next_expected_step}
          </span>
        </div>
      )}

      <div style={{ marginBottom: '15px' }}>
        <strong>What Happened (Narrative):</strong>
        <ul style={{ maxHeight: '200px', overflowY: 'auto', background: '#f5f5f5', color: 'black', padding: '10px', listStylePosition: 'inside' }}>
          {state.what_happened.length === 0 && <li>No events yet.</li>}
          {state.what_happened.map((event, i) => (
            <li key={i}>{event}</li>
          ))}
        </ul>
      </div>

      {/* Sequential Progress Tracker */}
      {isSequential && allSteps.length > 0 && (
        <div style={{ marginBottom: '15px', padding: '10px', background: '#f9f9f9', borderRadius: '4px' }}>
          <h4 style={{ marginTop: 0 }}>📋 Sequential Progress</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {allSteps.map((step, index) => {
              const isCompleted = state.observed_steps.includes(step);
              const isCurrent = step === state.next_expected_step;

              return (
                <div
                  key={step}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '8px',
                    background: isCompleted ? '#d4edda' : isCurrent ? '#fff3cd' : '#fff',
                    border: isCurrent ? '2px solid #ffc107' : '1px solid #ddd',
                    borderRadius: '4px',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <span style={{
                    minWidth: '30px',
                    fontWeight: 'bold',
                    color: isCompleted ? '#28a745' : isCurrent ? '#856404' : '#999'
                  }}>
                    {index + 1}.
                  </span>
                  <span style={{
                    flex: 1,
                    fontWeight: isCurrent ? 'bold' : 'normal',
                    color: isCompleted ? '#28a745' : isCurrent ? '#856404' : '#000'
                  }}>
                    {step}
                  </span>
                  <span style={{ fontSize: '1.2em' }}>
                    {isCompleted ? '✅' : isCurrent ? '⏳' : '⏸️'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Non-Sequential Step Lists */}
      {!isSequential && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <h4>✅ Observed Steps</h4>
            <ul>
              {state.observed_steps.map(step => (
                <li key={step} style={{ color: 'green' }}>{step}</li>
              ))}
              {state.observed_steps.length === 0 && <li>None</li>}
            </ul>
          </div>
          <div>
            <h4>⬜ Missing Steps</h4>
            <ul>
              {state.missing_steps.map(step => (
                <li key={step} style={{ color: 'red' }}>{step}</li>
              ))}
              {state.missing_steps.length === 0 && <li>None</li>}
            </ul>
          </div>
        </div>
      )}
      
      {state.explanation && (
        <div style={{ marginTop: '10px', fontStyle: 'italic', borderTop: '1px solid #eee', paddingTop: '5px' }}>
         AI Comment: "{state.explanation}"
        </div>
      )}
    </div>
  );
}
