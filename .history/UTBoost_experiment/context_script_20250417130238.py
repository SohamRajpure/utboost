import json
import os
from typing import Dict, List
from openai import OpenAI
from codebase_analyzer import CodebaseAnalyzer

class ContextGenerator:
    def __init__(self, github_token: str = None, openai_api_key: str = None):
        """
        Initialize the context generator with necessary API keys.
        
        Args:
            github_token: GitHub personal access token
            openai_api_key: OpenAI API key
        """
        self.analyzer = CodebaseAnalyzer()
        self.github_token = github_token
        self.client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        
    def load_task(self, task_file: str) -> Dict:
        """
        Load task information from passed_agent_passes.json.
        
        Args:
            task_file: Path to the JSON file containing task information
            
        Returns:
            Dictionary containing task information
        """
        with open(task_file, 'r') as f:
            return json.load(f)
            
    def derive_repo_info(self, task_info: Dict) -> Dict:
        """
        Derive repository information from task info.
        
        Args:
            task_info: Dictionary containing task information
            
        Returns:
            Dictionary containing repository information
        """
        return self.analyzer.derive_repo_info(task_info)
        
    def get_llm_response(self, prompt: str, model: str = "gpt-4") -> str:
        """
        Get response from OpenAI's LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            model: The OpenAI model to use
            
        Returns:
            The LLM's response
        """
        if not self.client:
            raise ValueError("OpenAI API key not provided")
            
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
        
    def extract_top_files(self, llm_response: str) -> List[str]:
        """
        Extract top files from LLM response.
        
        Args:
            llm_response: Response from file level localization
            
        Returns:
            List of top file paths
        """
        # This is a simple implementation - you might want to make it more robust
        files = []
        for line in llm_response.split('\n'):
            if line.startswith('- '):
                file_path = line.split('(')[0].strip('- ').strip()
                files.append(file_path)
        return files
        
    def process_task(self, task_file: str) -> Dict:
        """
        Process a single task through the complete workflow.
        
        Args:
            task_file: Path to the task JSON file
            
        Returns:
            Dictionary containing all generated context and test case
        """
        # 1. Load task information
        task_info = self.load_task(task_file)
        
        # 2. Derive repository information
        repo_info = self.derive_repo_info(task_info)
        
        # 3. Create and process file level localization
        file_prompt = self.analyzer.file_level_localization(
            repo_owner=repo_info["repo_owner"],
            repo_name=repo_info["repo_name"],
            issue_description=task_info.get("issue_description", ""),
            test_patch=task_info.get("model_patch", ""),
            github_token=self.github_token
        )
        file_response = self.get_llm_response(file_prompt)
        top_files = self.extract_top_files(file_response)
        
        # 4. Create and process function class localization
        func_prompt = self.analyzer.function_class_localization(
            repo_owner=repo_info["repo_owner"],
            repo_name=repo_info["repo_name"],
            top_files=top_files,
            issue_desc=task_info.get("issue_description", ""),
            test_patch=task_info.get("model_patch", ""),
            github_token=self.github_token
        )
        func_response = self.get_llm_response(func_prompt)
        
        # 5. Create and process line level localization
        line_prompt = self.analyzer.line_level_localization(
            repo_owner=repo_info["repo_owner"],
            repo_name=repo_info["repo_name"],
            target_functions=[func.strip('- ') for func in func_response.split('\n') if func.startswith('- ')],
            issue_desc=task_info.get("issue_description", ""),
            test_patch=task_info.get("model_patch", ""),
            github_token=self.github_token
        )
        line_response = self.get_llm_response(line_prompt)
        
        # 6. Generate test case
        test_case_prompt = f"""Based on the following information, generate a test case:

Repository Information:
{repo_info}

File Level Analysis:
{file_response}

Function/Class Analysis:
{func_response}

Line Level Analysis:
{line_response}

Task Information:
{task_info}

Original Patch:
{task_info.get('model_patch', '')}

Generate a comprehensive test case that:
1. Tests the identified functionality
2. Includes necessary imports
3. Follows the project's testing conventions
4. Handles edge cases
5. Includes proper documentation
"""
        test_case = self.get_llm_response(test_case_prompt)
        
        return {
            "repository_info": repo_info,
            "file_level_analysis": file_response,
            "function_class_analysis": func_response,
            "line_level_analysis": line_response,
            "test_case": test_case
        }

def main():
    # Get API keys from environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not github_token or not openai_api_key:
        raise ValueError("Please set GITHUB_TOKEN and OPENAI_API_KEY environment variables")
    
    # Initialize context generator
    generator = ContextGenerator(github_token=github_token, openai_api_key=openai_api_key)
    
    # Process tasks
    task_file = "passed_agent_passes.json"  # Update this path as needed
    result = generator.process_task(task_file)
    
    # Save results
    output_file = "task_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Analysis complete. Results saved to {output_file}")

if __name__ == "__main__":
    main() 