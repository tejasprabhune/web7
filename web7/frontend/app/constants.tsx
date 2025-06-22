export const api_url = "http://127.0.0.1:8000";

export const get_agent_id = `${api_url}/user-query`;
export const get_action_plan = (agentId: string) => `${api_url}/workflow/${agentId}/steps`;
export const get_action_info = (agentId: string, stepId: string) => `${api_url}/workflow/${agentId}/${stepId}`;