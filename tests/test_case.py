import pytest as pt

from psst.case.case import Case


@pt.fixture(scope="module")
def case_default():

    c = Case()

    return c


def test_case(case_default):

    case = case_default

    assert isinstance(case, Case)

    assert list(case.gen.index) == ['GenCo0', 'GenCo1']


def test_unsupported_case():

    with pt.raises(NotImplementedError) as excinfo:
        c = Case(filename='name_of_file.extension')

    assert '.extension' in str(excinfo.value) and 'name_of_file.extension' in str(excinfo.value) and 'please contact the developer' in str(excinfo.value).lower()

