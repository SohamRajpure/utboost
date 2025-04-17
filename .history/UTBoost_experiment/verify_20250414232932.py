#Intramorphic testing


class TestOracle:
    def validate_patches(self, gold_patch: str, candidate_patch: str) -> bool:
        gold_results = self.run_tests(gold_patch)
        candidate_results = self.run_tests(candidate_patch)
        return self.compare_outputs(gold_results, candidate_results)
