import pytest
from flask import session
from main import app, db, User, Data, bcrypt
from datetime import date

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

@pytest.fixture
def test_user(client):
    with app.app_context():
        user = User(username='testuser', email='testuser@example.com', password=bcrypt.generate_password_hash('testpassword', 10), status=1)
        db.session.add(user)
        db.session.commit()
        yield user

def test_admin_login(client):
    response = client.post('/admin/', data={'username': 'admin', 'password': 'admin'})
    assert response.status_code == 302  # Redirects to admin dashboard
    assert session.get('admin_id') is not None

def test_admin_login_invalid_credentials(client):
    response = client.post('/admin/', data={'username': 'admin', 'password': 'wrong_password'})
    assert response.status_code == 302  # Redirects back to login page
    assert session.get('admin_id') is None

def test_admin_dashboard(client):
    with client.session_transaction() as sess:
        sess['admin_id'] = 1
        sess['admin_name'] = 'admin'
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data

def test_admin_get_all_user(client):
    with client.session_transaction() as sess:
        sess['admin_id'] = 1
    response = client.get('/admin/get-all-user')
    assert response.status_code == 200
    assert b'Approve User' in response.data

def test_user_login(client):
    response = client.post('/user/', data={'email': 'anamzahra453@gmail.com', 'password': '123'})
    assert response.status_code == 302  # Redirects to user dashboard

def test_user_login_invalid_credentials(client):
    response = client.post('/user/', data={'email': 'user@example.com', 'password': 'wrong_password'})
    assert response.status_code == 302  # Redirects back to login page
    assert session.get('user_id') is None

def test_user_dashboard(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'user'
    response = client.get('/user/dashboard')
    assert response.status_code == 200
    assert b'User Dashboard' in response.data


def test_user_add_data(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    response = client.post('/user/add-data', data={
        'firstname': 'John',
        'lastname': 'Doe',
        'gender': 'Male',
        'immunization_history': 'Up to date',
        'insurance_provider_details': 'Test Insurance',
        'past_illnesses': 'None',
        'policy_number': 'ABC123',
        'last_checkup': date.today().strftime('%Y-%m-%d'),  # Use a valid date string
        'phone': '1234567890'
    })

    assert response.status_code == 302  # Redirects back to user dashboard
    assert Data.query.filter_by(firstname='John').first() is not None

def test_user_change_password(client, test_user):
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
    response = client.post('/user/change-password', data={'email': 'testuser@example.com', 'password': 'new_password'})
    assert response.status_code == 302  # Redirects back to user dashboard
    user = User.query.get(test_user.id)
    assert user is not None
    assert bcrypt.check_password_hash(user.password, 'new_password')

if __name__ == '__main__':
    pytest.main()
