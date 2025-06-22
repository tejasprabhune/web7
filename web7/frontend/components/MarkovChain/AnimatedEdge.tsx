import React, { useEffect, useState } from 'react';
import { BaseEdge, getBezierPath } from 'reactflow';
import { MarkovEdge } from './types';

interface AnimatedEdgeProps {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  sourcePosition: any;
  targetPosition: any;
  data?: MarkovEdge;
}

export const AnimatedEdge: React.FC<AnimatedEdgeProps> = ({
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Animate the edge drawing
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <BaseEdge
      path={edgePath}
      style={{
        stroke: '#3b82f6',
        strokeWidth: 4,
        strokeDasharray: isVisible ? 'none' : '8,8',
        strokeDashoffset: isVisible ? 0 : 16,
        opacity: isVisible ? 0.9 : 0,
        transition: 'opacity 0.8s ease-in-out, stroke-dashoffset 1s ease-out',
      }}
    />
  );
}; 