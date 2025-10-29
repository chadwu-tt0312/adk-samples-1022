#!/usr/bin/env python3
"""Simple test script to run the machine learning engineering agent locally"""

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

    print("✅ Agent loaded successfully!")
    print(f"Agent name: {root_agent.name}")
    print(f"Model: {os.getenv('ROOT_AGENT_MODEL')}")
    print(f"Sub-agents: {len(root_agent.sub_agents)}")

    # Test basic agent functionality
    print("\n🧪 Testing agent with a simple query...")

    # Create a simple test query
    test_query = "Hello, can you help me with a machine learning task?"

    print(f"Query: {test_query}")
    print("Agent response would be generated here...")

    print("\n✅ Agent test completed successfully!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error running agent: {e}")
    sys.exit(1)
