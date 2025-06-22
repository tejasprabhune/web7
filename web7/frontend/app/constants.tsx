export const api_url = "https://b8fc-2001-5a8-4517-9500-7c89-ff92-d274-9a8d.ngrok-free.app";

export const get_agent_id = `${api_url}/user-query`;
export const get_action_plan = (agentId: string) => `${api_url}/workflow/${agentId}/steps`;
export const get_action_info = (agentId: string, stepId: string) => `${api_url}/workflow/${agentId}/${stepId}`;