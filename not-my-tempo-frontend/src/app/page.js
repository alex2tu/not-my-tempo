'use client';

import { useState } from 'react';
import YouTubePlayer from '../components/YouTubePlayer';
import WebcamFeed from '../components/WebcamFeed';
import InfoButton from '@/components/InfoButton';

export default function Home() {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectedGesture, setDetectedGesture] = useState('Play');

  const extractVideoId = (url) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const extracted = extractVideoId(youtubeUrl);
    if (extracted) {
      setVideoId(extracted);
    } else {
      alert('Please enter a valid YouTube URL');
    }
  };

  const handleGestureDetected = (gesture) => {
    setDetectedGesture(gesture);
  };

  const toggleDetection = () => {
    setIsDetecting(!isDetecting);
  };

  return (
    <div className="min-h-screen p-8">
      {/* Title */}
      <h1 className="text-4xl font-bold text-center mb-8">Not My Tempo</h1>

      {/* Search Bar */}
      <div className="max-w-4xl mx-auto mb-8">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            placeholder="Enter YouTube URL or Video ID"
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-black"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800"
          >
            Search
          </button>
        </form>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto flex gap-8">
        {/* Video Player */}
        <div className="flex-1 aspect-video bg-black rounded-lg overflow-hidden">
          {videoId && <YouTubePlayer videoId={videoId} />}
        </div>

        {/* Webcam Feed */}
        <div className="w-80 flex flex-col gap-4">
          <div className="aspect-video bg-black rounded-lg overflow-hidden">
            <WebcamFeed
              isDetecting={isDetecting}
              onGestureDetected={handleGestureDetected}
            />
          </div>
          <button
            onClick={toggleDetection}
            className={`w-full py-2 rounded-lg ${
              isDetecting
                ? 'bg-red-500 hover:bg-red-600'
                : 'bg-black hover:bg-gray-800'
            } text-white`}
          >
            {isDetecting ? 'Stop Detection' : 'Start Detection'}
          </button>
          <div className="text-center">
            <p>Detected</p>
            <p>Gesture: <span className="font-bold">{detectedGesture}</span></p>
          </div>
          <InfoButton />
        </div>
      </div>
    </div>
  );
}
