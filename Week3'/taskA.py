import csv
import os
import sys

try:
    import mysql.connector
except ImportError:
    print("The mysql-connector-python package is required. Install it with: python -m pip install mysql-connector-python")
    sys.exit(1)

# taskA.py creates and populates a simple store database, then runs analytics queries.
# It uses mysql-connector-python to manage the MySQL connection and execute SQL.
DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "autocommit": True,
}

CSV_FILE = "revenue_report.csv"

CUSTOMERS = [
    (1, "Ava Carter", "New York"),
    (2, "Noah Walker", "Los Angeles"),
    (3, "Mia Patel", "Chicago"),
    (4, "Liam Chen", "Houston"),
    (5, "Sophia Davis", "Phoenix"),
    (6, "Ethan Kim", "Philadelphia"),
    (7, "Isabella Martinez", "San Antonio"),
    (8, "Mason Brown", "San Diego"),
    (9, "Charlotte Wilson", "Dallas"),
    (10, "Lucas Johnson", "San Jose"),
]

PRODUCTS = [
    (1, "Wireless Mouse", 24.99),
    (2, "Mechanical Keyboard", 79.5),
    (3, "USB-C Hub", 34.75),
    (4, "Noise-Canceling Headphones", 129.0),
    (5, "27-inch Monitor", 229.99),
    (6, "Webcam", 49.0),
    (7, "Portable SSD", 119.99),
    (8, "Laptop Stand", 29.95),
]

ORDERS = [
    (1, 1, 2, 2, "2026-04-01"),
    (2, 2, 1, 1, "2026-04-02"),
    (3, 3, 4, 1, "2026-04-03"),
    (4, 4, 8, 3, "2026-04-03"),
    (5, 5, 6, 2, "2026-04-04"),
    (6, 6, 7, 1, "2026-04-05"),
    (7, 7, 2, 1, "2026-04-05"),
    (8, 8, 3, 2, "2026-04-06"),
    (9, 9, 5, 1, "2026-04-06"),
    (10, 10, 1, 4, "2026-04-07"),
    (11, 1, 4, 1, "2026-04-08"),
    (12, 2, 3, 3, "2026-04-08"),
    (13, 3, 5, 1, "2026-04-09"),
    (14, 4, 7, 2, "2026-04-09"),
    (15, 5, 8, 1, "2026-04-10"),
    (16, 6, 2, 2, "2026-04-10"),
    (17, 7, 6, 1, "2026-04-11"),
    (18, 8, 5, 2, "2026-04-11"),
    (19, 9, 4, 1, "2026-04-12"),
    (20, 10, 7, 1, "2026-04-12"),
]

CREATE_CUSTOMERS = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL
) ENGINE=InnoDB;
"""

CREATE_PRODUCTS = """
CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    price DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB;
"""

CREATE_ORDERS = """
CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    order_date DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) ENGINE=InnoDB;
"""

INSERT_CUSTOMER = "INSERT INTO customers (customer_id, name, city) VALUES (%s, %s, %s)"
INSERT_PRODUCT = "INSERT INTO products (product_id, product_name, price) VALUES (%s, %s, %s)"
INSERT_ORDER = "INSERT INTO orders (order_id, customer_id, product_id, quantity, order_date) VALUES (%s, %s, %s, %s, %s)"

QUERY_REVENUE_PER_CUSTOMER = """
SELECT c.customer_id, c.name, COALESCE(SUM(p.price * o.quantity), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN products p ON o.product_id = p.product_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;
"""

QUERY_MOST_ORDERED_PRODUCT = """
SELECT p.product_id, p.product_name, SUM(o.quantity) AS total_quantity
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_quantity DESC
LIMIT 1;
"""

QUERY_CUSTOMERS_WITH_MORE_THAN_TWO_ORDERS = """
SELECT c.customer_id, c.name, COUNT(*) AS order_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(*) > 2;
"""

QUERY_AVG_ORDER_VALUE_BY_CITY = """
SELECT c.city, ROUND(AVG(p.price * o.quantity), 2) AS avg_order_value
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.city;
"""


# connect_mysql: open a connection to MySQL using the DB_CONFIG settings.
# If the connection fails, print an error and stop execution.
def connect_mysql():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as exc:
        print("Could not connect to MySQL server:", exc)
        print("Set MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, and MYSQL_PORT environment variables if needed.")
        sys.exit(1)


# main: create the store_db schema, insert sample data, execute analytics queries,
# and export the revenue report as a CSV file.
def main():
    connection = connect_mysql()
    cursor = connection.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS store_db")
    cursor.execute("USE store_db")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    cursor.execute(CREATE_CUSTOMERS)
    cursor.execute(CREATE_PRODUCTS)
    cursor.execute(CREATE_ORDERS)

    cursor.executemany(INSERT_CUSTOMER, CUSTOMERS)
    cursor.executemany(INSERT_PRODUCT, PRODUCTS)
    cursor.executemany(INSERT_ORDER, ORDERS)
    connection.commit()

    print("\n=== Total money spent per customer ===")
    cursor.execute(QUERY_REVENUE_PER_CUSTOMER)
    revenue_rows = cursor.fetchall()
    for customer_id, name, total_spent in revenue_rows:
        print(f"{customer_id}: {name} -> ${total_spent:.2f}")

    print("\n=== Most ordered product by total quantity ===")
    cursor.execute(QUERY_MOST_ORDERED_PRODUCT)
    row = cursor.fetchone()
    if row:
        print(f"Product ID {row[0]}: {row[1]} with {row[2]} units ordered")

    print("\n=== Customers with more than 2 orders ===")
    cursor.execute(QUERY_CUSTOMERS_WITH_MORE_THAN_TWO_ORDERS)
    customers_rows = cursor.fetchall()
    for customer_id, name, order_count in customers_rows:
        print(f"{customer_id}: {name} -> {order_count} orders")

    print("\n=== Average order value per city ===")
    cursor.execute(QUERY_AVG_ORDER_VALUE_BY_CITY)
    for city, avg_value in cursor.fetchall():
        print(f"{city}: ${avg_value:.2f}")

    print(f"\nWriting revenue report to {CSV_FILE}")
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["customer_id", "name", "total_spent"])
        for customer_id, name, total_spent in revenue_rows:
            writer.writerow([customer_id, name, f"{total_spent:.2f}"])

    cursor.close()
    connection.close()
    print("Done.")


if __name__ == "__main__":
    main()
