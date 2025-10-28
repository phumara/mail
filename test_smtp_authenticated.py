import requests

# Create a session to maintain cookies
session = requests.Session()

# Step 1: Get the login page to obtain CSRF token
login_url = 'http://127.0.0.1:8000/accounts/login/'
login_page = session.get(login_url)
csrf_token = session.cookies.get('csrftoken')

print(f"Login page status: {login_page.status_code}")
print(f"CSRF Token: {csrf_token}")

# Step 2: Try to login (you'll need to provide actual credentials)
# For now, let's just test the SMTP connection with the session
smtp_test_url = 'http://127.0.0.1:8000/campaigns/test-smtp-connection/2/'
headers = {
    'X-CSRFToken': csrf_token,
    'Content-Type': 'application/json'
}

response = session.post(smtp_test_url, headers=headers)
print(f"SMTP test status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type', 'None')}")
print(f"Response: {response.text}")

# Check if we're authenticated
if response.status_code == 401:
    print("\nUser is not authenticated. Need to login first.")
elif response.status_code == 200:
    print("\nSMTP test successful!")
else:
    print(f"\nUnexpected status: {response.status_code}")