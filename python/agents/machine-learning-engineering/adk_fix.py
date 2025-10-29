#!/usr/bin/env python3
"""Fix Windows symlink permission issue for ADK"""

import os
import sys
import tempfile
import shutil


def fix_adk_logging():
    """Fix ADK logging symlink issue on Windows"""

    # Create a custom temp directory that doesn't require symlink permissions
    custom_temp_dir = os.path.join(os.path.expanduser("~"), "adk_temp")

    if not os.path.exists(custom_temp_dir):
        os.makedirs(custom_temp_dir)
        print(f"✅ Created custom temp directory: {custom_temp_dir}")

    # Set environment variables to override ADK's default behavior
    os.environ["TEMP"] = custom_temp_dir
    os.environ["TMP"] = custom_temp_dir
    os.environ["ADK_LOG_DIR"] = custom_temp_dir

    print(f"✅ Set ADK log directory to: {custom_temp_dir}")

    # Create the agents_log subdirectory
    agents_log_dir = os.path.join(custom_temp_dir, "agents_log")
    if not os.path.exists(agents_log_dir):
        os.makedirs(agents_log_dir)
        print(f"✅ Created agents_log directory: {agents_log_dir}")

    return custom_temp_dir


def run_adk_with_fix():
    """Run ADK with the permission fix applied"""

    print("🔧 Applying Windows permission fix for ADK...")
    temp_dir = fix_adk_logging()

    print(f"📁 Using temp directory: {temp_dir}")
    print("🚀 Starting ADK agent...")
    print("=" * 50)

    # Import and run the agent
    try:
        from google.genai import types
        from google.adk.runners import InMemoryRunner
        from machine_learning_engineering.agent import root_agent
        import asyncio

        print("🤖 Machine Learning Engineering Agent")
        print(f"Agent name: {root_agent.name}")
        print(f"Model: {os.getenv('ROOT_AGENT_MODEL', 'Not set')}")
        print("=" * 50)
        print("Type 'quit' to exit")
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
        return False
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return False

    return True


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv

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

    success = run_adk_with_fix()
    if not success:
        sys.exit(1)
