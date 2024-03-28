from pytest_bdd import scenarios, given, then
import pytest

# Load feature files from the specified directory
scenarios("./feature/")

# Fixture to provide job details
@pytest.fixture
def job_details(request):
    return {
        'conf': request.getfixturevalue('conf'),
        'id': request.getfixturevalue('id')
    }

# Given step to define the configuration file and product id
@given('config file <conf> for product "<product>" and TestCaseld <id>')
def given_config(job_details, conf, product, id):
    print(f"Fixture conf: {job_details['conf']}, Fixture id: {job_details['id']}")
    print(f"Step conf: {conf}, Step id: {id}")

# Then step to verify the data
@then('data between source file and table should match')
def then_data_match():
    print("Data matches")



#####################################################################3


