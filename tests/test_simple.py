import pytest


# @pytest.mark.skip
def setup_module(module):
    print("*** setup_module")


# @pytest.mark.skip
def teardown_module(module):
    print("*** teardown_module")


# @pytest.mark.skip
def setup_function(function):
    print("*** setup_function")


# @pytest.mark.skip
def teardown_function(function):
    print("*** teardown_function")


# -- parameterize


def test_1(variant_1):
    assert "injected" in variant_1


# -- fixtures


def test_2(variant_2):
    assert variant_2 == 100


def test_3(variant_2):
    assert variant_2 == 100


def test_4():
    assert True
