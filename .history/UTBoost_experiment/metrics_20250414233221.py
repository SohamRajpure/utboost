def generate_validation_report(results: List[TestResult]) -> str:
    report = ["UTBoost Validation Report"]
    for res in results:
        status = "PASS" if res['equivalent'] else "FAIL"
        report.append(f"{res['test_case']}: {status}")
        if res['diff']:
            report.append(f"Divergence: {res['diff']}")
    return '\n'.join(report)
