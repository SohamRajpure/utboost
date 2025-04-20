# After generating UTBoost tests, append to existing test suite
def inject_tests(task_instance, utboost_tests):
    """
    Inject UTBoost generated tests into the existing test suite.
    
    Args:
        task_instance: Dictionary containing task information including test_file path
        utboost_tests: String containing the generated test code to inject
        
    Returns:
        Path object pointing to the modified test file
        
    Raises:
        FileNotFoundError: If the test file doesn't exist
        ValueError: If utboost_tests is empty or invalid
        PermissionError: If unable to write to the test file
    """
    if not utboost_tests or not isinstance(utboost_tests, str):
        raise ValueError("utboost_tests must be a non-empty string")
        
    if not task_instance or "test_file" not in task_instance:
        raise ValueError("task_instance must contain 'test_file' key")
        
    test_file = Path(task_instance["test_file"])
    
    if not test_file.exists():
        raise FileNotFoundError(f"Test file not found: {test_file}")
        
    if not test_file.is_file():
        raise ValueError(f"Path is not a file: {test_file}")
        
    try:
        # Read existing content to check for duplicates
        with open(test_file, "r") as f:
            existing_content = f.read()
            
        # Check if tests already exist
        if "# UTBoost Generated Tests" in existing_content:
            print(f"Warning: UTBoost tests already exist in {test_file}")
            return test_file
            
        # Add proper spacing and formatting
        separator = "\n" + "#" * 80 + "\n"
        formatted_tests = f"{separator}# UTBoost Generated Tests{separator}{utboost_tests.strip()}\n"
        
        # Append the tests
        with open(test_file, "a") as f:
            f.write(formatted_tests)
            
        print(f"Successfully injected UTBoost tests into {test_file}")
        return test_file
        
    except PermissionError:
        raise PermissionError(f"Permission denied when writing to {test_file}")
    except Exception as e:
        raise Exception(f"Error injecting tests: {str(e)}")
