"""
Run all financial engine tests.

Usage:
    python run_tests.py
    python run_tests.py -v          # verbose
    python run_tests.py -k test_    # filter by name
"""

import sys
import subprocess

def main():
    args = sys.argv[1:]
    cmd = [sys.executable, "-m", "pytest", "tests/test_calculations.py", "-v"] + args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=__import__("os").path.dirname(__file__))
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
