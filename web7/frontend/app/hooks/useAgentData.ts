import { useState, useEffect, useCallback, useRef } from 'react';
import { get_agent_id, get_action_plan, get_action_info } from '../constants';

interface AgentData {
  agentId: string | null;
  actionPlan: { steps: any[] } | null;
  currentStep: string | null;
  stepResponse: any | null;
  isLoading: boolean;
  error: string | null;
}

export function useAgentData() {
  const [data, setData] = useState<AgentData>({
    agentId: null,
    actionPlan: null,
    currentStep: null,
    stepResponse: null,
    isLoading: false,
    error: null,
  });

  const isFetchingActionPlanRef = useRef(false);

  const createAgent = useCallback(async (query: string) => {
    setData(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await fetch(get_agent_id, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
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

  const fetchActionPlan = useCallback(async (agentId: string) => {
    if (!agentId || isFetchingActionPlanRef.current) return null;
    
    isFetchingActionPlanRef.current = true;
    setData(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await fetch(get_action_plan(agentId));
      
      if (!response.ok) {
        throw new Error('Failed to fetch action plan');
      }

      const result = await response.json();
      
      console.log('Action plan response:', result);
      
      setData(prev => ({
        ...prev,
        actionPlan: result,
        isLoading: false
      }));

      // Return the status to determine if polling should continue
      // Handle different possible response structures
      const status = result.status !== undefined ? result.status : 
                    result.data?.status !== undefined ? result.data.status : 
                    null;
      return status;
    } catch (error) {
      console.error("Error fetching action plan:", error);
      setData(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Unknown error',
        isLoading: false
      }));
      return null;
    } finally {
      isFetchingActionPlanRef.current = false;
    }
  }, []);

  const fetchStepResponse = useCallback(async (agentId: string, stepId: string) => {
    if (!agentId || !stepId) return;
    
    setData(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await fetch(get_action_info(agentId, stepId));
      
      if (!response.ok) {
        throw new Error('Failed to fetch step response');
      }

      const result = await response.json();
      
      setData(prev => ({
        ...prev,
        stepResponse: result,
        isLoading: false
      }));
    } catch (error) {
      console.error("Error fetching step response:", error);
      setData(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Unknown error',
        isLoading: false
      }));
    }
  }, []);

  const resetData = useCallback(() => {
    setData({
      agentId: null,
      actionPlan: null,
      currentStep: null,
      stepResponse: null,
      isLoading: false,
      error: null,
    });
  }, []);

  const setCurrentStepId = useCallback((stepId: string | null) => {
    setData(prev => ({ ...prev, currentStep: stepId }));
  }, []);

  // Auto-fetch action plan when agentId is set
  useEffect(() => {
    if (data.agentId && !data.actionPlan && !isFetchingActionPlanRef.current) {
      fetchActionPlan(data.agentId);
    }
  }, [data.agentId, data.actionPlan]);

  return {
    ...data,
    createAgent,
    fetchActionPlan,
    fetchStepResponse,
    resetData,
    setCurrentStepId,
  };
} 