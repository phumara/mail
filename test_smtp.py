import requests

# Test the SMTP connection endpoint
response = requests.post('http://127.0.0.1:8000/campaigns/test-smtp-connection/2/', 
                        headers={'X-CSRFToken': 'dummy'})

print(f'Status: {response.status_code}')
print(f'Content-Type: {response.headers.get("content-type", "None")}')
print(f'Response length: {len(response.text)}')
print(f'First 300 chars: {response.text[:300]}')