"""Demonstration of Machine Learning Engineering Agent using Agent Development Kit"""

import os
import json
from typing import Optional
from google.genai import types
from google.adk.agents import callback_context as callback_context_module

from google.adk import agents
from machine_learning_engineering.sub_agents.initialization import agent as initialization_agent_module
from machine_learning_engineering.sub_agents.refinement import agent as refinement_agent_module
from machine_learning_engineering.sub_agents.ensemble import agent as ensemble_agent_module
from machine_learning_engineering.sub_agents.submission import agent as submission_agent_module

from machine_learning_engineering import prompt


from google.adk.models import llm_response as llm_response_module
from machine_learning_engineering.shared_libraries import common_util


def extract_task_name_from_response(
    callback_context: callback_context_module.CallbackContext,
    llm_response: llm_response_module.LlmResponse,
) -> Optional[llm_response_module.LlmResponse]:
    """Parses the LLM response to find the task_name and sets it in the state."""
    response_text = common_util.get_text_from_response(llm_response).strip()
    if response_text.startswith("task_name:"):
        task_name = response_text.split(":", 1)[1].strip()
        # Remove potential brackets
        if task_name.startswith("[") and task_name.endswith("]"):
            task_name = task_name[1:-1]
        callback_context.state["task_name"] = task_name
        # Return None to signify that the response has been handled and no further action is needed.
        return None
    # If it's a regular chat response, pass it through.
    return llm_response


def save_state(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """Prints the current state of the callback context."""
    workspace_dir = callback_context.state.get("workspace_dir", "")
    task_name = callback_context.state.get("task_name", "")
    if not task_name:
        # Don't save state if no task has been started
        return None
    run_cwd = os.path.join(workspace_dir, task_name)
    # Ensure the directory exists before writing to it
    os.makedirs(run_cwd, exist_ok=True)
    with open(os.path.join(run_cwd, "final_state.json"), "w") as f:
        json.dump(callback_context.state.to_dict(), f, indent=2)
    return None


mle_pipeline_agent = agents.SequentialAgent(
    name="mle_pipeline_agent",
    sub_agents=[
        initialization_agent_module.initialization_agent,
        refinement_agent_module.refinement_agent,
        ensemble_agent_module.ensemble_agent,
        submission_agent_module.submission_agent,
    ],
    description="Executes a sequence of sub-agents for solving the MLE task.",
    after_agent_callback=save_state,
)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = agents.Agent(
    model=os.getenv("ROOT_AGENT_MODEL"),
    name="mle_frontdoor_agent",
    instruction=prompt.FRONTDOOR_INSTRUCTION,
    global_instruction=prompt.SYSTEM_INSTRUCTION,
    sub_agents=[mle_pipeline_agent],
    after_model_callback=extract_task_name_from_response,
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
