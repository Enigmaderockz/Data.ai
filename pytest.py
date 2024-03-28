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


def pytest_generate_tests(metafunc):
    # Check if the test is a scenario outline
    if 'scenario' in metafunc.fixturenames:
        # Extract the scenario from the test function
        scenario = metafunc.function.scenario
        # Create a list to hold the parameter sets for each example
        example_params = []
        # Iterate over the examples in the scenario
        for example in scenario.examples:
            # Append the parameter set (conf, id) for each example
            example_params.append((example['conf'], example['id']))
        # Parametrize the test function with the collected parameters
        metafunc.parametrize('conf,id', example_params, indirect=True)

# Define the fixtures to receive the parametrized values
@pytest.fixture
def conf(request):
    # Return the 'conf' parameter for the current test case
    return request.param[0]

@pytest.fixture
def id(request):
    # Return the 'id' parameter for the current test case
    return request.param[1]
