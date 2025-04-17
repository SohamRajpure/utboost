#Use GPT-4o to generate test cases for the given patch

import openai   
from typing import List, Tuple
import json
import os

class TestGenerator:
    def __init__(self, api_key: str):
        self.llm_client = openai.OpenAI(api_key=api_key)

    def generate_test_cases(self, context_window: str, issue_desc: str) -> List[str]:
        prompt = f"""Generate unit tests for Python function considering:
        {issue_desc}
        Current code context:
        {context_window}
        Include necessary imports and setup"""
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Generate unit tests"}
            ]
        )
        return response.choices[0].message.content.strip()  
    
    @staticmethod
    def get_context_window(file_path: str, target_lines: Tuple[int,int], window_size=10) -> str:
        with open(file_path) as f:
            lines = f.readlines()
        start = max(0, target_lines[0] - window_size)
        end = min(len(lines), target_lines[1] + window_size)
        return ''.join(lines[start:end])

    @staticmethod
    def read_issue_from_eval_dir(eval_dir: str, agent_name: str, instance_id: str) -> Tuple[str, str]:
        """Read issue description and patch from evaluation directory.
        
        Args:
            eval_dir: Path to evaluation/verified directory
            agent_name: Name of the agent (e.g. '20241213_devlo')
            instance_id: ID of the instance (e.g. 'django__django-13343')
            
        Returns:
            Tuple of (issue_description, patch)
        """
        json_file = os.path.join(eval_dir, agent_name, f"{instance_id}.json")
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Could not find {json_file}")
            
        with open(json_file, 'r') as f:
            data = json.load(f)
            return data.get('issue_description', ''), data.get('patch', '')
