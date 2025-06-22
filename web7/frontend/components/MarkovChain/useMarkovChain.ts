import { useState, useEffect, useCallback, useRef } from 'react';
import { MarkovNode, MarkovEdge, MarkovChainState } from './types';
import { generateEdgeId, shiftNodesUp, calculateNodePosition } from './utils';
import { get_action_info } from '@/app/constants';

interface UseMarkovChainOptions {
  agentId?: string | null;
  actionPlan?: { steps: any[] } | null;
  currentStepId?: string | null;
  onStepComplete?: (nextStepId: string | null) => void;
  pollingInterval?: number;
  maxNodes?: number;
  onNewNode?: (node: MarkovNode) => void;
  onNewEdge?: (edge: MarkovEdge) => void;
  autoStart?: boolean;
}

export const useMarkovChain = (options: UseMarkovChainOptions = {}) => {
  const {
    agentId,
    actionPlan,
    currentStepId,
    onStepComplete,
    pollingInterval = 3000,
    maxNodes = 50,
    onNewNode,
    onNewEdge,
    autoStart = true,
  } = options;

  const [state, setState] = useState<MarkovChainState>({
    nodes: [],
    edges: [],
    currentTime: Date.now(),
  });
  const [isPollingActive, setIsPollingActive] = useState(autoStart);

  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const isPollingRef = useRef(false);

  const pollForNewNodes = useCallback(async () => {
    if (isPollingRef.current || !agentId || !currentStepId) return;
    isPollingRef.current = true;

    try {
      const response = await fetch(get_action_info(agentId, currentStepId));
      if (!response.ok) {
        console.error('Error fetching action info, stopping polling.');
        if (pollingRef.current) clearInterval(pollingRef.current);
        if (onStepComplete) onStepComplete(null); // Stop on error
        return;
      }
      const stepData = await response.json();
      console.log(stepData);
      const nodeExists = state.nodes.some(node => node.id === stepData.step_id);

      if (stepData.status === 'updated' && !nodeExists) {
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
            // Last step was completed, stop polling.
            onStepComplete(null);
            if (pollingRef.current) clearInterval(pollingRef.current);
          }
        }
      }
    } catch (error) {
      console.error('Error polling for new nodes:', error);
      if (onStepComplete) onStepComplete(null); // Stop on error
    } finally {
      isPollingRef.current = false;
    }
  }, [agentId, currentStepId, actionPlan, onStepComplete, state.nodes, onNewNode, onNewEdge]);

  useEffect(() => {
    // Stop condition: if polling is inactive or there's no step to process
    if (!isPollingActive || !currentStepId) {
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
        pollingRef.current = null;
      }
      return;
    }

    // Set a timeout to call the polling function
    pollingRef.current = setTimeout(() => {
      pollForNewNodes();
    }, pollingInterval);

    // Cleanup: clear the timeout if dependencies change or component unmounts
    return () => {
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
      }
    };
  }, [isPollingActive, currentStepId, pollForNewNodes, pollingInterval]);

  // Start polling automatically if autoStart is true
  useEffect(() => {
    if (autoStart) {
      setIsPollingActive(true);
    }
  }, [autoStart]);

  // Start polling
  const startPolling = useCallback(() => {
    setIsPollingActive(true);
  }, []);

  // Stop polling
  const stopPolling = useCallback(() => {
    setIsPollingActive(false);
  }, []);

  // Add a node manually
  const addNode = useCallback((label: string, data?: any) => {
    setState(prevState => {
      const currentTime = Date.now();
      const newNode: MarkovNode = {
        id: generateEdgeId(currentTime, prevState.nodes.length),
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
    startPolling,
    stopPolling,
    addNode,
    clearNodes,
    isPolling: isPollingActive,
  };
}; 