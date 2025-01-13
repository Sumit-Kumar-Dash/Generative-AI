import pytest
from utils import str_to_bool


def test_yes_is_true():
    result = str_to_bool('yes')
    assert result is True


def test_y_is_true():
    result = str_to_bool('y')
    assert result is True


'''
dont keep any loop like for loop of list for testing multiple values because 
testing will happen for first value of list only
instead pass as parametrize to the function

pytest supports parameterized testing out of the box using the @pytest.mark.parametrize decorator.
pytest uses the @pytest.fixture decorator, which offers more flexibility and can be reused across multiple tests.
'''

@pytest.mark.parametrize('value', ['y', 'yes', '','N'])
def test_is_true(value):
    '''
    for value in ['yes','Y','']:
        result = str_to_bool(value)
        assert ...
    '''
    result = str_to_bool(value)
    assert result is True