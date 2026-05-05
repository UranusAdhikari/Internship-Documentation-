# Store DB Setup

This workspace contains:

- `store_db_setup.py` — Python script that creates `store_db`, sets up `customers`, `products`, and `orders`, inserts sample data using parameterized `%s` queries, runs analytic queries, and exports `revenue_report.csv`.
- `api_monitor.py` — Python monitoring script that creates `monitor_db`, stores JSONPlaceholder posts, detects changes on rerun, and logs events to `change_log`.
- `revenue_report.csv` — exported revenue-per-customer results.

## Requirements

- Python 3.10
- `mysql-connector-python` (installed in `.venv`)
- Access to a local MySQL server

## Usage

1. Set MySQL connection environment variables if needed:

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your_password"
$env:MYSQL_PORT = "3306"
```
2. Run either script from the workspace root:

```powershell
Set-Location "c:\Users\Acer\OneDrive\Desktop\Intern\Week3'"
& ".\.venv\Scripts\python.exe" store_db_setup.py
# or
& ".\.venv\Scripts\python.exe" api_monitor.py
```

- `store_db_setup.py` prints analytics and writes `revenue_report.csv`.
- `api_monitor.py` creates `monitor_db`, stores posts, detects changes, and writes logs to `change_log`.
