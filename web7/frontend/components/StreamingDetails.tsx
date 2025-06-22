"use client";

import { useState, useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';

interface StreamingDetailsProps {
  stepHistory: string[];
  isPolling: boolean;
}

export default function StreamingDetails({ stepHistory, isPolling }: StreamingDetailsProps) {
  const [displayedText, setDisplayedText] = useState("");
  const [isFullyStreamed, setIsFullyStreamed] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const streamingIndex = useRef({ step: 0, char: 0 });

  useEffect(() => {
    // Reset component state when the step history is cleared (e.g., on a new agent run)
    if (stepHistory.length === 0) {
      setDisplayedText('');
      streamingIndex.current = { step: 0, char: 0 };
      setIsFullyStreamed(false);
      return;
    }

    const intervalId = setInterval(() => {
      let { step, char } = streamingIndex.current;

      // Check if we are done with all steps
      if (step >= stepHistory.length) {
        setIsFullyStreamed(true);
        clearInterval(intervalId);
        return;
      }
      
      setIsFullyStreamed(false);
      const currentStepDetails = stepHistory[step];

      // At the start of a new step's content, add the separator
      if (char === 0) {
        setDisplayedText(prev => {
          if (step > 0) {
            return prev + `\n\n--------\n\n`;
          }
          return prev; // The first step doesn't get a separator before it.
        });
      }

      // Stream the characters of the current step
      if (currentStepDetails && char < currentStepDetails.length) {
        setDisplayedText(prev => prev + currentStepDetails[char]);
        streamingIndex.current.char++;
      } else {
        // Move to the next step
        streamingIndex.current.step++;
        streamingIndex.current.char = 0;
      }
    }, 20); // Adjust speed of streaming

    return () => clearInterval(intervalId);
  }, [stepHistory]);

  useEffect(() => {
    // Auto-scroll to the bottom
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [displayedText]);

  if (stepHistory.length === 0 && !displayedText) {
    return null;
  }

  const isStreaming = !isFullyStreamed || (stepHistory.length > 0 && isPolling);

  return (
    <div className="h-full flex flex-col border-t border-gray-200">
      {/* Header */}
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center">
          <Terminal className="w-5 h-5 text-gray-500 mr-2" />
          <h2 className="text-lg font-bold text-gray-800">Details</h2>
        </div>
      </div>

      {/* Content */}
      <div ref={containerRef} className="flex-1 p-4 bg-white overflow-y-auto text-sm text-gray-700 font-mono">
        <pre className="whitespace-pre-wrap break-words">
          {displayedText}
          {isStreaming && <span className="inline-block w-2 h-4 bg-gray-600 animate-pulse ml-1" />}
        </pre>
      </div>
    </div>
  );
} 