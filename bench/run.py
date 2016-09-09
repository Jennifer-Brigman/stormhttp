import os
import sys

if __name__ == "__main__":
    benchmark_directory = os.path.realpath(os.path.dirname(__file__))
    python_executable = "/usr/bin/env python3.5"
    sys.stdout.write("Running all benchmarks ...\n".format(benchmark_directory))

    for root, _, benchmarks in os.walk(benchmark_directory):
        if root != benchmark_directory:
            benchmark_name = os.path.basename(root)
            if benchmark_name == "__pycache__":
                continue
            sys.stdout.write("  Running benchmark: {}\n".format(benchmark_name))
            for benchmark in benchmarks:
                if benchmark == "__init__.py" or not benchmark.endswith(".py"):
                    continue
                sys.stdout.write("    Running implementation: {} ... ".format(benchmark))
                sys.stdout.flush()
                os.system("{} {}".format(python_executable, os.path.join(root, benchmark)))
                sys.stdout.write("\n")


