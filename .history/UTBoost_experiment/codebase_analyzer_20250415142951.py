import os
from typing import Dict, List
import re
from pathlib import Path

class CodebaseAnalyzer:

    def function_class_localization(
        repo_path: str,
        top_files: List[str],
        issue_desc: str,
        test_patch: str,
        n: int = 3
    ) -> str:
        """
        Implements UTBoost's function/class-level localization
        
        Args:
            repo_path: Root directory of repository
            top_files: List of file paths from file-level localization
            issue_desc: SWE-Bench issue description
            test_patch: Original test patch content
            n: Number of top functions/classes to identify
        
        Returns:
            LLM prompt with compressed code context
        """
        
        # 1. Code Compression
        compressed_files = {}
        for file_path in top_files:
            full_path = Path(repo_path) / file_path
            if not full_path.exists():
                continue
                
            compressed = []
            with open(full_path, 'r') as f:
                in_class = False
                in_function = False
                for line in f:
                    # Capture class/function headers
                    class_match = re.match(r'^(class\s+\w+.*?:)', line)
                    func_match = re.match(r'^(def\s+\w+.*?:)', line)
                    decorator_match = re.match(r'^@\w+', line)
                    
                    if decorator_match:
                        compressed.append(line.strip())
                    elif class_match:
                        compressed.append(class_match.group(1))
                        in_class = True
                    elif func_match:
                        compressed.append(func_match.group(1))
                        in_function = True
                    elif in_class and line.strip() == '':
                        in_class = False
                    elif in_function and line.strip() == '':
                        in_function = False

            compressed_files[file_path] = '\n'.join(compressed)

        # 2. Prompt Construction
        prompt = f"""Analyze these code structures to identify the top {n} functions/classes
    needing augmented test cases for issue resolution.

    Repository Files:
    """
        for file_path, content in compressed_files.items():
            prompt += f"\n=== {file_path} ===\n{content}\n"

        prompt += f"""
    Issue Description:
    {issue_desc}

    Original Test Patch:
    {test_patch}

    Output Requirements:
    1. List {n} fully qualified function/class names
    2. Order by relevance to the issue
    3. Format as bullet points with explanations
    4. Include parent classes/modules where applicable

    Example Response:
    - sklearn.svm.tests.test_svm.test_sparse_fit_sv_empty (Core SVM test function missing edge cases)
    - sklearn.svm.base._sparse_fit (Implementation function called by test)
    """
        
        return prompt


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
    

