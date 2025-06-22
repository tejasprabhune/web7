from letta_client import Letta
import ast
import os
from dotenv import load_dotenv

load_dotenv()

client = Letta(token=os.getenv("LETTA_API_KEY"))

async def generate_task_list(agent_id, user_input):
    task_list_response = await client.agents.messages.create(
                agent_id=agent_id,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are an AI assistant tasked with breaking down a user's prompt into actionable tasks. The goal is to create a list of separate tasks that can be used to query and find appropriate MCP (Model Context Protocol) servers and tools.

                            Here is the user's prompt:
                            <user_prompt>
                            {user_input}
                            </user_prompt>

                            Analyze the prompt carefully to understand the main action or actions requested by the user. Consider what steps would be necessary to complete the user's request.

                            Break down the prompt into distinct, actionable tasks. Each task should represent a single, clear action that can be performed by querying an MCP server or using a specific tool.

                            Follow these guidelines when creating the task list:
                            1. Keep tasks simple and focused on a single action.
                            2. Don't create more tasks than necessary to complete the user's request.
                            3. If the prompt is very simple (e.g., "send an email"), it's acceptable to have only one task.
                            4. Avoid overlapping or redundant tasks.
                            5. Ensure that the sequence of tasks, if followed, would fulfill the user's request.

                            Output your response as a Python list containing strings, where each string represents a single task. Do not include any explanation or additional text outside of the Python list.

                            For example:
                            ["Task 1", "Task 2", "Task 3"]"""
                    }
                ]
                )
    task_list = next(m.content for m in task_list_response.messages if m.message_type == "assistant_message")
    await client.agents.blocks.modify(
        agent_id=agent_id,
        block_label="tasks",
        value = task_list
    )
    return ast.literal_eval(task_list)

