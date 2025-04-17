TOP_AGENTS = [
    "20250316_augment_agent_v0", 
    "20250117_wandb_programmer_o1_crosscheck5", 
    "20250206_agentscope", 
    "20250224_tools_claude-3-7-sonnet",
    "20250228_epam-ai-run-claude-3-5-sonnet", 
    "20241221_codestory_midwit_claude-3-5-sonnet_swe-search", 
    "20250203_openhands_4x_scaled",
    "20250110_learn_by_interact_claude3.5", 
    "20241213_devlo", 
    "20241223_emergent", 
    "20241208_gru", 
    "20241212_epam-ai-run-claude-3-5-sonnet",
    "20241202_amazon-q-developer-agent-20241202-dev", 
    "20241108_devlo", 
    "20250120_Bracket", 
    "20241029_OpenHands-CodeAct-2.1-sonnet-20241022",
    "20241212_google_jules_gemini_2.0_flash_experimental", 
    "20241125_enginelabs", 
    "20241202_agentless-1.5_claude-3.5-sonnet-20241022"
]

#These are the top 20 agents on the leaderboard as of 4/15/2025.
# Extract generated patches from the top 20 agent's /evluation/verified directory

import os
import json
from pathlib import Path

# Define the directory containing the JSON files
evaluation_dir = "../evaluation/verified"

# Create a directory to store task-specific information if it doesn't exist
tasks_dir = "tasks"
os.makedirs(tasks_dir, exist_ok=True)

# Process each agent
for agent in TOP_AGENTS:
    # Paths to the agent's files
    all_preds_path = os.path.join(evaluation_dir, agent, "all_preds.json")
    results_path = os.path.join(evaluation_dir, agent, "results", "results.json")
    
    # Skip if either file doesn't exist
    if not os.path.exists(all_preds_path) or not os.path.exists(results_path):
        print(f"Skipping {agent} - missing required files")
        continue
    
    # Load the results to get resolved tasks
    with open(results_path, 'r') as f:
        results = json.load(f)
        resolved_tasks = set(results.get("resolved", []))
    
    # Process the first 20 tasks from all_preds.json
    with open(all_preds_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= 10:  # Only process first 20 tasks
                break
                
            data = json.loads(line)
            instance_id = data.get('instance_id')
            model_name = data.get('model_name_or_path')
            model_patch = data.get('model_patch')
            
            if not all([instance_id, model_name, model_patch]):
                continue
                
            # Create task directory if it doesn't exist
            task_dir = os.path.join(tasks_dir, instance_id)
            os.makedirs(task_dir, exist_ok=True)
            
            # Path to the task's passed_agent_passes.json
            passes_file = os.path.join(task_dir, "passed_agent_passes.json")
            
            # Initialize or load existing passes
            if os.path.exists(passes_file):
                with open(passes_file, 'r') as pf:
                    passes = json.load(pf)
            else:
                passes = []
            
            # If this agent passed the task, add their info
            if instance_id in resolved_tasks:
                new_pass = {
                    "model_name_or_path": model_name,
                    "model_patch": model_patch
                }
                
                # Only add if not already present
                if new_pass not in passes:
                    passes.append(new_pass)
                    
                    # Save updated passes
                    with open(passes_file, 'w') as pf:
                        json.dump(passes, pf, indent=2)
                    
                    print(f"Added pass for {agent} on task {instance_id}")





