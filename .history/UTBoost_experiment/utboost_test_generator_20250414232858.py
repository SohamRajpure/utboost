class TestGenerator:
    def generate_test_cases(self, context_window: str, issue_desc: str) -> List[str]:
        prompt = f"""Generate unit tests for Python function considering:
        {issue_desc}
        Current code context:
        {context_window}
        Include necessary imports and setup"""
        return self.llm_client.generate(prompt, temperature=0.8)
