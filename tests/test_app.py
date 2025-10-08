import pytest
from fastapi.testclient import TestClient
from main import voting_app
from utils.constants import Endpoints

client = TestClient(voting_app)


def test_read_main():
    """
    Test the root endpoint.
    """
    response = client.get(Endpoints.ROOT)
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """
    Test the health check endpoint.
    """
    response = client.get(Endpoints.HEALTH)
    assert response.status_code == 200
    assert response.json() == {"message": "Healthy", "status": 200}


test_users = [
    ("test1@example.com", "test user 1", "testpassword1", None),
    ("test2@example.com", "test user 2", "testpassword2", None),
    ("test3@example.com", "test user 3", "testpassword3", None),
    ("test4@example.com", "test user 4", "testpassword4", None),
    ("test5@example.com", "test user 5", "testpassword5", None),
    ("test6@example.com", "test user 6", "testpassword6", None),
    ("test7@example.com", "test user 7", "testpassword7", None),
    ("test8@example.com", "test user 8", "testpassword8", None),
    ("test9@example.com", "test user 9", "testpassword9", None),
    ("test10@example.com", "test user 10", "testpassword10", None)
]

@pytest.mark.parametrize("email, name, password, token" , test_users)
def test_create_registration(email, name, password, token):
    """
    Test user registration endpoint.
    """
    user_data = {
        "email": email,
        "name": name,
        "password": password
    }
    response = client.post(f"/users{Endpoints.REGISTER}", json=user_data)
    assert response.status_code == 201
    assert "email" in response.json()
    assert response.json()["email"] == user_data["email"]

@pytest.mark.parametrize("email, name, password, token" , test_users)
def test_user_login(email, name, password, token):
    """
    Test user login endpoint.
    """
    login_data = {
        "email": email,
        "password": password
    }
    # For GET request with body, we need to use request method directly
    response = client.request("GET", f"/users{Endpoints.LOGIN}", json=login_data)
    assert response.status_code == 200
    assert "token" in response.json()
    token = response.json()["token"]
    # Update the token in the test_users list
    for i in range(len(test_users)):
        if test_users[i][0] == email:
            test_users[i] = (email, name, password, token)
    # Return the token for further tests
    print(f"Token for {email}: {token}")

candidates = [
    (1, "Candidate 1", "Party A"),
    (2, "Candidate 2", "Party B"),
    (3, "Candidate 3", "Party C"),
    (4, "Candidate 4", "Party D"),
    (5, "Candidate 5", "Party E"),
    (6, "Candidate 6", "Party F"),
    (7, "Candidate 7", "Party G"),
    (8, "Candidate 8", "Party H"),
    (9, "Candidate 9", "Party I"),
    (10, "Candidate 10", "Party J")
]

@pytest.mark.parametrize("candidate_id, candidate_name, candidate_party" , candidates)
def test_add_candidate(candidate_id, candidate_name, candidate_party):
    """
    Test adding a candidate (admin only).
    """
    
    admin_token = "abdul_is_admin"
    client.headers = {"x-api-key": admin_token}

    candidate_data = {
        "id": candidate_id,
        "name": candidate_name,
        "party": candidate_party
    }
    response = client.post(f"/admin{Endpoints.ADD_CANDIDATE}", json=candidate_data)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["id"] == candidate_data["id"]

votes = [
    (1, 1),
    (2, 1),
    (3, 3),
    (4, 3),
    (5, 3),
    (6, 9),
    (7, 9),
    (8, 1),
    (9, 2),
    (10, 10)
]

@pytest.mark.parametrize("user_id, candidate_id" , votes)
def test_cast_vote(user_id, candidate_id):
    """
    Test casting a vote.
    """
    # Get the token for the user
    email, name, password, token = test_users[user_id - 1] # user_id starts from 1
    voting_data = {
        "candidate_id": candidate_id
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/users{Endpoints.VOTE}", json=voting_data, headers=headers)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["candidate_id"] == voting_data["candidate_id"]

vote_counts = {
    1: {"candidate_id": 1, "candidate_name": "Candidate 1", "party": "Party A", "vote_count": 3},
    2: {"candidate_id": 2, "candidate_name": "Candidate 2", "party": "Party B", "vote_count": 1},
    3: {"candidate_id": 3, "candidate_name": "Candidate 3", "party": "Party C", "vote_count": 3},
    4: {"candidate_id": 4, "candidate_name": "Candidate 4", "party": "Party D", "vote_count": 0},
    5: {"candidate_id": 5, "candidate_name": "Candidate 5", "party": "Party E", "vote_count": 0},
    6: {"candidate_id": 6, "candidate_name": "Candidate 6", "party": "Party F", "vote_count": 0},
    7: {"candidate_id": 7, "candidate_name": "Candidate 7", "party": "Party G", "vote_count": 0},
    8: {"candidate_id": 8, "candidate_name": "Candidate 8", "party": "Party H", "vote_count": 0},
    9: {"candidate_id": 9, "candidate_name": "Candidate 9", "party": "Party I", "vote_count": 2},
    10: {"candidate_id": 10, "candidate_name": "Candidate 10", "party": "Party J", "vote_count": 1}
}

def test_get_vote_counts():
    """
    Test retrieving vote counts (admin only).
    """
    admin_token = "abdul_is_admin"
    client.headers = {"x-api-key": admin_token}
    response = client.get(f"/admin{Endpoints.ADD_CANDIDATE}")
    assert response.status_code == 200
    for vote_count in response.json():
        assert vote_count["candidate_id"] == vote_counts[vote_count["candidate_id"]]["candidate_id"]
        assert vote_count["candidate_name"] == vote_counts[vote_count["candidate_id"]]["candidate_name"]
        assert vote_count["vote_count"] == vote_counts[vote_count["candidate_id"]]["vote_count"]


if __name__ == "__main__":
    pytest.main()