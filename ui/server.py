from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import sys
import os

# Add the root directory to the Python path
# This is a crucial step to ensure the server can find your 'agent' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import the dispatcher
from agent.dispatcher import dispatch_command

# Initialize the FastAPI app
app = FastAPI()

# Define the structure of the request body we expect from the front-end
class CommandRequest(BaseModel):
    command: str

# Define the main API endpoint
@app.post("/execute_command")
async def execute_command(request: CommandRequest):
    """
    Receives a command from the web UI, passes it to the agent's dispatcher,
    and returns the result.
    """
    print(f"Received command from UI: {request.command}")
    # This is where the magic happens: we call the same dispatcher as our CLI
    result = await dispatch_command(request.command)
    return {"result": result}

# Mount the 'static' directory to serve our HTML, CSS, and JS files
app.mount("/", StaticFiles(directory="ui/static", html=True), name="static")

# A simple function to run the server
if __name__ == "__main__":
    print("Starting FastAPI server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)