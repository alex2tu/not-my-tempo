import { useEffect, useRef } from 'react';

export default function WebcamFeed({ isDetecting, onGestureDetected }) {
  const videoRef = useRef(null);

  useEffect(() => {
    let stream = null;

    const startWebcam = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: 640,
            height: 480
          } 
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing webcam:", err);
      }
    };

    startWebcam();

    // Cleanup function
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  useEffect(() => {
    if (isDetecting) {
      // Here we would initialize OpenCV.js and start gesture detection
      // For now, we'll just simulate gesture detection
      const interval = setInterval(() => {
        onGestureDetected('Play');
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [isDetecting, onGestureDetected]);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      className="w-full h-full object-cover rounded-lg"
    />
  );
} 