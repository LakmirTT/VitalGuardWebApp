# Install dependencies:

1. `python3 -m pip install Django`
2. `python3 -m pip install djangorestframework`

# Run

- cd to repo folder
- run `python3 manage.py runserver`

# Directory structure:

- .                                                 - `root folder`
- db.sqlite3                                      - `database`
- manage.py                                       - `Django management script`
- mysite                                          - `Development server main directory.`
    - asgi.py
    - \_\_init__.py
    - \_\_pycache__
    - settings.py                                 - `configuration file`
    - urls.py                                     - `mapping urls to apps`
    - wsgi.py
- README.md
- VitalGuard                                      - `App main folder. Each development server may contain multiple apps, and each app may be transferred to different development servers before deployment.`
    - admin.py                                    - `Define which models(database tables) are present in Django administration tool`
    - apps.py                         
    - \_\_init__.py
    - migrations
    - models.py                                   - `Database architecture definition`
    - \_\_pycache__
    - serializers.py                              - `Classes for serializing data in order to work with API`
    - templates                                   - `Frontend design files`
      -  VitalGuard
           - login.html
           - patient_entry.html
    - tests.py
    - urls.py                                     - `Mapping url patterns to views`
    - views.py                                    - `Request handling logic (API)`

