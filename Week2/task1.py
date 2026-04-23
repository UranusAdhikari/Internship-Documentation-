"""
Fetch user data from JSONPlaceholder API and display it in terminal.

API:
https://jsonplaceholder.typicode.com/users

Steps:
1. Send GET request using requests
2. Check response status (200 OK)
3. Loop through data
4. Print name, email, and city

Output:
- Show user details in terminal
- Take screenshot of output
"""

import requests
import os 
from dotenv import load_dotenv
load_dotenv()
url = os.getenv("API_URL", "https://jsonplaceholder.typicode.com/users")

response = requests.get(url)
if response.status_code == 200:
    users = response.json()
    for user in users:
        print(f"Name: {user['name']}")
        print(f"Email: {user['email']}")
        print(f"City: {user['address']['city']}")
        print("-" * 30)
else:
    print(f"Failed to fetch users. Status code: {response.status_code}")
    