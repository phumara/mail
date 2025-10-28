import requests

# Test accessing the SMTP manager page directly
session = requests.Session()

# First, let's check if we can access the SMTP manager page
smtp_manager_url = 'http://127.0.0.1:8000/campaigns/smtp-manager/'
response = session.get(smtp_manager_url)

print(f"SMTP Manager page status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type', 'None')}")
print(f"Response length: {len(response.text)}")

# Check if we got redirected to login
if 'login' in response.text.lower():
    print("User is not authenticated - redirected to login")
else:
    print("User appears to be authenticated")
    
# Check cookies
print(f"Session cookies: {session.cookies.get_dict()}")