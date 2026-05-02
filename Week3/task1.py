"""
Task 01 · Create, Insert & Query [Medium]
Independent task — build your first MySQL database from scratch
Goal:
Create a MySQL database, populate it with data, and run queries to answer questions about it.
1. Create a database called library.db with a table books
   (id, title, author, year, genre, rating REAL)
2. Insert at least 8 books — use a mix of genres, years, and ratings
3. Query 1:
   SELECT all books published after 2000, ordered by rating (highest first)
4. Query 2:
   SELECT all books in the 'Fiction' genre with rating above 4.0
5. Query 3:
   Find the average rating across all books
6. Query 4:
   Count how many books exist per genre — use GROUP BY genre
7. Print all query results neatly with labels — not just raw tuples

Bonus : Add a reviews table and link it to books via book_id foreign key
Deliverable: library.db + script showing all 4 query outputs
"""
import os
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
    print(f"Error connecting to MySQL: {err}")
    exit(1)

# Create database and table
cursor.execute("create database if not exists library_db")
cursor.execute("use library_db")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    year INT,
    genre VARCHAR(100),
    rating REAL
)
""")

cursor.execute("""
create table if not exists reviews (
    id int auto_increment primary key,
    book_id int,
    review_text text,
    rating int,
    foreign key (book_id) references books(id)
)
""")

# Sample data for books and reviews
books_data = [
    ("The Great Gatsby", "F. Scott Fitzgerald", 1925, "Fiction", 4.2),
    ("To Kill a Mockingbird", "Harper Lee", 1960, "Fiction", 4.3),
    ("1984", "George Orwell", 1949, "Dystopian", 4.1),
    ("The Catcher in the Rye", "J.D. Salinger", 1951, "Fiction", 3.8),
    ("The Hobbit", "J.R.R. Tolkien", 1937, "Fantasy", 4.7),
    ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", 1997, "Fantasy", 4.5),
    ("The Da Vinci Code", "Dan Brown", 2003, "Thriller", 3.9),
    ("The Alchemist", "Paulo Coelho", 1988, "Adventure", 3.9)
]

reviews_data = [
    (1, "A classic piece of literature.", 5),
    (2, "A powerful story about justice.", 5),
    (3, "A chilling dystopian novel.", 4),
    (4, "A coming-of-age story that resonates.", 4),
    (5, "An epic fantasy adventure.", 5),
    (6, "A magical journey for all ages.", 5),
    (7, "A fast-paced thriller with twists.", 4),
    (8, "An inspiring tale of self-discovery.", 4)
]

# Insert sample data into the books table
for book in books_data:
    cursor.execute("""
    INSERT INTO books (title, author, year, genre, rating)
    VALUES (%s, %s, %s, %s, %s)
    """, book)

# Insert sample data into the reviews table
for review in reviews_data:
    cursor.execute("""
    INSERT INTO reviews (book_id, review_text, rating)
    VALUES (%s, %s, %s)
    """, review)

# Commit the changes
conn.commit()

# Query 1: SELECT all books published after 2000, ordered by rating (highest first) 
cursor.execute("""
    SELECT title, author, year, genre, rating FROM books
    WHERE year > 2000
    ORDER BY rating DESC
""")
results = cursor.fetchall()
print("Books published after 2000, ordered by rating:")
for title, author, year, genre, rating in results:
    print(f"{title} by {author} ({year}) - Genre: {genre}, Rating: {rating}")
    
# Query 2: SELECT all books in the 'Fiction' genre with rating above 4.0
cursor.execute("""
    SELECT title, author, year, rating FROM books
    WHERE genre = 'Fiction' AND rating > 4.0
""")
results = cursor.fetchall()
print("\nFiction books with rating above 4.0:")
for title, author, year, rating in results:
    print(f"{title} by {author} ({year}) - Rating: {rating}")   
    
# Query 3: Find the average rating across all books
cursor.execute("""
    SELECT AVG(rating) FROM books
""")
result = cursor.fetchone()
print(f"\nAverage rating across all books: {result[0]:.2f}")

# Query 4: Count how many books exist per genre — use GROUP BY genre
cursor.execute("""
    SELECT genre, COUNT(*) FROM books
    GROUP BY genre
""")
results = cursor.fetchall()
print("\nNumber of books per genre:")
for genre, count in results:
    print(f"{genre}: {count} books")
    
# Bonus: Query to show reviews for each book
cursor.execute("""
    SELECT b.title, r.review_text, r.rating FROM books b
    JOIN reviews r ON b.id = r.book_id
""")
results = cursor.fetchall()
print("\nBook reviews:")
for title, review_text, rating in results:
    print(f"{title} - Review: {review_text} (Rating: {rating})")

# Close the connection
cursor.close()
conn.close()
