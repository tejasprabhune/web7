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

def accomplish_task(agent_id, task, task_number):
    response = client.agents.messages.create(
        agent_id=agent_id,
        messages=[
            {
                "role": "user",
                "content": f"""You are an AI assistant tasked with analyzing a given task, selecting the most appropriate Model Context Protocol (MCP) to complete it, and then executing the task using that MCP. Your goal is to efficiently complete the task while adhering to the following instructions.

                    First, you will be provided with a task description and a list of available MCPs. Here is the task you need to complete:

                    <task>
                    {task}
                    </task>

                    In your analysis, consider the following:
                    1. What is the main objective of the task?
                    2. What type of information or actions are needed to complete the task?

                    You should use this analysis to trigger the search tool that you have available to you and retrieve all of the MCPs that you want to use in the future. These MCPs will automatically be injected in your agent, which will provide you with future tools that you can use after this search function has been called.

                    After the search, select the single most appropriate MCP that you believe will be most effective in completing the task. While you should only use one MCP to complete the action, remember that you can use any number of tool calls within that MCP as needed.

                    Once you have selected the MCP, explain your reasoning for choosing it. Then, describe how you plan to use this MCP to complete the task. Be specific about which tool calls you anticipate making and in what order.

                    Finally, execute the task using the selected MCP. As you work through the task, make any necessary tool calls within the MCP. If you encounter any difficulties or need to adjust your approach, explain your reasoning and the changes you're making.

                    After you have executed the search function, present your work in the following format with the resulting MCPs:

                    <analysis>
                    [Your analysis of the task and available MCPs]
                    </analysis>

                    <selected_mcp>
                    [Name of the selected MCP]
                    </selected_mcp>

                    <reasoning>
                    [Your reasoning for selecting this MCP]
                    </reasoning>

                    <execution_plan>
                    [Your plan for using the MCP to complete the task]
                    </execution_plan>

                    <task_execution>
                    [The actual execution of the task, including any tool calls and your thought process]
                    </task_execution>

                    <result>
                    [The final result or output of the completed task]
                    </result>

                    Remember to be thorough in your analysis, clear in your reasoning, and efficient in your execution. If you encounter any ambiguities or need more information to complete the task, state this clearly in your response.
            """,
            }
        ],
    )
    for message in response.messages:
        print(message)

    if f"task {task_number}" in [
        b.label for b in client.agents.blocks.list(agent_id=agent_id)
    ]:
        client.agents.blocks.modify(
            agent_id=agent_id,
            block_label=f"task {task_number}",
            value=str(response.messages),
        )
    else:
        block = client.blocks.create(
            label=f"task {task_number}",
            description="A block to store information {task}",
            value=str(response.messages),
            limit=40000,
        )
        print("new block created")
        client.agents.blocks.attach(agent_id=agent_id, block_id=block.id)

    