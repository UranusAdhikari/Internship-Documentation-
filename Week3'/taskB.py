import datetime
import json
import os
import sys
import urllib.error
import urllib.request

try:
    import mysql.connector
except ImportError:
    print("The mysql-connector-python package is required. Install it with: python -m pip install mysql-connector-python")
    sys.exit(1)

# taskB.py monitors JSONPlaceholder post data, saves it to monitor_db, and detects changes.
# It records NEW inserts and MODIFIED field differences in a change_log table.
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "autocommit": False,
}

DB_NAME = "monitor_db"
API_URL = "https://jsonplaceholder.typicode.com/posts"

CREATE_POSTS_TABLE = """
CREATE TABLE IF NOT EXISTS posts (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL
) ENGINE=InnoDB;
"""

CREATE_CHANGE_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS change_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    change_type VARCHAR(20) NOT NULL,
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_at DATETIME NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id)
) ENGINE=InnoDB;
"""

INSERT_POST = "INSERT INTO posts (id, user_id, title, body) VALUES (%s, %s, %s, %s)"
UPDATE_POST = "UPDATE posts SET user_id = %s, title = %s, body = %s WHERE id = %s"
INSERT_CHANGE_LOG = """
INSERT INTO change_log (post_id, user_id, change_type, field_name, old_value, new_value, changed_at)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

QUERY_POST_COUNT_PER_USER = """
SELECT user_id, COUNT(*) AS post_count
FROM posts
GROUP BY user_id
ORDER BY user_id;
"""

QUERY_LATEST_CHANGE_LOG = """
SELECT log_id, post_id, user_id, change_type, field_name, old_value, new_value, changed_at
FROM change_log
WHERE changed_at = (
    SELECT MAX(changed_at)
    FROM change_log
)
ORDER BY log_id;
"""

QUERY_USER_WITH_MOST_CHANGES = """
SELECT user_id, COUNT(*) AS change_count
FROM change_log
GROUP BY user_id
ORDER BY change_count DESC
LIMIT 1;
"""


# connect_mysql: open a MySQL connection using DB_CONFIG.
# Returns None if the connection cannot be established.
def connect_mysql():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as exc:
        print("Error connecting to MySQL server:", exc)
        print("Set MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_PORT environment variables if needed.")
        return None


# fetch_api_posts: retrieve post data from the JSONPlaceholder API and parse JSON.
# Returns a list of post dictionaries or None on failure.
def fetch_api_posts():
    try:
        request = urllib.request.Request(API_URL, headers={"User-Agent": "Python/urllib"})
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload)
    except urllib.error.URLError as exc:
        print("API request failed:", exc)
    except json.JSONDecodeError as exc:
        print("Failed to decode API response as JSON:", exc)
    except Exception as exc:
        print("Unexpected error during API fetch:", exc)
    return None


# ensure_database_and_tables: create monitor_db if needed and ensure the posts and change_log tables exist.
def ensure_database_and_tables(cursor):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute(CREATE_POSTS_TABLE)
        cursor.execute(CREATE_CHANGE_LOG_TABLE)
    except mysql.connector.Error as exc:
        print("Error creating database or tables:", exc)
        raise


# load_existing_posts: read all stored posts from the database into a dict keyed by post ID.
# This supports change detection on subsequent runs.
def load_existing_posts(cursor):
    try:
        cursor.execute("SELECT id, user_id, title, body FROM posts")
        return {row[0]: {"user_id": row[1], "title": row[2], "body": row[3]} for row in cursor.fetchall()}
    except mysql.connector.Error as exc:
        print("Error loading existing posts:", exc)
        return {}


# log_change: insert a change event into the change_log table.
# It records the post id, user id, change type, changed field, old/new values, and timestamp.
def log_change(cursor, post_id, user_id, change_type, field_name, old_value, new_value, changed_at):
    try:
        cursor.execute(
            INSERT_CHANGE_LOG,
            (post_id, user_id, change_type, field_name, old_value, new_value, changed_at),
        )
    except mysql.connector.Error as exc:
        print(f"Error logging change for post {post_id}:", exc)


# insert_post: insert a new post row into the posts table.
def insert_post(cursor, post):
    try:
        cursor.execute(INSERT_POST, (post["id"], post["userId"], post["title"], post["body"]))
    except mysql.connector.Error as exc:
        print(f"Error inserting post {post['id']}:", exc)


# update_post: update an existing post row when the API data differs from stored data.
def update_post(cursor, post):
    try:
        cursor.execute(UPDATE_POST, (post["userId"], post["title"], post["body"], post["id"]))
    except mysql.connector.Error as exc:
        print(f"Error updating post {post['id']}:", exc)


# print_post_count_per_user: query and print how many posts each user has in the posts table.
def print_post_count_per_user(cursor):
    try:
        cursor.execute(QUERY_POST_COUNT_PER_USER)
        print("\n=== Post count per user ===")
        for user_id, post_count in cursor.fetchall():
            print(f"User {user_id}: {post_count} posts")
    except mysql.connector.Error as exc:
        print("Error querying post counts per user:", exc)


# print_latest_change_log: print all change log records that have the latest timestamp.
# This shows which changes were detected during the last run.
def print_latest_change_log(cursor):
    try:
        cursor.execute(QUERY_LATEST_CHANGE_LOG)
        rows = cursor.fetchall()
        print("\n=== Change log entries from latest run ===")
        if not rows:
            print("No change log entries found.")
            return
        for log_id, post_id, user_id, change_type, field_name, old_value, new_value, changed_at in rows:
            details = f"[log_id={log_id}] post_id={post_id}, user_id={user_id}, type={change_type}"
            if field_name:
                details += f", field={field_name}, old={old_value}, new={new_value}"
            details += f", at={changed_at}"
            print(details)
    except mysql.connector.Error as exc:
        print("Error querying latest change log:", exc)


# print_user_with_most_changes: find and print which user triggered the most change events.
def print_user_with_most_changes(cursor):
    try:
        cursor.execute(QUERY_USER_WITH_MOST_CHANGES)
        result = cursor.fetchone()
        print("\n=== User with most change events ===")
        if result:
            print(f"User {result[0]} triggered {result[1]} change event(s)")
        else:
            print("No change events recorded yet.")
    except mysql.connector.Error as exc:
        print("Error querying user change event counts:", exc)


# main: orchestrate the monitoring flow.
# It connects to MySQL, fetches API posts, detects new or modified posts, logs changes, commits the transaction,
# and prints summary reports.
def main():
    connection = connect_mysql()
    if connection is None:
        sys.exit(1)

    cursor = connection.cursor()
    try:
        ensure_database_and_tables(cursor)
    except Exception:
        connection.close()
        sys.exit(1)

    api_posts = fetch_api_posts()
    if api_posts is None:
        connection.close()
        sys.exit(1)

    existing_posts = load_existing_posts(cursor)
    run_timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    first_run = len(existing_posts) == 0
    if first_run:
        print("First run detected: inserting all posts and logging NEW events.")

    for post in api_posts:
        post_id = post.get("id")
        if post_id is None:
            continue

        db_post = existing_posts.get(post_id)
        if db_post is None:
            insert_post(cursor, post)
            log_change(cursor, post_id, post["userId"], "NEW", None, None, None, run_timestamp)
            continue

        if (
            db_post["user_id"] != post["userId"]
            or db_post["title"] != post["title"]
            or db_post["body"] != post["body"]
        ):
            if db_post["user_id"] != post["userId"]:
                log_change(
                    cursor,
                    post_id,
                    post["userId"],
                    "MODIFIED",
                    "user_id",
                    str(db_post["user_id"]),
                    str(post["userId"]),
                    run_timestamp,
                )
            if db_post["title"] != post["title"]:
                log_change(
                    cursor,
                    post_id,
                    post["userId"],
                    "MODIFIED",
                    "title",
                    db_post["title"],
                    post["title"],
                    run_timestamp,
                )
            if db_post["body"] != post["body"]:
                log_change(
                    cursor,
                    post_id,
                    post["userId"],
                    "MODIFIED",
                    "body",
                    db_post["body"],
                    post["body"],
                    run_timestamp,
                )
            update_post(cursor, post)

    try:
        connection.commit()
    except mysql.connector.Error as exc:
        print("Error committing changes to the database:", exc)

    print_post_count_per_user(cursor)
    print_latest_change_log(cursor)
    print_user_with_most_changes(cursor)

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()
