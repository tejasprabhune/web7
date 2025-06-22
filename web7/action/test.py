from letta_client import Letta
import ast
<<<<<<< Updated upstream
from dotenv import load_dotenv
import os
=======
import dotenv
import os
import pprint


agent_id = "agent-eba622c8-4ab9-49db-8c66-20e83f4fb4f7"

dotenv.load_dotenv()
client = Letta(token=os.getenv("LETTA_API_KEY"))
>>>>>>> Stashed changes

load_dotenv()

<<<<<<< Updated upstream
client = Letta(token=os.getenv("LETTA_API_KEY"))
=======
>>>>>>> Stashed changes

def intialize_agent(tools_list = ["web_search", "run_code"]):
    agent_state = client.agents.create(
    model="anthropic/claude-3-5-sonnet-20241022",
    embedding="openai/text-embedding-3-small",
    memory_blocks=[
                    {
                    "label": "human",
                    "value": "The human's name is Chad. They are diligent task doer that thinks deeply."
                    },
                    {
                    "label": "persona",
                    "value": "My name is Sam, the all-knowing sentient AI."
                    }
                ],
                    tools=tools_list
                )
    return agent_state


def generate_task_list(agent_id, user_input):
    task_list_response = client.agents.messages.create(
                agent_id=agent_id,
                messages=[
                    {
                        "role": "user",
                        "content": f'Generate a list of tasks you need to do to acomplish: {user_input} Return the answer ONLY as a Python list of strings. Be sparing in the amount of tasks your generate. It can be 1.'
                    }
                ]
                )
    task_list = next(m.content for m in task_list_response.messages if m.message_type == "assistant_message")
    client.agents.blocks.modify(
    agent_id=agent_id,
    block_label="task list",
    value = task_list
    )
    #client.agents.blocks.attach(agent_id=agent_id, block_id=block.id)
    return ast.literal_eval(task_list)

def search_mcps(agent_ids):
    return 

def delete_mcps(agent_ids):
    return 

def accomplish_task(agent_id, task):
    search_mcps(agent_id)
    

    # Use the "everything" mcp server:
    # https://github.com/modelcontextprotocol/servers/tree/main/src/everything
    mcp_server_name = "web7_notion"
    mcp_tool_name = "NOTION_ADD_PAGE_CONTENT"

    # List all McpTool belonging to the "everything" mcp server.
    mcp_tools = client.tools.list_mcp_tools_by_server(
        mcp_server_name=mcp_server_name,
    )

    mcp_tool = client.tools.add_mcp_tool(
        mcp_server_name=mcp_server_name, mcp_tool_name=mcp_tool_name
    )

    mcp_tools = client.tools.list_mcp_tools_by_server(
        mcp_server_name=mcp_server_name,
    )


    response = client.agents.messages.create(
        agent_id= agent_id,
        messages=[
            {
                "role": "user",
                "content": f"Call the NOTION_ADD_PAGE_CONTENT tool to accomplish {task}",
            }
        ],
    )
    for message in response.messages:
        print(message)


        
    delete_mcps(agent_id)

#agent = intialize_agent()

task_list = generate_task_list(agent_id, "Write hello in a notion")
print(task_list)
accomplish_task(agent_id, task_list[0])



