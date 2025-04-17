#Use GPT-4o to generate test cases for the given patch

import openai   
from typing import List, Tuple

class TestGenerator:
    def __init__(self, api_key: str):
        self.llm_client = openai.OpenAI(api_key=api_key)

    def generate_test_cases(self, context_window: str, issue_desc: str) -> List[str]:
        prompt = f"""Generate unit tests for Python function considering:
        {issue_desc}
        Current code context:
        {context_window}
        Include necessary imports and setup"""
        return self.llm_client.generate(prompt, temperature=0.8)


    def get_context_window(file_path: str, target_lines: Tuple[int,int], window_size=10) -> str:
        with open(file_path) as f:
            lines = f.readlines()
        start = max(0, target_lines[0] - window_size)
        end = min(len(lines), target_lines[1] + window_size)
        return ''.join(lines[start:end])
