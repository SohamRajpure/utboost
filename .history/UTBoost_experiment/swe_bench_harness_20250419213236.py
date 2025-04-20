# After generating UTBoost tests, append to existing test suite
def inject_tests(task_instance, utboost_tests):
    test_file = Path(task_instance["test_file"])
    with open(test_file, "a") as f:
        f.write("\n\n# UTBoost Generated Tests\n")
        f.write(utboost_tests)
    return test_file
