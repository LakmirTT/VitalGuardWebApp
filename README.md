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

# CURL commands to test api:

## Add new measurement:

```
curl -X POST http://127.0.0.1:8000/vitalguard/measurement/ \
     -H "Content-Type: application/json" \
     -d '{
           "patient": 1,
           "time_taken": "1911-05-26T12:34:56Z",
           "heart_rate": 99,
           "body_temp": 99,
           "ox_saturation": 99,
           "blood_pressure": 99
         }' > res.html
```

## Verify user credentials & check user type:

```
curl -X POST http://127.0.0.1:8000/vitalguard/api/users/check_credentials/ \
     -H "Content-Type: application/json" \
     -d '{
           "username": "j_smith",
           "password": "12345"
         }'
```

## Pairing request:

```
curl -X POST http://127.0.0.1:8000/vitalguard/api/device/pair_req/ \
     -H "Content-Type: application/json" \
     -d '{
           "name": "test_req",
           "surname": "test_req_surname",
           "device_tag": "test_device_tag"
         }'
```

## Get patient measurements (no token auth so far):

```
curl -X GET http://127.0.0.1:8000/vitalguard/api/users/get_measurements/ -H "Content-Type: application/json"
```

# TODO: token auth