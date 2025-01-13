import os
import sys
import json

def formatter(string, sort_keys=True, indent=4):
    # load incoming string into JSON
    loaded_json = json. loads(string)
    # dump as string
    return json.dumps(loaded_json, sort_keys=sort_keys, indent=indent)

def main(path):
    with open(path, 'r') as _f:
        print(formatter(_f. read()))

print(sys.argv) # print whatever sent in the command line
'''
Run this on terminal: python3 .\jformat.py
Output for above print statement: ['.\\jformat.py']

python3 .\jformat.py argument 1 argument 2
o/p: ['.\\jformat.py','argument 1','argument 2']
'''

if __name__== '__main__':
    main(sys.argv[-1]) # Takes the last argument from the command line
'''
run from terminal : python3 jformat.py examples/example.json
o/p : 
{
    "arg": 1,
    "boto": true,
    "zetta": 7
}
'''