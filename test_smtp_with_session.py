import requests
import sys

# First, let's try to login to get a proper session
session = requests.Session()

# Try to access the login page to get CSRF token
login_url = 'http://127.0.0.1:8000/accounts/login/'
try:
    login_page = session.get(login_url)
    print(f"Login page status: {login_page.status_code}")
    
    # Look for CSRF token in cookies
    csrf_token = session.cookies.get('csrftoken')
    print(f"CSRF Token from cookie: {csrf_token}")
    
    # Try to test SMTP connection with the session
    test_url = 'http://127.0.0.1:8000/campaigns/test-smtp-connection/2/'
    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json'
    }
    
    response = session.post(test_url, headers=headers)
    print(f"SMTP test status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'None')}")
    print(f"Response: {response.text[:500]}")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Response: {response.text[:500] if 'response' in locals() else 'No response'}")