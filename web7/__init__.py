from letta_client import Letta
client = Letta(token="LETTA_API_KEY")
agent_state = client.agents.create(
    model="openai/gpt-4.1",
    embedding="openai/text-embedding-3-small",
    memory_blocks=[
        {
          "label": "human",
          "value": "The human's name is Chad. They like vibe coding."
        },
        {
          "label": "persona",
          "value": "My name is Sam, the all-knowing sentient AI."
        }
    ],
    tools=["web_search", "run_code"]
)
print(agent_state.id)