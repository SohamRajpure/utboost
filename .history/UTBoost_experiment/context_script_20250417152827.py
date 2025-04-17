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
        
    def get_llm_response(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Get response from OpenAI's LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            model: The OpenAI model to use (default: gpt-3.5-turbo)
            
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
        
    def process_task(self, task_data: Dict) -> Dict:
        """
        Process a single task through the complete workflow.
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            Dictionary containing all generated context and test case
        """
        # 1. Derive repository information
        repo_info = self.derive_repo_info(task_data)
        
        # 2. Create and process file level localization
        file_prompt = CodebaseAnalyzer.file_level_localization(
            repo_owner=repo_info["repo_owner"],
            repo_name=repo_info["repo_name"],
            issue_description=task_data.get("issue_description", ""),
            test_patch=task_data.get("model_patch", ""),
            github_token=self.github_token
        )
        
        file_response = self.get_llm_response(file_prompt)
        top_files = self.extract_top_files(file_response)
        
        # 3. Create and process function class localization
        func_prompt = CodebaseAnalyzer.function_class_localization(
            repo_owner=repo_info["repo_owner"],
            repo_name=repo_info["repo_name"],
            top_files=top_files,
            issue_desc=task_data.get("issue_description", ""),
            test_patch=task_data.get("model_patch", ""),
            github_token=self.github_token
        )
        func_response = self.get_llm_response(func_prompt)
        
        # 4. Create and process line level localization
        line_prompt = CodebaseAnalyzer.line_level_localization(
            repo_owner=repo_info["repo_owner"],
            repo_name=repo_info["repo_name"],
            target_functions=[func.strip('- ') for func in func_response.split('\n') if func.startswith('- ')],
            issue_desc=task_data.get("issue_description", ""),
            test_patch=task_data.get("model_patch", ""),
            github_token=self.github_token
        )
        line_response = self.get_llm_response(line_prompt)
        
        # 5. Generate test case
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
{task_data}

Original Patch:
{task_data.get('model_patch', '')}

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

def select_task(task_file: str) -> Dict:
    """
    Load tasks and let user select one to process.
    
    Args:
        task_file: Path to the JSON file containing tasks
        
    Returns:
        Selected task information
    """
    with open(task_file, 'r') as f:
        tasks = json.load(f)
        
    if not tasks:
        raise ValueError("No tasks found in the file")
        
    # If tasks is a list, show options
    if isinstance(tasks, list):
        print("\nAvailable tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task.get('task_id', 'Unknown Task')}")
            
        while True:
            try:
                choice = int(input("\nSelect a task number to process: "))
                if 1 <= choice <= len(tasks):
                    return tasks[choice - 1]
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        # If it's a single task object, return it
        return tasks

def main():
    # Get API keys from environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not github_token or not openai_api_key:
        print("""
        Please set your API keys as environment variables:
        
        1. For temporary use in current session:
           export GITHUB_TOKEN='your_github_token'
           export OPENAI_API_KEY='your_openai_api_key'
        
        2. For permanent use, add to ~/.zshrc:
           echo 'export GITHUB_TOKEN="your_github_token"' >> ~/.zshrc
           echo 'export OPENAI_API_KEY="your_openai_api_key"' >> ~/.zshrc
           source ~/.zshrc
        
        3. Or use a password manager/secure note to store the keys
           and set them as environment variables when needed.
        """)
        return
    
    # Initialize context generator
    generator = ContextGenerator(github_token=github_token, openai_api_key=openai_api_key)
    
    try:
        # Process the specific task file
        task_file = "UTBoost_experiment/tasks/sympy__sympy-20916/passed_agent_passes.json"
        print(f"\nProcessing task from: {task_file}")
        
        # Load and process the task
        with open(task_file, 'r') as f:
            tasks = json.load(f)
            
        if not isinstance(tasks, list):
            raise ValueError("Expected a list of tasks in the JSON file")
            
        if not tasks:
            raise ValueError("No tasks found in the file")
            
        # Take the first task
        task_data = tasks[0]
        print(f"\nProcessing task ID: {task_data.get('task_id', 'unknown')}")
        
        # Print task data structure for debugging
        print("\nTask data structure:")
        print(json.dumps(task_data, indent=2))
        
        result = generator.process_task(task_data)
        
        # Save results with task ID in filename
        task_id = task_data.get('task_id', 'sympy-20916')
        output_file = f"task_analysis_results_{task_id}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nAnalysis complete. Results saved to {output_file}")
        
    except Exception as e:
        print(f"\nError processing task: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 