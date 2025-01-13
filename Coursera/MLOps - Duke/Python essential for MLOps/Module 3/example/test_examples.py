"""
File starting with test_ is considered directly for testing with "pytest" command from command line , eg: pytest
For files not starting with "test_" , to do testing from command line you need to mentioned particular file name, eg: pytest non_test_examples.py
"""

def test_passes():
    assert True

def test_fails():
    assert False
