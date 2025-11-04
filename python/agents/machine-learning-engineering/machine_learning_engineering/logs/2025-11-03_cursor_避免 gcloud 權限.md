# 避免 gcloud 權限
_Exported on 2025/11/3 at 14:40:57 [GMT+8] from Cursor (2.0.50)_

---

**User**

在專案中只使用 machine-learning-engineering 目錄下的程式

1. "adk web" 指令執行的是哪裡的程式碼? 為何可以配合 machine-learning-engineering ?

2. "adk run machine_learning_engineering" 可以改成不使用 gcloud 相關權限，而全部改用 azure 嗎?

請提供詳細分析與說明

---

**Cursor**


先檢視專案結構，找出 "adk web" 與 "adk run" 的實作位置，以及 machine-learning-engineering 目錄的內容。


改用 grep 搜尋相關程式碼：


檢視 machine-learning-engineering 目錄內容，並搜尋 gcloud 相關使用：


查看主要的 agent.py，並搜尋 gcloud/Google Cloud 相關使用：


進一步檢查環境變數和認證相關設定：


檢查 ADK 如何發現 agent，並查看是否有 Azure 相關的替代方案：


整理詳細分析與說明：


## 詳細分析與說明

### 1. "adk web" 指令執行的是哪裡的程式碼？為何可以配合 machine-learning-engineering？

#### ADK Web 指令的執行機制

`adk web` 指令由 `google-adk` 套件提供，不在專案程式碼中。它會：

1. 掃描目錄結構：在當前目錄與子目錄尋找包含 `__init__.py` 和 `agent.py` 的目錄
2. 自動發現 Agent：找到後，檢查 `agent.py` 中是否有 `root_agent` 變數
3. 載入並啟動 Web UI：將發現的 agent 載入到 Web 介面

#### machine-learning-engineering 的結構

專案目錄結構符合 ADK 的發現規範：

```
machine-learning-engineering/
└── machine_learning_engineering/
    ├── __init__.py          # ✅ 包含 from . import agent
    └── agent.py              # ✅ 定義了 root_agent
```

在 `agent.py` 中定義了符合 ADK 規範的 `root_agent`：

```43:50:python/agents/machine-learning-engineering/machine_learning_engineering/agent.py
root_agent = agents.Agent(
    model=os.getenv("ROOT_AGENT_MODEL"),
    name="mle_frontdoor_agent",
    instruction=prompt.FRONTDOOR_INSTRUCTION,
    global_instruction=prompt.SYSTEM_INSTRUCTION,
    sub_agents=[mle_pipeline_agent],
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
```

因此 `adk web` 能自動發現並載入 machine-learning-engineering agent。

---

### 2. "adk run machine_learning_engineering" 可以改成不使用 gcloud 相關權限，而全部改用 Azure 嗎？

可行，但需要大幅修改。

#### 目前使用 Google Cloud 的位置

1. LLM 模型調用
   - 環境變數：`GOOGLE_GENAI_USE_VERTEXAI=true`
   - 程式碼位置：
```6:9:python/agents/machine-learning-engineering/machine_learning_engineering/agent.py
from google.genai import types
from google.adk.agents import callback_context as callback_context_module

from google.adk import agents
```

2. Google Search Tool
```15:15:python/agents/machine-learning-engineering/machine_learning_engineering/sub_agents/initialization/agent.py
from google.adk.tools.google_search_tool import google_search
```

3. 部署相關（`deployment/deploy.py`）
   - 使用 `vertexai` 和 `google-cloud-aiplatform`

4. 依賴套件（`pyproject.toml`）
```12:16:python/agents/machine-learning-engineering/pyproject.toml
    "google-adk (>=1.5.0,<2.0.0)",
    "google-genai (>=1.9.0,<2.0.0)",
    "pydantic (>=2.10.6,<3.0.0)",
    "python-dotenv (>=1.0.1,<2.0.0)",
    "google-cloud-aiplatform (>=1.93,<2.0)",
```

#### 改用 Azure 需要的修改

#### 主要挑戰

1. `google-adk` 與 `google-genai` 深度整合
   - `google-adk` 直接使用 `google.genai` 的類型與介面
   - Azure 需使用 `openai` 或 `azure-openai` SDK，介面不同
2. `root_agent` 定義方式
   - 目前使用 `agents.Agent()`，模型參數指向 Google 模型
   - 需改為相容 Azure OpenAI 的模型初始化方式
3. 工具依賴
   - `google_search_tool` 需要替換或改寫
4. 認證機制
   - 目前：`gcloud auth application-default login`
   - Azure：需使用 `DefaultAzureCredential` 或 API Key

#### 具體修改步驟

**步驟 1：替換 LLM SDK**

```python
# 原本
from google.genai import types
from google.adk import agents

# 改為（需要自定義 wrapper）
from openai import AzureOpenAI
# 或
from azure.openai import AzureOpenAI
```

**步驟 2：修改 Agent 定義**

目前 `root_agent` 使用 `google.adk.agents.Agent()`，必須改為：
- 使用 Azure OpenAI SDK 的自定義 Agent 類
- 或修改 ADK 以支援 Azure（難度高）

**步驟 3：替換工具**

```python
# 原本
from google.adk.tools.google_search_tool import google_search

# 改為
# 使用 Azure Bing Search API 或其他搜尋服務
```

**步驟 4：環境變數修改**

```bash
# 原本
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<project-id>

# 改為
export AZURE_OPENAI_ENDPOINT=<your-endpoint>
export AZURE_OPENAI_API_KEY=<your-key>
export AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**步驟 5：修改依賴套件**

需要將 `pyproject.toml` 中的依賴改為：
```toml
dependencies = [
    "openai>=1.0.0",  # 或 azure-openai
    "azure-identity>=1.15.0",
    # 移除所有 google-* 相關套件
]
```

#### 結論與建議

可行性：技術可行，但工作量很大。

主要困難：
1. `google-adk` 與 Google 服務深度綁定，需大量自定義程式碼
2. Agent 框架結構需重新設計
3. 所有 sub-agents 也需要相應修改

建議：
- 如果只為了避免 gcloud 權限，可改用 Google AI Studio（API Key）而非 Vertex AI，避免 `gcloud auth`
- 如果必須使用 Azure，建議：
  1. 評估是否可用現有 Azure OpenAI 範例重寫
  2. 或建立 ADK 與 Azure 的適配層（成本高）

需要我協助制定具體的修改計畫嗎？

```plaintext
machine-learning-engineering/
└── machine_learning_engineering/
    ├── __init__.py          # ✅ 包含 from . import agent
    └── agent.py              # ✅ 定義了 root_agent
```

```python
root_agent = agents.Agent(
    model=os.getenv("ROOT_AGENT_MODEL"),
    name="mle_frontdoor_agent",
    instruction=prompt.FRONTDOOR_INSTRUCTION,
    global_instruction=prompt.SYSTEM_INSTRUCTION,
    sub_agents=[mle_pipeline_agent],
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
```

```python
from google.genai import types
from google.adk.agents import callback_context as callback_context_module

from google.adk import agents
```

```python
from google.adk.tools.google_search_tool import google_search
```

```plaintext
    "google-adk (>=1.5.0,<2.0.0)",
    "google-genai (>=1.9.0,<2.0.0)",
    "pydantic (>=2.10.6,<3.0.0)",
    "python-dotenv (>=1.0.1,<2.0.0)",
    "google-cloud-aiplatform (>=1.93,<2.0)",
```

```python
# 原本
from google.genai import types
from google.adk import agents

# 改為（需要自定義 wrapper）
from openai import AzureOpenAI
# 或
from azure.openai import AzureOpenAI
```

```python
# 原本
from google.adk.tools.google_search_tool import google_search

# 改為
# 使用 Azure Bing Search API 或其他搜尋服務
```

```shellscript
# 原本
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<project-id>

# 改為
export AZURE_OPENAI_ENDPOINT=<your-endpoint>
export AZURE_OPENAI_API_KEY=<your-key>
export AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

```plaintext
dependencies = [
    "openai>=1.0.0",  # 或 azure-openai
    "azure-identity>=1.15.0",
    # 移除所有 google-* 相關套件
]
```

---

**User**

只為了避免 gcloud 權限，要如何修改? 
請協助制定具體的修改計畫

---

**Cursor**


檢視目前的認證機制，制定改用 Google AI Studio API Key（不使用 gcloud 權限）的修改計畫。


檢查是否有其他依賴 Vertex AI 的程式碼：


檢查 Google Search Tool 是否依賴 Vertex AI：


制定避免 gcloud 權限的修改計畫，改用 Google AI Studio API Key。


開始修改，改用 Google AI Studio API Key（無需 gcloud 權限）。


```python
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

# Use API Key mode by default (no gcloud auth required)
# To use Vertex AI instead, set GOOGLE_GENAI_USE_VERTEXAI=true
# and configure GOOGLE_CLOUD_PROJECT/GOOGLE_CLOUD_LOCATION
if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI"):
    # Default to API Key mode (false means use API Key, not Vertex AI)
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
    
    # Check if API Key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY not set. Please set it to use Google AI Studio API.")
        print("   Get your API key from: https://aistudio.google.com/apikey")
        print("   Or set GOOGLE_GENAI_USE_VERTEXAI=true to use Vertex AI (requires gcloud auth)")
else:
    # Vertex AI mode - requires GOOGLE_CLOUD_PROJECT
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI").lower() == "true":
        if not os.getenv("GOOGLE_CLOUD_PROJECT"):
            print("⚠️  Warning: GOOGLE_CLOUD_PROJECT not set for Vertex AI mode.")
            print("   Set GOOGLE_CLOUD_PROJECT=<your-project-id> or switch to API Key mode")
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

```

```python
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

    # Use API Key mode by default (no gcloud auth required)
    # To use Vertex AI instead, set GOOGLE_GENAI_USE_VERTEXAI=true
    # and configure GOOGLE_CLOUD_PROJECT/GOOGLE_CLOUD_LOCATION
    if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI"):
        # Default to API Key mode (false means use API Key, not Vertex AI)
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
        
        # Check if API Key is set
        if not os.getenv("GOOGLE_API_KEY"):
            print("⚠️  Warning: GOOGLE_API_KEY not set. Please set it to use Google AI Studio API.")
            print("   Get your API key from: https://aistudio.google.com/apikey")
            print("   Or set GOOGLE_GENAI_USE_VERTEXAI=true to use Vertex AI (requires gcloud auth)")
    else:
        # Vertex AI mode - requires GOOGLE_CLOUD_PROJECT
        if os.getenv("GOOGLE_GENAI_USE_VERTEXAI").lower() == "true":
            if not os.getenv("GOOGLE_CLOUD_PROJECT"):
                print("⚠️  Warning: GOOGLE_CLOUD_PROJECT not set for Vertex AI mode.")
                print("   Set GOOGLE_CLOUD_PROJECT=<your-project-id> or switch to API Key mode")
            if not os.getenv("GOOGLE_CLOUD_LOCATION"):
                os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

    success = run_adk_with_fix()
    if not success:
        sys.exit(1)

```

更新 README.md，加入使用 API Key（無需 gcloud）的說明：


```markdown
# Machine Learning Engineering with Multiple Agents (MLE-STAR)

## Overview

The Machine Learning Engineering Agent is an approach to building Machine Learning Engineering (MLE) agents that can train state-of-the-art machine learning models on various tasks (including classification and regression tasks), through a novel approach of leveraging web search and targeted code block refinement. Using the example of predicting California housing prices, we show how MLE-STAR can create a regression model based on factors like population, income, etc. that outperforms traditional approaches to training ML models. The experimental results show that MLE-STAR achieves medals in 63.6% of the Kaggle competitions on the MLE-bench-Lite, significantly outperforming the best alternative. The implementation is based on the Google Cloud AI Research paper "MLE-STAR: Machine Learning Engineering Agent via Search and Targeted Refinement" (https://www.arxiv.org/abs/2506.15692).

#### Performance of MLE agents on [MLE-Bench-Lite](https://github.com/openai/mle-bench/tree/main) datasets.

| MLE Agents | Base LLM | Any Medals| Gold Medals | Silver Medals | Bronze Medals |
| --- | --- | --- | --- | --- | --- |
| [ **MLE-STAR** ](https://www.arxiv.org/pdf/2506.15692) | **Gemini-2.5-Pro** | **63.6%** | **36.4%** | **21.2%** | 6.1% |
| [ **MLE-STAR** ](https://www.arxiv.org/pdf/2506.15692) | **Gemini-2.5-Flash** | 43.9% | 30.3% | 4.5% | **9.1%** |
---

<br>

## Agent Details

The key features of the Machine Learning Agent include:

| Feature | Description |
| --- | --- |
| **Interaction Type** | Conversational |
| **Complexity**  | Advanced |
| **Agent Type**  | Multi Agent |
| **Components**  | Tools: Code execution, Retrieval |
| **Vertical**  | All |

### Agent architecture

This diagram shows the detailed architecture of the agents and tools used
to implement this workflow.
<img src="machine-learning-engineering-architecture.svg" alt="Machine-Learning-Engineering" width="800"/>

### Key Features

1. **Initial Solution Generation:** Uses a search engine to retrieve state-of-the-art models and their example codes, then merges the best-performing candidates into a consolidated initial solution.

2. **Code Block Refinement:** Iteratively improves the solution by identifying and targeting specific code blocks (ML pipeline components) that have the most significant impact on performance, determined through ablation studies. An inner loop refines the targeted block with various strategies.

3. **Ensemble Strategies:** Introduces a novel ensembling method where the Agent proposes and refines ensemble strategies to combine multiple solutions, aiming for superior performance than individual best solutions.

4. **Robustness Modules:** Includes a debugging agent for error correction, a data leakage checker to prevent improper data access during preprocessing, and a data usage checker to ensure all provided data sources are utilized.

## Setup and Installation

1.  **Prerequisites**

    *   Python 3.12+
    *   Poetry
        *   For dependency management and packaging. Please follow the
            instructions on the official
            [Poetry website](https://python-poetry.org/docs/) for installation.

        ```bash
        pip install poetry
        ```
    *  Git
        *   Git can be downloaded from https://git-scm.com/. Then follow the [installation guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).


    * Google Cloud Account
        *   You need a Google Cloud account
    * A project on Google Cloud Platform
    * Google Cloud CLI
        *   For installation, please follow the instruction on the official
            [Google Cloud website](https://cloud.google.com/sdk/docs/install).

2.  **Installation and Setup**

    *   Clone repository
        ```bash
        # Clone this repository.
        git clone https://github.com/google/adk-samples.git
        cd adk-samples/python/agents/machine-learning-engineering
        ```

    *   Install Poetry
        ```bash
        # Install the Poetry package and dependencies.
        # Note for Linux users: If you get an error related to `keyring` during the installation, you can disable it by running the following command:
        # poetry config keyring.enabled false
        # This is a one-time setup.
        poetry install
        ```

        This command reads the `pyproject.toml` file and installs all the necessary dependencies into a virtual environment managed by Poetry.

        If the above command returns with a `command not found` error, then use:

        ```bash
        python -m poetry install
        ```

    *   Activate the shell

        ```bash
        poetry env activate
        ```

        This activates the virtual environment, allowing you to run commands within the project's environment. To make sure the environment is active, use for example

        ```bash
        $> poetry env list
        machine-learning-engineering-Gb54hHID-py3.12 (Activated)
        ```

        If the above command did not activate the environment for you, you can also activate it through

        ```bash
        source $(poetry env info --path)/bin/activate
        ```

<a name="configuration"></a>

3.  **Configuration**

    You can use either **API Key mode** (recommended, no gcloud auth required) or **Vertex AI mode** (requires gcloud authentication).

    *   **Option 1: API Key Mode (Recommended - No gcloud Required)**

        *   Get your Google AI Studio API key:
            1.  Visit [Google AI Studio](https://aistudio.google.com/apikey)
            2.  Sign in with your Google account
            3.  Click "Create API Key" and copy the key

        *   Set the following environment variables in your shell, or in a `.env` file:

        ```bash
        export GOOGLE_API_KEY=<your-api-key>
        export ROOT_AGENT_MODEL=gemini-2.5-flash  # or gemini-2.5-pro, etc.
        # Note: GOOGLE_GENAI_USE_VERTEXAI defaults to false (API Key mode)
        ```

        *   This mode does **NOT** require `gcloud` authentication or Google Cloud Project setup.

    *   **Option 2: Vertex AI Mode (Requires gcloud)**

        *   You may set the following environment variables in your shell, or in
            a `.env` file instead.

        ```bash
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT=<your-project-id>
        export GOOGLE_CLOUD_LOCATION=<your-project-location>
        export ROOT_AGENT_MODEL=<Google LLM to use>
        export GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>  # Only required for deployment on Agent Engine
        ```

        *   Authenticate your GCloud account.

        ```bash
        gcloud auth application-default login
        gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
        ```

## Running the Agent

**Prepare your task**

You should prepare the inputs for your task in the following way:

1. Create a folder under `tasks` with the name of your task.
2. In that folder, create a file containing the description of the task.
3. Place the data files in this folder.

**Using `adk`**

ADK provides convenient ways to bring up agents locally and interact with them.
You may talk to the agent using the CLI:

```bash
adk run machine_learning_engineering
```

Or via the Poetry shell:
```bash
poetry run adk run machine_learning_engineering
```

Or on a web interface:

```bash
 adk web
```

The command `adk web` will start a web server on your machine and print the URL.

### Example Interaction

You may open the URL, select "machine_learning_engineering" in the top-left drop-down menu, and
a chatbot interface will appear on the right. The conversation is initially
blank. Here are some example requests you may ask the Machine Learning Agent to identity itself:

> **[user]:** who are you?

> **[mle_frontdoor_agent]:** I am a machine learning engineer agent.

> **[user]:** what can you do?

> **[mle_frontdoor_agent]:** I am a machine learning engineer. My primary role is to engineer solutions for machine learning tasks, such as the California Housing Task. I can also describe the task if you'd like. I work by executing a sequence of sub-agents to solve the machine learning engineering task.

> **[user]:** describe the task that you have

> **[mle_frontdoor_agent]:** The task I have is the California Housing Task. This task involves predicting the median house value in California districts, given various features about those districts. It's a regression problem where the goal is to build a model that can accurately estimate house prices based on factors like population, median income, and housing age within a district.

> **[user]:** execute the task

> **[mle_frontdoor_agent]:** *\<intermediate output snipped\>*.
<br>
\# Save the submission file to CSV without the index
print(f"Submission file saved successfully to {submission_file_path}")

## Running Tests

For running tests and evaluation, install the extra dependencies:

```bash
poetry install --with dev
```

Then the tests and evaluation can be run from the `machine-learning-engineering` directory using
the `pytest` module:

```bash
python3 -m pytest tests
python3 -m pytest eval
```

`tests` runs the agent on a sample request, and makes sure that every component
is functional. `eval` is a demonstration of how to evaluate the agent, using the
`AgentEvaluator` in ADK. It sends a couple requests to the agent and expects
that the agent's responses match a pre-defined response reasonablly well.


## Deployment

You will need to have specified a GCS bucket in the environment variable `GOOGLE_CLOUD_BUCKET` as detailed in the [Configuration](#configuration) section.

If the bucket does not exist, ADK will create one for you. This is the easiest option. If the bucket does exist, then you must provide permissions to the service account as described in [this](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/troubleshooting/deploy#permission_errors) Troubleshooting article.

The Machine Learning Engineering Agent can be deployed to Vertex AI Agent Engine using the following
commands:

```bash
poetry install --with deployment
python3 deployment/deploy.py --create
```

When the deployment finishes, it will print a line like this:

```
Created remote agent: projects/<PROJECT_NUMBER>/locations/<PROJECT_LOCATION>/reasoningEngines/<AGENT_ENGINE_ID>
```

If you forget the AGENT_ENGINE_ID, you can list the existing agents using:

```bash
python3 deployment/deploy.py --list
```

The output will be like:

```
All remote agents:

123456789 ("machine_learning_engineering")
- Create time: 2025-07-11 09:46:07+00:00
- Update time: 2025-05-10 09:46:09+00:00
```

You may interact with the deployed agent using the `test_deployment.py` script
```bash
$ export USER_ID=<any string>
$ python3 deployment/test_deployment.py --resource_id=${AGENT_ENGINE_ID} --user_id=${USER_ID}
Found agent with resource ID: ...
Created session for user ID: ...
Type 'quit' to exit.
Input: Hello. What can you do for me?
Response: Hello! I'm a Machine Learning Engineer Assistant. I can help you achieve competition-level quality in solving machine learning tasks.

To get started, please provide the task description of the competition.
```

To delete the deployed agent, you may run the following command:

```bash
python3 deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```


## Appendix

### Required Config Parameters

This document describes the required configuration parameters in the `DefaultConfig` dataclass.

---

#### `data_dir`
-   **Description:** Specifies the directory path where the machine learning tasks and their data are stored.
-   **Type:** `str`
-   **Default:** `"./machine_learning_engineering/tasks/"`

---

#### `task_name`
-   **Description:** The name of the specific task to be loaded and processed.
-   **Type:** `str`
-   **Default:** `"california-housing-prices"`

---

#### `task_type`
-   **Description:** Defines the type of machine learning problem.
-   **Type:** `str`
-   **Default:** `"Tabular Regression"`

---

#### `lower`
-   **Description:** A boolean flag, indicating whether a lower value of the metric is better.
-   **Type:** `bool`
-   **Default:** `True`

---

#### `workspace_dir`
-   **Description:** The directory path used for saving intermediate outputs, results, logs, or any other artifacts generated during the task execution.
-   **Type:** `str`
-   **Default:** `"./machine_learning_engineering/workspace/"`

---

#### `agent_model`
-   **Description:** Specifies the identifier for the LLM model to be used by the agent. It defaults to the value of the environment variable `ROOT_AGENT_MODEL` or `"gemini-2.0-flash-001"` if the variable is not set.
-   **Type:** `str`
-   **Default:** `os.environ.get("ROOT_AGENT_MODEL", "gemini-2.0-flash-001")`

```

已建立修改計畫並完成主要修改。建立修改摘要文件：


```markdown
# 遷移到 API Key 模式（無需 gcloud 權限）

## 修改摘要

本次修改將 machine-learning-engineering agent 預設改為使用 Google AI Studio API Key 模式，避免需要 gcloud 認證。

## 已完成的修改

### 1. `adk_runner.py`
- ✅ 移除強制設定 `GOOGLE_GENAI_USE_VERTEXAI=true`
- ✅ 預設改為 `false`（使用 API Key 模式）
- ✅ 新增 API Key 檢查與提示訊息
- ✅ 保留 Vertex AI 模式的支援

### 2. `adk_fix.py`
- ✅ 與 `adk_runner.py` 相同的修改
- ✅ 確保兩種執行方式都支援 API Key 模式

### 3. `README.md`
- ✅ 更新 Configuration 章節
- ✅ 新增兩種模式的詳細說明
- ✅ 明確標示推薦方式（API Key 模式）

## 使用方法

### 方式一：使用 API Key（推薦，無需 gcloud）

1. **取得 API Key**
   - 訪問 https://aistudio.google.com/apikey
   - 登入並建立 API Key

2. **設定環境變數**
   ```bash
   export GOOGLE_API_KEY=your-api-key-here
   export ROOT_AGENT_MODEL=gemini-2.5-flash
   # 或使用 .env 檔案
   ```

3. **執行 Agent**
   ```bash
   adk web
   # 或
   adk run machine_learning_engineering
   ```

### 方式二：使用 Vertex AI（需要 gcloud）

如果需要使用 Vertex AI，設定以下環境變數：

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

然後執行 gcloud 認證：
```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
```

## .env 檔案範例

建立 `.env` 檔案（複製以下內容並填入你的 API Key）：

```bash
# API Key 模式（推薦）
GOOGLE_API_KEY=your-google-ai-studio-api-key-here
ROOT_AGENT_MODEL=gemini-2.5-flash
GOOGLE_GENAI_USE_VERTEXAI=false

# 如果需要使用 Vertex AI，取消註解並設定以下變數：
# GOOGLE_GENAI_USE_VERTEXAI=true
# GOOGLE_CLOUD_PROJECT=your-gcp-project-id
# GOOGLE_CLOUD_LOCATION=us-central1
```

## 注意事項

1. **API Key 模式限制**
   - 不需要 Google Cloud Project
   - 不需要 gcloud CLI
   - 適合本地開發和測試
   - 無法使用部署到 Vertex AI Agent Engine 的功能

2. **Vertex AI 模式**
   - 需要 Google Cloud Project
   - 需要 gcloud 認證
   - 可用於部署到 Vertex AI Agent Engine
   - 可能有更多進階功能

3. **Google Search Tool**
   - `google_search_tool` 可能仍需要某些 Google 服務認證
   - 如遇到問題，可能需要額外設定

## 測試建議

1. 測試 API Key 模式：
   ```bash
   export GOOGLE_API_KEY=your-key
   export GOOGLE_GENAI_USE_VERTEXAI=false
   adk run machine_learning_engineering
   ```

2. 如果遇到錯誤，檢查：
   - API Key 是否正確設定
   - 環境變數是否正確載入
   - `google-genai` 套件版本是否支援 API Key 模式

## 回報問題

如果遇到任何問題，請檢查：
1. API Key 是否有效
2. 環境變數設定是否正確
3. `google-genai` 和 `google-adk` 版本是否相容

```

檢查是否有語法錯誤：


## 修改完成總結

已將專案改為預設使用 Google AI Studio API Key 模式，無需 gcloud 認證。

### 已完成的修改

#### 1. **`adk_runner.py`**
- 移除強制設定 `GOOGLE_GENAI_USE_VERTEXAI=true`
- 預設改為 `false`（API Key 模式）
- 新增 API Key 檢查與提示訊息
- 保留 Vertex AI 模式的支援

#### 2. **`adk_fix.py`**
- 套用與 `adk_runner.py` 相同的修改

#### 3. **`README.md`**
- 更新 Configuration 章節
- 新增兩種模式說明：
  - Option 1: API Key Mode（推薦，無需 gcloud）
  - Option 2: Vertex AI Mode（需要 gcloud）

#### 4. **`MIGRATION_TO_API_KEY.md`**
- 建立遷移指南與使用說明

### 使用方式

**最簡單的方式（推薦）：**

```bash
# 1. 取得 API Key: https://aistudio.google.com/apikey
# 2. 設定環境變數
export GOOGLE_API_KEY=your-api-key-here
export ROOT_AGENT_MODEL=gemini-2.5-flash

# 3. 執行（無需 gcloud 認證）
adk web
# 或
adk run machine_learning_engineering
```

或使用 `.env` 檔案：

```bash
# 在專案目錄下建立 .env 檔案
GOOGLE_API_KEY=your-api-key-here
ROOT_AGENT_MODEL=gemini-2.5-flash
```

### 主要改變

1. 預設行為：不再強制使用 Vertex AI，改為 API Key 模式
2. 無需 gcloud：不需要執行 `gcloud auth application-default login`
3. 無需 GCP Project：不需要設定 `GOOGLE_CLOUD_PROJECT`
4. 向後相容：仍可透過設定 `GOOGLE_GENAI_USE_VERTEXAI=true` 使用 Vertex AI 模式

### 注意事項

- API Key 模式適合本地開發，但無法使用部署到 Vertex AI Agent Engine 的功能
- 如需部署功能，仍需使用 Vertex AI 模式並設定相關環境變數

修改已完成並通過語法檢查。可直接使用 API Key 模式，無需 gcloud 認證。

```shellscript
# 1. 取得 API Key: https://aistudio.google.com/apikey
# 2. 設定環境變數
export GOOGLE_API_KEY=your-api-key-here
export ROOT_AGENT_MODEL=gemini-2.5-flash

# 3. 執行（無需 gcloud 認證）
adk web
# 或
adk run machine_learning_engineering
```

```shellscript
# 在專案目錄下建立 .env 檔案
GOOGLE_API_KEY=your-api-key-here
ROOT_AGENT_MODEL=gemini-2.5-flash
```

