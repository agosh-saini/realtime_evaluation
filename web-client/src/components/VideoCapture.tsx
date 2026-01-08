'use client';

import { useRef, useEffect } from 'react';

interface VideoCaptureProps {
  onFrameCapture: (base64: string) => void;
  isRecording: boolean;
}

export default function VideoCapture({ onFrameCapture, isRecording }: VideoCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Initialize Camera
  useEffect(() => {
    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing camera:", err);
      }
    }
    setupCamera();
  }, []);

  // Frame Capture Loop
  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (isRecording) {
      intervalId = setInterval(() => {
        if (videoRef.current && canvasRef.current) {
          const video = videoRef.current;
          const canvas = canvasRef.current;
          
          // Set canvas dimensions
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          
          // Draw frame
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Convert to base64 (jpeg for speed)
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
            // Remove prefix "data:image/jpeg;base64,"
            const base64 = dataUrl.split(',')[1];
            onFrameCapture(base64);
          }
        }
      }, 1000); // 1 frame per second
    }

    return () => clearInterval(intervalId);
  }, [isRecording, onFrameCapture]);

  return (
    <div style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '20px' }}>
      <h3>Live Feed</h3>
      {/* Hidden canvas for processing */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <video 
        ref={videoRef} 
        autoPlay 
        muted 
        playsInline 
        style={{ width: '100%', maxWidth: '640px', background: '#000' }}
      />
    </div>
  );
}
