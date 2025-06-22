import { useState, useEffect, useCallback, useRef } from 'react';
import { get_agent_id, get_action_plan, get_action_info } from '../constants';

interface AgentData {
  agentId: string | null;
  actionPlan: { steps: any[] } | null;
  currentStep: string | null;
  stepResponse: any | null;
  stepHistory: string[];
  isLoading: boolean;
  error: string | null;
}

export function useAgentData() {
  const [data, setData] = useState<AgentData>({
    agentId: null,
    actionPlan: null,
    currentStep: null,
    stepResponse: null,
    stepHistory: [],
    isLoading: false,
    error: null,
  });
  const [isPolling, setIsPolling] = useState(false);

  const isFetchingActionPlanRef = useRef(false);

  const startPolling = useCallback(() => setIsPolling(true), []);
  const stopPolling = useCallback(() => setIsPolling(false), []);

  const createAgent = useCallback(async (query: string) => {
    setData(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await fetch(get_agent_id, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "query": query })
      });

      if (!response.ok) {
        throw new Error('Failed to create agent');
      }

      const result = await response.json();
      console.log("Agent ID received:", result);
      
      setData(prev => ({
        ...prev,
        agentId: result.agent_id,
        isLoading: false
      }));

      return result.agent_id;
    } catch (error) {
      console.error("Error getting agent ID:", error);
      setData(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Unknown error',
        isLoading: false
      }));
      return null;
    }
  }, []);

  // This effect polls for the action plan until it's ready.
  useEffect(() => {
    if (data.agentId && !data.actionPlan) {
      setData(prev => ({ ...prev, isLoading: true, error: null }));

      const intervalId = setInterval(async () => {
        try {
          const response = await fetch(get_action_plan(data.agentId!));
          if (!response.ok) {
            // This will be caught by the catch block
            throw new Error(`Action plan fetch failed with status: ${response.status}`);
          }

          const result = await response.json();
          console.log('Polling for action plan...', result);

          // Stop polling once status is 0 (ready)
          if (result.status === 0) {
            clearInterval(intervalId);
            setData(prev => ({
              ...prev,
              actionPlan: result,
              isLoading: false,
            }));
          }
        } catch (error) {
          clearInterval(intervalId);
          console.error("Error fetching action plan:", error);
          setData(prev => ({
            ...prev,
            error: error instanceof Error ? error.message : 'Unknown error while fetching action plan',
            isLoading: false,
          }));
        }
      }, 2000); // Poll every 2 seconds

      // Cleanup function to clear the interval if the component unmounts
      return () => clearInterval(intervalId);
    }
  }, [data.agentId, data.actionPlan]);

  const fetchStepResponse = useCallback(async (agentId: string, stepId: string) => {
    console.log("fetching step response", agentId, stepId);
    if (!agentId || !stepId) return;

    // No isLoading change here to keep the UI smooth during polling
    
    try {
      const response = await fetch(get_action_info(agentId, stepId));
      
      if (!response.ok) {
        throw new Error('Failed to fetch step response');
      }

      const result = await response.json();
      
      setData(prev => {
        // Update the status of the specific step in the action plan
        const updatedSteps = prev.actionPlan?.steps.map(step => 
          step.id === stepId ? { ...step, status: result.status } : step
        );
        const newActionPlan = prev.actionPlan ? { ...prev.actionPlan, steps: updatedSteps ?? prev.actionPlan.steps } : null;

        // Add the new step details to history if it has details
        const newStepHistory = result.details ? [...prev.stepHistory, result.details] : prev.stepHistory;

        return {
          ...prev,
          actionPlan: newActionPlan,
          stepResponse: result,
          stepHistory: newStepHistory,
        };
      });
    } catch (error) {
      console.error("Error fetching step response:", error);
      // Stop polling on error
      stopPolling();
      setData(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Unknown error',
      }));
    }
  }, [stopPolling]);

  // This effect handles the polling for individual step responses.
  useEffect(() => {
    if (!isPolling || !data.agentId || !data.currentStep) {
      return;
    }

    const intervalId = setInterval(() => {
      fetchStepResponse(data.agentId!, data.currentStep!);
    }, 3000); // Polling interval

    return () => clearInterval(intervalId);
  }, [isPolling, data.agentId, data.currentStep, fetchStepResponse]);

  const resetData = useCallback(() => {
    setData({
      agentId: null,
      actionPlan: null,
      currentStep: null,
      stepResponse: null,
      stepHistory: [],
      isLoading: false,
      error: null,
    });
    stopPolling();
  }, [stopPolling]);

  const setCurrentStepId = useCallback((stepId: string | null) => {
    setData(prev => ({ ...prev, currentStep: stepId }));
  }, []);

  return {
    ...data,
    isPolling,
    startPolling,
    stopPolling,
    createAgent,
    fetchStepResponse,
    resetData,
    setCurrentStepId,
  };
} 
