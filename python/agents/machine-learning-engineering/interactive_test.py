#!/usr/bin/env python3
"""Interactive test script for the machine learning engineering agent"""

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

try:
    from machine_learning_engineering.agent import root_agent

    print("🤖 Machine Learning Engineering Agent")
    print("=" * 50)
    print(f"Agent name: {root_agent.name}")
    print(f"Model: {os.getenv('ROOT_AGENT_MODEL')}")
    print(f"Sub-agents: {len(root_agent.sub_agents)}")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for commands")
    print()

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

            # Generate response from agent
            response = root_agent.generate_content(user_input)

            if hasattr(response, "text"):
                print(response.text)
            else:
                print(str(response))

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
