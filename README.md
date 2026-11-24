Profile-View-for-an-Online-Enrollment-System

PythonAnywhere deployment instructions are in [DEPLOYMENT.md](DEPLOYMENT.md).

For local development on Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_students
.\.venv\Scripts\python.exe manage.py runserver
```

If needed, create the virtual environment first with `python -m venv .venv`.
Open http://127.0.0.1:8000/students/ to view the five fictional students without login.
