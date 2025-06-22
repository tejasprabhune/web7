from letta_client import Letta
import ast
from dotenv import load_dotenv
import os

load_dotenv()

client = Letta(token=os.getenv("LETTA_API_KEY"))

def intialize_agent(tools_list = ["web_search", "run_code"]):
    agent_state = client.agents.create(
    model="openai/gpt-4.1",
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


def generate_task_list(agent, user_input):
    task_list_response = client.agents.messages.create(
                agent_id=agent.id,
                messages=[
                    {
                        "role": "user",
                        "content": f'Generate a list of tasks you need to do to acomplish: {user_input} Return the answer ONLY as a Python list of strings.'
                    }
                ]
                )
    task_list = task_list_response.messages[-1].content
    block = client.blocks.create(
            label="tast list",
            description="A block to store the set of tasks that you will need to accomplish",
            value=task_list,
            limit=4000,
        )
    client.agents.blocks.attach(agent_id=agent.id, block_id=block.id)
    return ast.literal_eval(task_list)


agent = intialize_agent()
task_list = generate_task_list(agent, "I want to order food")
print(task_list)
