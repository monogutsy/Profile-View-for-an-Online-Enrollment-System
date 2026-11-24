# Deploy on PythonAnywhere

This project uses Django 5.2, SQLite, and Python 3.10 or newer. Choose a Python version offered on your PythonAnywhere Web tab and use that exact version for your virtual environment. The commands below use Python 3.10 as an example.

Student lists and profiles open without login, as requested for the activity. Use the included fictional students. Django admin remains optional and requires its own admin account.

## 1. Upload the complete project

Commit and push your current local project files to GitHub before cloning. New local files do not reach PythonAnywhere until they are uploaded or pushed. Include `enrollment`, `students` (including migrations and management commands), `templates`, `static`, `manage.py`, and `requirements.txt`.

In a PythonAnywhere **Bash console**:

```bash
git clone https://github.com/monogutsy/Profile-View-for-an-Online-Enrollment-System.git
cd ~/Profile-View-for-an-Online-Enrollment-System
python3.10 -m venv ~/.virtualenvs/enrollment
source ~/.virtualenvs/enrollment/bin/activate
python -m pip install -r requirements.txt
```

If you already uploaded the repository, start with `cd` instead of cloning again. Create the Linux virtual environment there; do not upload the Windows `.venv`.

## 2. Create the private configuration

In the same project directory, replace `YOUR_USERNAME.pythonanywhere.com` below with the exact domain shown on your Web tab (including `.eu.pythonanywhere.com` if applicable). Use only the hostname, without `https://` or a trailing slash.

```bash
python -c "import json, secrets; config = {'hostname': 'YOUR_USERNAME.pythonanywhere.com', 'secret_key': secrets.token_urlsafe(64)}; f = open('pythonanywhere_config.json', 'x'); json.dump(config, f); f.close()"
chmod 600 pythonanywhere_config.json
export DJANGO_SETTINGS_MODULE=enrollment.production
python manage.py migrate
python manage.py seed_students
python manage.py collectstatic --noinput
python manage.py check --deploy
```

The configuration command runs once and refuses to overwrite an existing file. For a hostname correction, edit that file using PythonAnywhere's Files tab and preserve its secret key. It is ignored by Git. Both WSGI and terminal commands read it through `enrollment.production`.

The deployment check may report `security.W004` because HSTS is intentionally disabled until the live HTTPS configuration is verified. Investigate any other warning or error before continuing.

`seed_students` adds the five fictional BSIT 1-A students with numbers `024A-2352` through `024A-2356`. It is safe to repeat: it preserves records with those student numbers. Your local SQLite database is ignored by Git, so this step supplies records on a fresh deployment. No superuser is needed to view the activity.

## 3. Configure the Web app

On the **Web** tab, add a web app with **Manual configuration** and the same Python version used for the virtual environment.

Replace `YOUR_USERNAME` in these paths with your PythonAnywhere username:

| Web tab field | Value |
| --- | --- |
| Source code | `/home/YOUR_USERNAME/Profile-View-for-an-Online-Enrollment-System` |
| Working directory | `/home/YOUR_USERNAME/Profile-View-for-an-Online-Enrollment-System` |
| Virtualenv | `/home/YOUR_USERNAME/.virtualenvs/enrollment` |

Open the **WSGI configuration file linked on the Web tab**. Replace its starter contents with the following, changing `YOUR_USERNAME`:

```python
import os
import sys

project_path = '/home/YOUR_USERNAME/Profile-View-for-an-Online-Enrollment-System'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'enrollment.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

PythonAnywhere uses this Web-tab WSGI file, not the project's `enrollment/wsgi.py`. Do not run `manage.py runserver` for hosting.

## 4. Map CSS and reload

Under **Static files**, add:

| URL | Directory |
| --- | --- |
| `/static/` | `/home/YOUR_USERNAME/Profile-View-for-an-Online-Enrollment-System/staticfiles` |

Save and click **Reload** on the Web tab. Visit the HTTPS version of your domain. Django also redirects HTTP requests to HTTPS.

## 5. Verify the hosted site

- `/` redirects to `/students/` without a sign-in page.
- `/students/` shows five students in BSIT 1-A.
- Clicking different students displays their own personal and background details.
- **Back to Student List** returns to the same class.
- `/static/css/style.css` displays CSS rather than a 404 page.
- `/students/999999/` returns a normal 404 page with debugging disabled.

If anything fails, check the **error log linked on the Web tab**. A 400 usually means the configured hostname differs from the URL being visited; missing CSS usually means the static mapping or `collectstatic` step is missing. A missing `students_student` table means migrations were not applied to this deployment's database. An empty list means the seed command has not been run.

## Later updates

In Bash, use the existing checkout and virtual environment:

```bash
cd ~/Profile-View-for-an-Online-Enrollment-System
source ~/.virtualenvs/enrollment/bin/activate
export DJANGO_SETTINGS_MODULE=enrollment.production
git pull
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check
```

Then click **Reload** on the Web tab. Preserve `db.sqlite3` and `pythonanywhere_config.json` between updates.

Official references: [PythonAnywhere Django deployment](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/) and [Django static files on PythonAnywhere](https://help.pythonanywhere.com/pages/DjangoStaticFiles/).
