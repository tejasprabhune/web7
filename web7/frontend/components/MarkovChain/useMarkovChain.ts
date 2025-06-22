import { useState, useEffect, useCallback, useRef } from 'react';
import { MarkovNode, MarkovEdge, MarkovChainState } from './types';
import { generateEdgeId, shiftNodesUp, calculateNodePosition, generateNodeId } from './utils';

interface UseMarkovChainOptions {
  stepResponse?: any | null;
  actionPlan?: { steps: any[] } | null;
  currentStepId?: string | null;
  onStepComplete?: (nextStepId: string | null) => void;
  onNewNode?: (node: MarkovNode) => void;
  onNewEdge?: (edge: MarkovEdge) => void;
}

export const useMarkovChain = (options: UseMarkovChainOptions = {}) => {
  const {
    stepResponse,
    actionPlan,
    currentStepId,
    onStepComplete,
    onNewNode,
    onNewEdge,
  } = options;

  const [state, setState] = useState<MarkovChainState>({
    nodes: [],
    edges: [],
    currentTime: Date.now(),
  });

  // This effect runs when new step data is received from the parent.
  // It handles adding the node to the state if it's new.
  useEffect(() => {
    if (!stepResponse || stepResponse.status !== 'updated') return;

    const stepData = stepResponse;
    const nodeExists = state.nodes.some(node => node.id === stepData.step_id);

    if (!nodeExists) {
      setState(prevState => {
        const currentTime = Date.now();
        
        const parentNode = prevState.nodes.length > 0 ? prevState.nodes[prevState.nodes.length - 1] : undefined;
        
        const position = calculateNodePosition(
          { id: stepData.step_id, label: stepData.action, timestamp: currentTime, data: {} },
          800, // Assuming a container width
          600, // Assuming a container height
          { min: 0, max: 1 }, // Placeholder time range
          prevState.nodes,
          parentNode
        );

        const newNode: MarkovNode = {
          id: stepData.step_id,
          label: stepData.action,
          timestamp: currentTime,
          x: position.x,
          y: position.y,
          data: {
            details: stepData.details,
            mcp_server: stepData.mcp_server,
            mcp_server_img_url: stepData.mcp_server_img_url,
            value: Math.random() * 100, // Placeholder
          },
        };

        let newEdge: MarkovEdge | null = null;
        if (prevState.nodes.length > 0) {
          const lastNode = prevState.nodes[prevState.nodes.length - 1];
          newEdge = {
            id: generateEdgeId(lastNode.id, newNode.id),
            source: lastNode.id,
            target: newNode.id,
            timestamp: currentTime,
          };
        }

        if (onNewNode) onNewNode(newNode);
        if (onNewEdge && newEdge) onNewEdge(newEdge);

        const shiftedNodes = shiftNodesUp(prevState.nodes);
        const newNodes = [...shiftedNodes, newNode];
        const newEdges = newEdge ? [...prevState.edges, newEdge] : prevState.edges;
        
        return {
          nodes: newNodes,
          edges: newEdges,
          currentTime,
        };
      });

      // Move to the next step
      if (actionPlan && onStepComplete) {
        const currentIndex = actionPlan.steps.findIndex(step => step.id === currentStepId);
        if (currentIndex !== -1 && currentIndex + 1 < actionPlan.steps.length) {
          const nextStepId = actionPlan.steps[currentIndex + 1].id;
          onStepComplete(nextStepId);
        } else {
          // Last step was completed
          onStepComplete(null);
        }
      }
    }
  }, [stepResponse, actionPlan, currentStepId, onStepComplete, onNewNode, onNewEdge]);

  // Add a node manually
  const addNode = useCallback((label: string, data?: any) => {
    setState(prevState => {
      const currentTime = Date.now();
      const newNode: MarkovNode = {
        id: generateNodeId(currentTime, prevState.nodes.length),
        label,
        timestamp: currentTime,
        data,
      };

      let newEdge: MarkovEdge | null = null;
      if (prevState.nodes.length > 0) {
        const lastNode = prevState.nodes[prevState.nodes.length - 1];
        newEdge = {
          id: generateEdgeId(lastNode.id, newNode.id),
          source: lastNode.id,
          target: newNode.id,
          timestamp: currentTime,
        };
      }

      // Shift all existing nodes up to make room for the new one
      const shiftedNodes = shiftNodesUp(prevState.nodes, 100);
      
      return {
        nodes: [...shiftedNodes, newNode],
        edges: newEdge ? [...prevState.edges, newEdge] : prevState.edges,
        currentTime,
      };
    });
  }, []);

  // Clear all nodes
  const clearNodes = useCallback(() => {
    setState({
      nodes: [],
      edges: [],
      currentTime: Date.now(),
    });
  }, []);

  return {
    nodes: state.nodes,
    edges: state.edges,
    currentTime: state.currentTime,
    addNode,
    clearNodes,
  };
}; 
