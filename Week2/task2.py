"""
TASK 2: Fetch & Save to CSV
Fetch posts from the API. Save them to a CSV with columns: id, title, body. Then read the CSV back and print only posts where title contains more than 5 words.
Steps:
Endpoint: /posts
Save: id, title, body  to  posts.csv
Read back with DictReader
Filter: Posts having title more than 5 words and write in a new CSV
Deliverable: posts.csv + filter script + new csv
"""


import os
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

def task_2():
    print("--- TASK 2: Fetch & Save to CSV ---")

    url = os.getenv("https://jsonplaceholder.typicode.com/posts")
    print("Using URL:", url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return

    posts = response.json()

    with open('posts.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'body'])
        writer.writeheader()

        for post in posts:
            writer.writerow({
                'id': post['id'],
                'title': post['title'],
                'body': post['body']
            })

    print("Saved posts.csv")

    filtered_posts = [
        {
            'id': post['id'],
            'title': post['title'],
            'body': post['body']
        }
        for post in posts
        if len(post['title'].split()) > 5
    ]

    with open('filtered_posts.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'body'])
        writer.writeheader()
        writer.writerows(filtered_posts)

    print(f"Saved filtered_posts.csv ({len(filtered_posts)} rows)")


if __name__ == "__main__":
    task_2()