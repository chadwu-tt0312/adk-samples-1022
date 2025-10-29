#!/usr/bin/env python3
"""Alternative ADK runner that bypasses symlink issues"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set required environment variables if not set
if not os.getenv("ROOT_AGENT_MODEL"):
    os.environ["ROOT_AGENT_MODEL"] = "gemini-2.5-flash"

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
    # Import ADK components directly
    from google.adk.agents import Agent
    from google.genai import types
    from google.adk.runners import InMemoryRunner
    from google.adk.sessions import InMemorySessionService
    from machine_learning_engineering.agent import root_agent
    import asyncio

    print("🤖 Machine Learning Engineering Agent (ADK Compatible)")
    print("=" * 60)
    print(f"Agent name: {root_agent.name}")
    print(f"Model: {os.getenv('ROOT_AGENT_MODEL')}")
    print(f"Sub-agents: {len(root_agent.sub_agents)}")
    print("=" * 60)
    print("Type 'quit' to exit, 'help' for commands")
    print()

    # Initialize runner and session
    app_name = "machine-learning-engineering"
    runner = InMemoryRunner(agent=root_agent, app_name=app_name)

    async def create_session():
        return await runner.session_service.create_session(
            app_name=runner.app_name, user_id="interactive_user"
        )

    session = asyncio.run(create_session())
    print(f"✅ Session created: {session.id}")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() == "quit":
                print("👋 Goodbye!")
                break
            elif user_input.lower() == "help":
                print("\n📋 Available commands:")
                print("- quit: Exit the program")
                print("- help: Show this help message")
                print("- Any other text: Send to the agent")
                print()
                continue
            elif not user_input:
                continue

            print("🤖 Agent: ", end="", flush=True)

            # Generate response from agent using runner
            async def get_response():
                content = types.Content(parts=[types.Part(text=user_input)], role="user")
                response_text = ""
                async for event in runner.run_async(
                    user_id=session.user_id,
                    session_id=session.id,
                    new_message=content,
                ):
                    if event.content.parts and event.content.parts[0].text:
                        response_text += event.content.parts[0].text
                return response_text

            response = asyncio.run(get_response())
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")
            print()

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error initializing agent: {e}")
    sys.exit(1)
