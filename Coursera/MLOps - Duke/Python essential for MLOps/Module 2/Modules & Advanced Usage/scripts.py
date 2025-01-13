"""This is a Python script meant to be run from the terminal (or command line)

It uses the 'if _name_' construct at the end of the script to hook into any function.
In this case, it connect to the main() function

This script doesn't do much, it will just report the arguments being passed into the
script. It should serve as a foundation to create a more powerful script"""

import sys

def main(arguments):
    print("This is the main function, and it has access to the following variables:")
    for argument in arguments:
        print(argument)
    print(type(arguments))
    print(arguments)

if _name_ == '_main_':
    main(sys.argv)

""" run this in command line :
    python script.py
    python script.py argument --help -f key=value
"""