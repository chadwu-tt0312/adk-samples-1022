#!/usr/bin/env python3
"""Non-interactive ADK runner for a specific task."""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set required environment variables if not set
if not os.getenv("ROOT_AGENT_MODEL"):
    os.environ["ROOT_AGENT_MODEL"] = "gemini-1.5-flash"

if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI"):
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

if not os.getenv("GOOGLE_CLOUD_PROJECT"):
    os.environ["GOOGLE_CLOUD_PROJECT"] = "gen-lang-client-0331781710"

if not os.getenv("GOOGLE_CLOUD_LOCATION"):
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# Disable ADK logging to avoid symlink issues
os.environ["ADK_DISABLE_LOGGING"] = "true"
os.environ["ADK_LOG_LEVEL"] = "ERROR"

try:
    from google.adk.agents import Agent
    from google.genai import types
    from google.adk.runners import InMemoryRunner
    from google.adk.sessions import InMemorySessionService
    from machine_learning_engineering.agent import root_agent

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error initializing agent: {e}")
    sys.exit(1)

async def run_task(task_prompt: str):
    """Initializes and runs the agent for a single task."""
    print("🤖 Machine Learning Engineering Agent (Non-Interactive Runner)")
    print("=" * 60)
    print(f"Agent name: {root_agent.name}")
    print(f"Model: {os.getenv('ROOT_AGENT_MODEL')}")
    print(f"Task Prompt: {task_prompt}")
    print("=" * 60)

    app_name = "machine-learning-engineering"
    runner = InMemoryRunner(agent=root_agent, app_name=app_name)

    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="batch_user"
    )
    print(f"✅ Session created: {session.id}")
    print("⏳ Running agent... (This may take a while)")

    content = types.Content(parts=[types.Part(text=task_prompt)], role="user")
    full_response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            chunk = event.content.parts[0].text
            if chunk:
                full_response += chunk

    print("\n\n✅ Agent run finished.")
    print("=" * 60)
    print("Final Response:")
    print(full_response)
    print("=" * 60)


if __name__ == "__main__":
    # The prompt that will be sent to the agent
    # This is where we specify the task we want to run
    prompt = "Please solve the titanic task"
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])

    try:
        asyncio.run(run_task(prompt))
    except KeyboardInterrupt:
        print("\n🛑 Execution interrupted by user.")
    except Exception as e:
        print(f"❌ An error occurred during execution: {e}")
        import traceback
        traceback.print_exc()
        # In case of an error, print the final state if possible
        # This part is complex because we don't have direct access to the state here.
        # For now, we just report the error.
        
        # To see the final state, you would typically check the generated
        # workspace/titanic/<run_id>/final_state.json file after the run.
        print("\nℹ️ Check the workspace for partial results and logs.")
