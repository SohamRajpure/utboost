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
evaluation_dir = "../evaluation/verified" #TODO: change this to the correct directory

# Initialize a dictionary to store the patches for each agent
patches = {}

# Iterate through the top 20 agents and get the patches from the JSON files
for agent in TOP_AGENTS:
    # Construct the path to the JSON file
    json_file = os.path.join(evaluation_dir, f"{agent}.json")   

    # Check if the file exists
    if os.path.exists(json_file):
        # Load the JSON file
        with open(json_file, 'r') as f:
            data = json.load(f) 

            # Extract the patch from the JSON file
            patch = data['patch']

            # Add the patch to the dictionary
            patches[agent] = patch      

# Print the patches for each agent
for agent, patch in patches.items():
    print(f"{agent}: {patch}")





