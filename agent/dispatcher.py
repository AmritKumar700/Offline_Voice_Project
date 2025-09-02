from agent import planner
from agent.tools import os_tools, web_tools
import inspect # Import the inspect module
from agent.tools import reasoning_tools

# in agent/dispatcher.py

TOOL_REGISTRY = {
    "get_current_time": os_tools.get_current_time,
    "open_application": os_tools.open_application,
    "answer_question_from_web": reasoning_tools.answer_question_from_web,
}
# In agent/dispatcher.py

async def dispatch_command(command: str):
    # Step 1: Get the plan (which is now just a single action)
    plan_json = planner.create_plan(command)
    if "error" in plan_json: return plan_json["error"]

    # Step 2: Get the tool and parameters from the single action
    tool_name = plan_json.get("tool_name") or plan_json.get("tool")
    parameters = plan_json.get("parameters") or plan_json.get("params") or {}

    if not tool_name or tool_name not in TOOL_REGISTRY:
        return f"Error: The agent planned to use an unknown tool '{tool_name}'."

    print(f"Executing single tool: {tool_name} with params: {parameters}")

    # Step 3: Execute the single tool
    try:
        tool_function = TOOL_REGISTRY[tool_name]

        # Since 'answer_question_from_web' is async, we primarily await
        if inspect.iscoroutinefunction(tool_function):
            result = await tool_function(**parameters)
        else:
            result = tool_function(**parameters)

        print(f"Final output:\n---\n{result}\n---\n")
        return result
    except Exception as e:
        return f"Error executing tool {tool_name}: {e}"