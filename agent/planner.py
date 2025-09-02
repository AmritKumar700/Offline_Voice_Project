import ollama
import json

# This is the master prompt that guides the LLM.
# It explains its role, the tools available, and the required JSON output format.
# In agent/planner.py

# In agent/planner.py

# in agent/planner.py

# in agent/planner.py

# in agent/planner.py

PLANNER_PROMPT = """
You are an expert AI agent controller. Your job is to create a JSON plan to fulfill a user's request using the available tools.

## Available Tools:
- `answer_question_from_web(query: str)`: Use this for any question that requires finding information or answers online.
- `get_current_time()`: Use this for any requests about the current time.
- `open_application(app_name: str)`: Use this to open an application.

## User Request:
{user_request}

## Instructions:
1.  Choose the single best tool to accomplish the request.
2.  Do NOT chain tools together. The tools are powerful and handle chains internally.
3.  Respond with a JSON object containing `tool_name` and `parameters`.

## Your JSON Plan:
"""
# In agent/planner.py

def create_plan(user_request: str):
    """
    Creates a plan using the LLM based on the user's request.
    """
    print(f"🧠 Creating plan for request: {user_request}")

    prompt = PLANNER_PROMPT.format(user_request=user_request)

    try:
        response = ollama.chat(
            model="llama3",
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.0}
        )

        response_text = response['message']['content']
        print(f"🤖 LLM Raw Response: {response_text}")

        # --- THIS IS THE UPGRADE ---
        # Find the start and end of the JSON block
        start_index = response_text.find('{')
        end_index = response_text.rfind('}')

        if start_index != -1 and end_index != -1:
            # Extract the JSON string
            json_plan_str = response_text[start_index:end_index+1]

            # Parse the extracted string
            plan = json.loads(json_plan_str)
            return plan
        else:
            # Handle cases where no JSON is found
            print("❌ Error: No JSON object found in the LLM response.")
            return {"error": "Could not find a valid JSON plan in the response."}
        # ---------------------------

    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {e}")
        return {"error": "The LLM returned invalid JSON."}
    except Exception as e:
        print(f"❌ Error creating plan: {e}")
        return {"error": f"An error occurred: {e}"}