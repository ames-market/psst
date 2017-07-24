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



