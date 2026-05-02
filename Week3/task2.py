"""
Task 02 · API → MySQL Pipeline [Hard]
Goal:
Fetch user data from an API, store it in MySQL, and query it — complete automated pipeline.
1. Fetch all users from:
https://jsonplaceholder.typicode.com/users
2. Create app.db with a users table:
id, name, email, phone, city, company_name
3. Extract:
- city from address.city
- company_name from company.name (nested JSON)
4. Insert all 10 users into the database with proper error handling
5. Query 1:
Print all users sorted alphabetically by name
6. Query 2:
Find users from the same city
(GROUP BY city, HAVING COUNT > 1)
7. Add a second table: posts
Fetch from:
https://jsonplaceholder.typicode.com/posts
Insert only posts where user_id is 1, 2, and 3
Deliverable:
app.db with users + posts tables + both query outputs
Bonus:
JOIN users and posts and print each user's posts
"""

import os
import requests
from dotenv import load_dotenv
import mysql.connector

# load environment variables
load_dotenv()

# Connect to MySQL server
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        )
    cursor = conn.cursor()
except mysql.connector.Error as err:
    print("MySQL connection error:", err)
    exit(1)
    
# Create database and tables
cursor.execute("create database if not exists app_db")
cursor.execute("use app_db")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE, 
    city VARCHAR(100),
    company_name VARCHAR(255)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255),
    body TEXT,

    FOREIGN KEY (user_id) REFERENCES users(id)
)""")

# Fetch users from API
response = requests.get(os.getenv("API_URL"))
if response.status_code == 200:
    users = response.json()
    for u in users:
        try:
            cursor.execute("""
            INSERT INTO users (id, name, email, phone, city, company_name)
            VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    email = VALUES(email),
                    phone = VALUES(phone),
                    city = VALUES(city),
                    company_name = VALUES(company_name)
            """, (
                u.get("id"),
                u.get("name"),
                u.get("email"),
                u.get("phone"),
                u.get("address", {}).get("city"),   # safer nested access
                u.get("company", {}).get("name")    # safer nested access
            ))
        except Exception as e:
            print("User insert error:", e)

conn.commit() # commit after all inserts because of foreign key constraint as posts depend on users

# Fetch posts from API
response = requests.get(os.getenv("POSTS_API_URL"))
if response.status_code == 200:
    posts = response.json()
    for p in posts:
        if p["userId"] in [1, 2, 3]: # only insert posts for user_id 1, 2, 3
            try:
                cursor.execute("""
                INSERT INTO posts (id, user_id, title, body)
                VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        user_id = VALUES(user_id),
                        title = VALUES(title),
                        body = VALUES(body)
                """, (
                    p.get("id"),
                    p.get("userId"),
                    p.get("title"),
                    p.get("body")
                ))
            except Exception as e:
                print("Post insert error:", e)

conn.commit() # commit after all inserts

# Query 1: Print all users sorted alphabetically by name
print("\n--- All Users (sorted by name) ---")
cursor.execute("select name, email, city from users order by name")
results = cursor.fetchall()
for name, email, city in results:
    print(f"Name: {name}, Email: {email}, City: {city}")

# Query 2: Find users from the same city
print("\n--- Users from the same city ---")
cursor.execute("""
SELECT city, COUNT(*) 
FROM users
GROUP BY city
HAVING COUNT(*) > 1
""")
results = cursor.fetchall()
for city, count in results:
    print(f"City: {city}, Count: {count}")
    
# Bonus: JOIN users and posts and print each user's posts
print("\n--- Users and their posts ---")
cursor.execute("""
SELECT users.name, posts.title
FROM users
JOIN posts ON users.id = posts.user_id
ORDER BY users.name
""")
results = cursor.fetchall()
for name, title in results:
    print(f"User: {name}, Post Title: {title}")

    
# Cleanup
cursor.close()
conn.close()
