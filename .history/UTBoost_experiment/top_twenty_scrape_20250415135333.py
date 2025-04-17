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

# Define the directory containing the JSON files
evaluation_dir = "../evaluation/verified"

# Initialize a dictionary to store the patches for each agent
patches = {}

# Iterate through the top 20 agents and get the patches from all_preds.json
for agent in TOP_AGENTS:
    # Construct the path to the all_preds.json file
    json_file = os.path.join(evaluation_dir, agent, "all_preds.json")   

    # Check if the file exists
    if os.path.exists(json_file):
        # Read the JSONL file line by line
        with open(json_file, 'r') as f:
            agent_patches = {}
            for line in f:
                data = json.loads(line)
                instance_id = data.get('instance_id')
                patch = data.get('model_patch')
                if instance_id and patch:
                    agent_patches[instance_id] = patch
            
            # Add the agent's patches to the main dictionary
            patches[agent] = agent_patches

# Print the patches for each agent
for agent, agent_patches in patches.items():
    print(f"\nAgent: {agent}")
    for instance_id, patch in agent_patches.items():
        print(f"Instance: {instance_id}")
        print(f"Patch: {patch}\n")





