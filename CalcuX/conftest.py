"""
This module contains test configurations and dynamic test generation for pytest.
"""

import pytest
from decimal import Decimal
from faker import Faker
from calculator.operations import add, subtract, multiply, divide

fake = Faker()

def generate_test_data(num_records):
    """
    Generates test data for calculator operations.
    """
    operation_mappings = {
        'add': add,
        'subtract': subtract,
        'multiply': multiply,
        'divide': divide
    }
    
    for _ in range(num_records):
        a = Decimal(fake.random_number(digits=2))
        b = Decimal(fake.random_number(digits=2)) if _ % 4 != 3 else Decimal(fake.random_number(digits=1))
        operation_name = fake.random_element(elements=list(operation_mappings.keys()))
        operation_func = operation_mappings[operation_name]
        
        if operation_func == divide:
            b = Decimal('1') if b == Decimal('0') else b
        
        try:
            expected = operation_func(a, b)
        except ZeroDivisionError:
            expected = "ZeroDivisionError"
        
        yield a, b, operation_name, operation_func, expected

def pytest_addoption(parser):
    """
    Adds custom pytest options.
    """
    parser.addoption("--num_records", action="store", default=10, type=int, help="Number of test records to generate")

@pytest.fixture
def num_records(request):
    """
    Fixture to retrieve the number of records from pytest command-line options.
    """
    return request.config.getoption("--num_records")

def pytest_generate_tests(metafunc):
    """
    Dynamically generates test cases based on the number of records.
    """
    if {"a", "b", "operation", "expected"}.intersection(set(metafunc.fixturenames)):
        num_records = metafunc.config.getoption("num_records")
        parameters = list(generate_test_data(num_records))

        modified_parameters = [
            (a, b, op_name if "operation_name" in metafunc.fixturenames else op_func, expected) 
            for a, b, op_name, op_func, expected in parameters
        ]

        metafunc.parametrize(("a", "b", "operation", "expected"), modified_parameters)
