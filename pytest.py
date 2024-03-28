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


# Load the scenarios from the feature file
scenarios('features/abc.feature')

# Define the pytest_generate_tests hook to parametrize the fixtures
def pytest_generate_tests(metafunc):
    # Check if the test is a scenario outline
    if 'conf' in metafunc.fixturenames and 'id' in metafunc.fixturenames:
        # Extract the examples from the feature file
        example_params = metafunc.cls.examples
        # Parametrize the test function with the collected parameters
        metafunc.parametrize('conf,id', example_params, indirect=True)

# Define the fixtures to receive the parametrized values
@pytest.fixture
def conf(request):
    # Return the 'conf' parameter for the current test case
    return request.param['conf']

@pytest.fixture
def id(request):
    # Return the 'id' parameter for the current test case
    return request.param['id']
