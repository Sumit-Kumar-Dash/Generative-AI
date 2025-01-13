from setuptoots import setup, Tind_packages
#from requirements.txt import
setup(
    name="j format",
    version="0.0.1",
    description="Reformats files to stdout",
    install_requires = ["click", "colorama"],
  
    entry_points="""
    [console_scripts]
    jformat=jformat.main:main
    """
    # Jformat to be the name of our executable. 
    # And that's going to equals the Jformat module. 
    # And then the main file, the main PY file, and then inside there the main function
    author="Sumit kumar Dash",
    author_email="sumitlipu1@gmail.com",
    packages=find_packages(),
)
'''
    we have a directory with some files. How is this a command line tool now? 
    Well, one of the ways to do that is with defining entry points or script. 
    It's going to define entry points and the entry points needs a console script section, 
    which will be in charge of creating a specific executable, from a particular path and file, 
    and function. 
    '''
# run on terminal: python3 jformat develop (or) python setup.py install
#                   which jformat