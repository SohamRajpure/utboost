# After generating UTBoost tests, append to existing test suite
def inject_tests(task_instance, utboost_tests):
    test_file = Path(task_instance["test_file"])
    with open(test_file, "a") as f:
        f.write("\n\n# UTBoost Generated Tests\n")
        f.write(utboost_tests)
    return test_file

def process_all_tasks(tasks_dir: str = "UTBoost_experiment/tasks", output_dir: str = "UTBoost_experiment/results"):
    """
    Process all tasks in the tasks directory and generate test cases.
    
    Args:
        tasks_dir: Directory containing task folders
        output_dir: Directory to store results
    """
    from pathlib import Path
    import os
    import json
    from context_script import ContextGenerator
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
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
        """)
        return
    
    # Initialize context generator
    generator = ContextGenerator(github_token=github_token, openai_api_key=openai_api_key)
    
    # Get all task directories
    task_dirs = [d for d in os.listdir(tasks_dir) if os.path.isdir(os.path.join(tasks_dir, d))]
    
    print(f"Found {len(task_dirs)} tasks to process")
    
    # Process each task
    for task_dir in task_dirs:
        try:
            print(f"\nProcessing task: {task_dir}")
            
            # Load task data
            task_file = os.path.join(tasks_dir, task_dir, "passed_agent_passes.json")
            task_data = generator.load_task(task_file)
            
            # Generate test cases
            result = generator.process_task(task_data)
            
            # Save results
            output_file = os.path.join(output_dir, f"{task_dir}_results.json")
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"Successfully processed {task_dir}")
            
        except Exception as e:
            print(f"Error processing task {task_dir}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

if __name__ == "__main__":
    process_all_tasks()
