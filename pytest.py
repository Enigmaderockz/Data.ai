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


# Define the pytest_generate_tests hook to parametrize the fixtures
def pytest_generate_tests(metafunc):
    # Check if the test is a scenario outline
    if "scenario" in metafunc.fixturenames:
        scenario = metafunc.function.scenario
        # Get the examples for the scenario outline
        for example in scenario.examples:
            # Parametrize the fixtures with the example values
            metafunc.parametrize("conf", [example["conf"]], indirect=True)
            metafunc.parametrize("id", [example["id"]], indirect=True)

# Define the fixtures to receive the parametrized values
@pytest.fixture
def conf(request):
    return request.param

@pytest.fixture
def id(request):
    return request.param
