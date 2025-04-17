class CodebaseAnalyzer:
    def file_localization(self, issue_desc: str) -> List[str]:
        # Uses TF-IDF vectorization to match issue description
        # against file documentation/comments

        return top_n_files

    def function_localization(self, target_files: List[str]) -> Dict[str, List[str]]:
        # Parses AST to identify relevant functions/classes
        return function_map

    def line_localization(self, function_code: str) -> Tuple[int, int]:
        # Uses program slicing to identify critical code ranges
        return (start_line, end_line)

    def file_level_localization(
    repo_path: str,
    issue_description: str,
    test_patch: str,
    n: int = 3
) -> str:
    """
    Implements UTBoost's file-level localization to identify Top-N files
    for test case additions.
    
    Args:
        repo_path: Path to repository root
        issue_description: SWE-Bench issue description
        test_patch: Original test patch content
        n: Number of top files to identify
    
    Returns:
        LLM prompt with structured codebase and localization instructions
    """
    
    # 1. Codebase Tree Construction
    def build_tree(dir_path: str, indent: int = 0) -> str:
        """Builds vertical-aligned tree representation"""
        tree_str = ""
        items = sorted(os.listdir(dir_path))
        for item in items:
            full_path = os.path.join(dir_path, item)
            if os.path.isdir(full_path):
                tree_str += "│   " * indent + f"├── {item}/\n"
                tree_str += build_tree(full_path, indent + 1)
            else:
                tree_str += "│   " * indent + f"├── {item}\n"
        return tree_str

    codebase_tree = build_tree(repo_path)

    # 2. LLM Prompt Construction
    prompt = f"""Analyze this software repository and identify the {n} files most likely 
        to require test case additions based on the issue description and existing test patch.

        Repository Structure:
        {codebase_tree}

        Issue Description:
        {issue_description}

        Existing Test Patch:
        {test_patch}

        Output Requirements:
        1. List {n} full file paths from the repository structure
        2. Order by relevance to the issue
        3. Format as bullet points with explanations
        4. Focus on test files and code under test

        Example Response:
        - sklearn/svm/tests/test_svm.py (Contains SVM test cases similar to the patch)
        - sklearn/svm/base.py (Implements core SVM functionality referenced in issue)
        """

            return prompt