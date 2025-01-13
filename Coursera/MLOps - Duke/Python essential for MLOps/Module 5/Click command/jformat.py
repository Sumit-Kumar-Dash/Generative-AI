''' 
Click: A Python package for building command line interfaces.
 Now by adding path in click, Click is going to recognize that in the terminal and 
 then going to pass it as a parameter here, as argument here to the main function. 
 Now instead of using sys.argv and all of that stuff in main(), we're just going to comment that's it. 
 We no longer need to use the sys modules as well
'''
import json
import click

def formatter(string, sort_keys=True, indent=4):
    # load incoming string into JSON
    loaded_json = json. loads(string)
    # dump as string
    return json.dumps(loaded_json, sort_keys=sort_keys, indent=indent)

@click.command()
@click.argument('path',type=click.Path(exists=True)) # it tells hey we're going to pass an argument and this has to be a path and it needs to exist.
@click.option('--sort','-s',is_flag=True) 
def main(path,sort):
    with open(path, 'r') as _f:
        print(    formatter(_f.read(), sort_keys=True) )

if __name__ == '__main__':
    main()
     # run below command on terminal: 
     # python3 .\jformat.py examples.json
     # python3 .\jformat.py --sort examples.json