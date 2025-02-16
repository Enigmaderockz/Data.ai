Feature: Google API Response Validation

  Scenario: Validate Google API Response
    Given I send a GET request to "https://www.google.com"
    Then the response status code should be 200

  Scenario: Validate JSON Data in API Response
    Given I send a GET request to "https://www.google.com"
    Then the response should contain JSON data


Updated utility.py

import requests

def send_request(url):
    """Send a GET request to the specified URL and return the response."""
    response = requests.get(url)
    return response

def is_status_code_valid(response, expected_status):
    """Check if the response status code matches the expected status."""
    return response.status_code == expected_status

def is_json_response_valid(response):
    """Check if the response contains valid JSON data."""
    try:
        json_data = response.json()
        return bool(json_data)  # Pass if data exists, fail if empty
    except ValueError:
        return False  # Response is not a valid JSON



Updated test_google_steps.py

import pytest
from pytest_bdd import scenarios, given, then
from utils.utility import send_request, is_status_code_valid, is_json_response_valid

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

@then("the response should contain JSON data")
def check_json_data(context):
    """Assert that the response contains valid JSON data."""
    assert is_json_response_valid(context["response"]), "Response does not contain valid JSON data."


###with headers

@given('I send a GET request to "https://www.google.com" with headers')
def send_google_request_with_headers(context):
    """Send a GET request with headers and store the response."""
    url = "https://www.google.com"
    headers = {
        "Accept": "application/json",
        "User-Agent": "pytest-bdd-test"
    }
    context["response"] = send_request(url, headers=headers)


def send_request(url, headers=None):
    """Send a GET request to the specified URL with optional headers."""
    response = requests.get(url, headers=headers)
    return response

