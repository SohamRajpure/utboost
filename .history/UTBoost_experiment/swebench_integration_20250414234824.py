class SWEBenchAdapter:
    def __init__(self, swe_harness):
        self.harness = swe_harness
    
    def evaluate_patch(self, patch_file: Path) -> Dict[str, Any]:
        result = self.harness.apply_and_test(patch_file)
        return {
            'original_tests': result.base_results,
            'augmented_tests': self.run_augmented_tests(patch_file)
        }
