import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ReactFlow, {
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  useReactFlow,
  Viewport,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { AnimatedNode } from './AnimatedNode';
import { AnimatedEdge } from './AnimatedEdge';
import { MarkovNode, MarkovEdge } from './types';
import { calculateNodePosition, getTimeRange, calculateViewportForLastNodes, shiftNodesUp } from './utils';

// Define node and edge types outside the component to prevent re-creation on render
const nodeTypes = {
  animatedNode: AnimatedNode,
};

const edgeTypes = {
  animatedEdge: AnimatedEdge,
};

interface MarkovChainFlowProps {
  nodes: MarkovNode[];
  edges: MarkovEdge[];
  onNodeClick?: (node: MarkovNode) => void;
  className?: string;
}

export const MarkovChainFlow: React.FC<MarkovChainFlowProps> = ({
  nodes,
  edges,
  onNodeClick,
  className = '',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [reactFlowNodes, setReactFlowNodes, onNodesChange] = useNodesState([]);
  const [reactFlowEdges, setReactFlowEdges, onEdgesChange] = useEdgesState([]);
  const { setViewport } = useReactFlow();

  // Convert Markov nodes to React Flow nodes with stable positioning
  const convertToReactFlowNodes = useCallback((markovNodes: MarkovNode[]) => {
    if (!containerRef.current) return [];
    
    const containerRect = containerRef.current.getBoundingClientRect();
    if (containerRect.width === 0 || containerRect.height === 0) {
      // Don't try to calculate positions if the container has no size
      return [];
    }
    
    const timeRange = getTimeRange(markovNodes);
    
    return markovNodes.map((markovNode, index) => {
      // Use existing position if available, otherwise calculate new one
      let position;
      if (markovNode.x !== undefined && markovNode.y !== undefined) {
        position = { x: markovNode.x, y: markovNode.y };
      } else {
        // Find parent node (the previous node in the sequence)
        const parentNode = index > 0 ? markovNodes[index - 1] : undefined;
        
        position = calculateNodePosition(
          markovNode,
          containerRect.width,
          containerRect.height,
          timeRange,
          markovNodes.filter(n => n.id !== markovNode.id),
          parentNode
        );
        // Store the calculated position in the node data
        markovNode.x = position.x;
        markovNode.y = position.y;
      }
      
      return {
        id: markovNode.id,
        type: 'animatedNode',
        position,
        data: markovNode,
      } as Node;
    });
  }, []);

  // Convert Markov edges to React Flow edges
  const convertToReactFlowEdges = useCallback((markovEdges: MarkovEdge[]) => {
    return markovEdges.map((markovEdge) => ({
      id: markovEdge.id,
      source: markovEdge.source,
      target: markovEdge.target,
      type: 'animatedEdge',
      data: markovEdge,
    } as Edge));
  }, []);

  // Update viewport to show exactly the last 3 nodes with space for the next one
  const updateViewportToLastNodes = useCallback(() => {
    if (!containerRef.current || nodes.length === 0) return;
    
    const containerRect = containerRef.current.getBoundingClientRect();
    const viewport = calculateViewportForLastNodes(nodes, containerRect.width, containerRect.height, 3);
    
    if (viewport) {
      setViewport({
        x: containerRect.width / 2 - viewport.x,
        y: containerRect.height / 2 - viewport.y,
        zoom: viewport.zoom,
      }, { duration: 800 }); // Smoothly pan and zoom
    }
  }, [nodes, setViewport]);

  // Update React Flow nodes and edges when Markov data changes
  useEffect(() => {
    const newNodes = convertToReactFlowNodes(nodes);
    const newEdges = convertToReactFlowEdges(edges);
    
    setReactFlowNodes(newNodes);
    setReactFlowEdges(newEdges);
    
    // Update viewport to show last 3 nodes
    if (nodes.length > 0) {
      setTimeout(() => {
        updateViewportToLastNodes();
      }, 100);
    }
  }, [nodes, edges, convertToReactFlowNodes, convertToReactFlowEdges, setReactFlowNodes, setReactFlowEdges, updateViewportToLastNodes]);

  const onConnect = useCallback(
    (params: Connection) => setReactFlowEdges((eds) => addEdge(params, eds)),
    [setReactFlowEdges]
  );

  const onNodeClickHandler = useCallback(
    (event: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node.data as MarkovNode);
      }
    },
    [onNodeClick]
  );

  return (
    <div 
      ref={containerRef} 
      className={`w-full h-full ${className}`}
    >
      <ReactFlow
        nodes={reactFlowNodes}
        edges={reactFlowEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClickHandler}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView={false}
        attributionPosition="bottom-left"
        className="bg-gray-100"
        style={{ background: '#f3f4f6' }}
        proOptions={{ hideAttribution: true }}
        minZoom={0.1}
        maxZoom={2}
      />
    </div>
  );
}; 