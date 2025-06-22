import React, { memo, useEffect, useState } from 'react';
import { Handle, Position } from 'reactflow';
import { MarkovNode } from './types';

// The props received by a custom node are the 'data' property of the node object.
interface AnimatedNodeProps {
  data: {
    label: string;
    timestamp: number;
    details?: string;
    mcp_server?: string;
    mcp_server_img_url?: string;
    value?: number;
  };
  isConnectable: boolean;
  id: string; // React Flow also passes id here
}

export const AnimatedNode: React.FC<AnimatedNodeProps> = memo(({ data, isConnectable, id }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [scale, setScale] = useState(0);

  useEffect(() => {
    // Trigger animation after a short delay
    const timer = setTimeout(() => {
      setIsVisible(true);
      setScale(1);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div
      className="relative"
      style={{
        opacity: isVisible ? 1 : 0,
        transform: `scale(${scale})`,
        transition: 'opacity 0.5s ease-in-out, transform 0.5s ease-out',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-blue-400 border-2 border-white"
        style={{ opacity: 0.9 }}
      />
      <div className="flex flex-col items-center justify-center w-[140px] h-[140px] bg-white/95 backdrop-blur-sm border-2 border-blue-400/60 rounded-full shadow-lg">
        {data.mcp_server_img_url && (
          <img 
            src={data.mcp_server_img_url} 
            alt={data.mcp_server || 'Server Image'}
            className="w-15 h-15 rounded-full mb-2 object-cover"
          />
        )}
        <div className="text-base font-semibold text-gray-800 truncate max-w-[100px]">{data.label}</div>
        <div className="text-xs text-gray-500 mt-1">
          {new Date(data.timestamp).toLocaleTimeString()}
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-green-400 border-2 border-white"
        style={{ opacity: 0.9 }}
        id={id}
      />
    </div>
  );
});

AnimatedNode.displayName = 'AnimatedNode'; 