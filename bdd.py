Feature File: google.feature

Feature: Google API Response Validation

  Scenario: Validate Google API Response
    Given I send a GET request to "https://www.google.com"
    Then the response status code should be 200

Utility Function: utility.py

import requests

def send_request(url):
    """Send a GET request to the specified URL and return the response."""
    response = requests.get(url)
    return response

def is_status_code_valid(response, expected_status):
    """Check if the response status code matches the expected status."""
    return response.status_code == expected_status


test_google_steps.py
Now, assertions happen here based on the return value from utility.py.

python
Copy
Edit
import pytest
from pytest_bdd import scenarios, given, then
from utils.utility import send_request, is_status_code_valid

# Load scenarios from the feature file
scenarios("../features/google.feature")

@pytest.fixture
def context():
    """Context dictionary to store shared test data."""
    return {}

@given('I send a GET request to "https://www.google.com"')
def send_google_request(context):
    """Send a GET request and store the response."""
    url = "https://www.google.com"
    context["response"] = send_request(url)

@then('the response status code should be 200')
def check_status_code(context):
    """Assert that the response status code is 200."""
    assert is_status_code_valid(context["response"], 200), \
        f"Expected status code 200, but got {context['response'].status_code}"

