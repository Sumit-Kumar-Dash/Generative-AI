
# This function is here for convenience only, in a real-world scenario this function
# would be elsewhere in a package
'''

Class name should start with "Test", eg: TestStrtoInt
Function name should start with "test_" , eg: test_rounds_down

Setup Class: Before any test methods run, pytest will call setup_class. This is intended to set up any state that is shared across tests.
The message "this is setup class" will be printed.

Setup Method: Before each test method, pytest will call setup. This is intended to set up any state that each individual test needs.
The message "this is setup" will be printed.

Teardown Method: After each test method, pytest will call teardown. This is intended to clean up any state that the individual test created.
The message "this is teardown" will be printed after each test method.

Teardown Class: After all test methods have run, pytest will call teardown_class. This is intended to clean up any state that was set up for the entire test class.
The message "this is teardown class" will be printed.
'''

def str_to_int(string):
    """
    Parses a string number into an integer, optionally converting to a float
    and rounding down.
    You can pass "1.1" which returns 1
    ["1"] -> raises RuntimeError
    """
    error_msg = "Unable to convert to integer: '%s'" % str(string)
    try:
        integer = float(string.replace(',', '.'))
    except AttributeError:
        # this might be a integer already, so try to use it, otherwise raise
        # the original exception
        if isinstance(string, (int, float)):
            integer = string
        else:
            raise RuntimeError(error_msg)
    except (TypeError, ValueError):
        raise RuntimeError(error_msg)

    return int(integer)


# tests floats

class TestStrToInt:

    def setup(self):
        print('\nthis is setup')

    def teardown(self):
        print('\nthis is teardown')

    def setup_class(cls):
        print('\nthis is setup class')

    def teardown_class(cls):
        print('\nthis is teardown class')

    def test_rounds_down(self):
        result = str_to_int('1.99')
        assert result == 2

    def test_round_down_lesser_half(self):
        result = str_to_int('1.2')
        assert result == 2
