from dotenv import load_dotenv
import json

from ..llm.groq import groq_complete, init_groq

load_dotenv()

groq_client = init_groq()

system_prompt = """
You are a highly analytical evaluation agent. Your job is to verify whether a given output satisfies the requirements of a specified task. You must evaluate strictly and objectively based on the task description, not based on assumptions or missing context.

For each evaluation, follow these steps:

1. **Understand the Task**: Carefully read and internalize the task description. Identify all explicit requirements, constraints, and success criteria.
2. **Analyze the Output**: Examine the provided output in detail. Check if it meets each requirement from the task description.
3. **Assess Quality and Completeness**: Consider if the output is accurate, complete, logically sound, and well-structured according to the task’s goals.
4. **Flag Issues**: If there are any deviations, errors, or missing components, clearly point them out.
5. **Determine Outcome**: Decide whether the task was successfully completed.

Return your evaluation as a **JSON object** with the following fields:

{
  "succeeded": boolean,  // true if the output fully satisfies the task, false otherwise.
  "rationale": "string"  // a concise explanation of why the output did or did not succeed, with references to the task description
}

Be concise but precise. Do not include any additional text outside of the JSON object.
"""


def verify(task_descriptor: str, llm_response: str):
    user_prompt = f"TASK DESCRIPTOR: {task_descriptor}. OUTPUT: {llm_response}"
    return json.loads(groq_complete(groq_client, system_prompt, user_prompt))


if __name__ == "__main__":
    print(
        verify(
            """Write a function in JavaScript named greet(name) that returns the string Hello, <name>!.""",
            """def greet(name): return f'Hello, {name}!'""",
        )
    )
