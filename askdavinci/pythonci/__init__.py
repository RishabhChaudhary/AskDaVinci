"""Python CI Module"""
import subprocess as sp
from shutil import which


def format_code():
    """Format Code"""
    print("====| Format: Format Project Code")
    print("====| Format: Rnning Black")
    if which("black"):
        sp.check_call("black .", shell=True)
    else:
        print("Option tool black is not installed")

    print("====| Running Isort")
    sp.check_call("isort .", shell=True)
