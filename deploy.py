import stormhttp
import subprocess
import sys
import os

if __name__ == "__main__":
    if b"* master" not in subprocess.check_output(["git", "branch"]):
        print("ERROR: Switch to master branch to deploy.")
        sys.exit(1)
    os.chdir(os.path.dirname(__file__))
    pypi_deploy = subprocess.check_output(["python", "setup.py", "sdist", "bdist_wheel", "upload"])
    if b"400" in pypi_deploy and b'already exists' in pypi_deploy:
        print("ERROR: Didn't increment __version__.")
        sys.exit(1)
    else:
        os.system("git --tag '{}'".format(stormhttp.__version__))
        os.system("git commit -m 'Deploy version {} to PyPI'".format(stormhttp.__version__))
        os.system("git push --tags")
        sys.exit(0)