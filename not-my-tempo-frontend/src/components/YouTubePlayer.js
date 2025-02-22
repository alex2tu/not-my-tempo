import { useEffect, useRef } from 'react';

export default function YouTubePlayer({ videoId }) {
  const playerRef = useRef(null);

  useEffect(() => {
    // Load the YouTube IFrame Player API
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // Initialize player when API is ready
    window.onYouTubeIframeAPIReady = () => {
      playerRef.current = new window.YT.Player('youtube-player', {
        height: '100%',
        width: '100%',
        videoId: videoId,
        playerVars: {
          autoplay: 0,
          controls: 1,
          modestbranding: 1,
        },
        events: {
          onReady: onPlayerReady,
          onStateChange: onPlayerStateChange,
        },
      });
    };

    return () => {
      // Cleanup
      if (playerRef.current) {
        playerRef.current.destroy();
      }
    };
  }, [videoId]);

  const onPlayerReady = (event) => {
    // Player is ready
    console.log('Player ready');
  };

  const onPlayerStateChange = (event) => {
    // Handle player state changes
    console.log('Player state changed:', event.data);
  };

  // Methods to control the player
  const playVideo = () => {
    playerRef.current?.playVideo();
  };

  const pauseVideo = () => {
    playerRef.current?.pauseVideo();
  };

  const stopVideo = () => {
    playerRef.current?.stopVideo();
  };

  return (
    <div className="w-full h-full relative">
      <div id="youtube-player" className="absolute inset-0" />
    </div>
  );
} 