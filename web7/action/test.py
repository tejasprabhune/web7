from letta_client import Letta
import ast
from dotenv import load_dotenv
import os
import dotenv
import os
import pprint
from letta_client.core.request_options import RequestOptions
from types import SimpleNamespace
import json


agent_id = "agent-94dd08a3-5405-4d5f-a201-e0cb896b8ee1"

dotenv.load_dotenv()
client = Letta(token=os.getenv("LETTA_API_KEY"))

load_dotenv()


def intialize_agent(tools_list=["web_search", "run_code"]):
    agent_state = client.agents.create(
        model="anthropic/claude-3-5-sonnet-20241022",
        embedding="openai/text-embedding-3-small",
        memory_blocks=[
            {
                "label": "human",
                "value": "The human's name is a diligent task doer that thinks deeply.",
            },
            {
                "label": "persona",
                "value": "My name is Sam, the all-knowing sentient AI.",
            },
        ],
        tools=tools_list,
    )
    return agent_state


def generate_task_list(agent_id, user_input):
    task_list_response = client.agents.messages.create(
        agent_id=agent_id,
        messages=[
            {
                "role": "user",
                "content": f"Generate a list of tasks you need to do to acomplish: {user_input} Return the answer ONLY as a Python list of strings. Make 3 elements in this list. Do not include any other text.",
            }
        ],
        request_options=RequestOptions(timeout_in_seconds=0.01),
    )

    task_list = next(
        m.content
        for m in task_list_response.messages
        if m.message_type == "assistant_message"
    )
    client.agents.blocks.modify(
        agent_id=agent_id, block_label="task list", value=task_list
    )
    # client.agents.blocks.attach(agent_id=agent_id, block_id=block.id)
    return ast.literal_eval(task_list)


def search_mcps(agent_ids):
    return


def delete_mcps(agent_ids):
    return


def add_mcp(server_name):
    mcp_server_name = server_name

    mcp_tools = client.tools.list_mcp_tools_by_server(
        mcp_server_name=mcp_server_name,
    )
    for tool in mcp_tools:
        pprint.pprint(tool.name)
        print()
        mcp_tool = client.tools.add_mcp_tool(
            mcp_server_name=mcp_server_name, mcp_tool_name=tool.name
        )
        client.agents.tools.attach(agent_id=agent_id, tool_id=mcp_tool.id)


def accomplish_task(agent_id, task, task_number):
    search_mcps(agent_id)
    response = client.agents.messages.create(
        agent_id=agent_id,
        messages=[
            {
                "role": "user",
                "content": f"Accomplish the following task using your MCP tooling: {task}",
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

    delete_mcps(agent_id)


# agent = intialize_agent()
agent_id = "agent-4d880512-8969-4ef3-9b18-a42bddb4dd16"
print(agent_id)

# add_mcp("web7_notion")
# add_mcp("web7_gmail")
# task_list = generate_task_list(agent_id, "Create a new Notion page with a story containing personal Notion information'")
# print(task_list)
task_list = [
    # "Find the Notion User's Personal Information",
    # "Use this Notion User's Personal Information to create a nice story",
    "Send an email to prabhune@berkeley.edu saying how this was automatically sent from an LLM",
]
# task_list = ["Find the Notion User's Personal Information"]
for task in task_list:
    print(task)
    accomplish_task(agent_id, task, task_list.index(task))
    print(f"Task: {task} done")
