from letta_client import AsyncLetta
import asyncio
import ast
import os
from dotenv import load_dotenv

from .interface_search import detach_tools, mcp_search

load_dotenv()

client = AsyncLetta(token=os.getenv("LETTA_API_KEY"))


async def generate_task_list(agent_id, user_input):
    await detach_tools(agent_id)
    stream = client.agents.messages.create_stream(
        agent_id=agent_id,
        messages=[
            {
                "role": "user",
                "content": f"""You are an AI assistant tasked with breaking down a user's prompt into actionable tasks. The goal is to create a list of separate tasks that can be used to query and find appropriate MCP (Model Context Protocol) servers and tools. DO NOT USE ANY TOOL CALLS IN THIS PART.

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

                            Output your response as a Python list containing strings, where each string represents a single task. Do not include any explanation or additional text outside of the Python list. REMINDER: DO NOT USE ANY TOOL CALLS IN THIS PART.

                            For example:
                            ["Task 1", "Task 2", "Task 3"]""",
            }
        ],
    )

    task_list = ""
    async for m in stream:
        print(m)
        if m.message_type == "assistant_message":
            task_list = m.content

    await client.agents.blocks.modify(
        agent_id=agent_id, block_label="tasks", value=task_list
    )
    return ast.literal_eval(task_list)


async def accomplish_task(agent_id, task, task_number):
    await detach_tools(agent_id)
    response = await mcp_search(agent_id, task, k=3)
    print(response)
    stream = client.agents.messages.create_stream(
        agent_id=agent_id,
        messages=[
            {
                "role": "user",
                "content": f"""
You are an AI assistant equipped with various tools to help you complete specific tasks. Your goal is to execute the given task using all available tools efficiently and effectively.

Here is the task you need to complete:
<task>
{task}
</task>

Process for completing the task:
1. Analyze the task and determine which tools you need to use.
2. Use the tools in a logical order to gather necessary information or perform required actions.
3. If you encounter any errors or unexpected results, reassess your approach and try alternative methods.
4. Continue using tools and processing results until you have enough information to complete the task.

Before providing your final answer, use <scratchpad> tags to outline your thought process and plan your approach. This will help you organize your ideas and ensure you're using the tools effectively.

When you're ready to give your final answer, please provide it in the following format:
<answer>
[Your detailed response to the task, including any relevant information gathered from the tools]
</answer>

Reminders and best practices:
- Only use the tools provided to you. Do not assume you have access to any other capabilities.
- If a tool returns an error, try to understand why and adjust your approach accordingly.
- Be thorough in your analysis and use of the tools to ensure you're addressing all aspects of the task.
- If you're unsure about how to proceed at any point, review the task description and available tools to see if you've missed anything.
- Always strive for accuracy and completeness in your final answer.

Now, please proceed with the task using the provided tools and following the instructions above.
                """,
            }
        ],
    )

    messages = []
    async for message in stream:
        messages.append(message)
        print(message)

    if f"task {task_number}" in [
        b.label for b in await client.agents.blocks.list(agent_id=agent_id)
    ]:
        await client.agents.blocks.modify(
            agent_id=agent_id,
            block_label=f"task {task_number}",
            value=str(messages),
        )
    else:
        block = await client.blocks.create(
            label=f"task {task_number}",
            description="A block to store information {task}",
            value=str(messages),
            limit=40000,
        )
        print("new block created")
        await client.agents.blocks.attach(agent_id=agent_id, block_id=block.id)


async def main():
    agent_id = "agent-4d880512-8969-4ef3-9b18-a42bddb4dd16"
    prompt = "Search through Notion and look for the email address of the person wearing a green shirt. Then, write them an email congratulating them for winning the Berkeley AI hackathon."
    task_list = await generate_task_list(
        agent_id,
        prompt,
    )
    print(task_list)

    # print(task)
    # print()

    for i, task in enumerate(task_list):
        await accomplish_task(agent_id, task, i)
