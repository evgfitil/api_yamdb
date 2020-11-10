# api_yamdb
***api_yamdb (YaMDb)*** is a training Rest API project based on Django REST framework.

The YaMDb project collects user feedback on different content types. Contents are divided into categories: "Books", "Films", "TV Shows" and "Music".

All available endpoints and API specifications are here https://yamdb.evgfitil.ml/redoc/

You can try most of the functionality use endpoints on this demo site https://yamdb.evgfitil.ml/api/v1/ or test it locally.

### Developing and testing locally (Quick Start)

#### With Docker
  
  1. Clone this repository
  2. Rename `.env-docker-example` file to `.env.dev`. Customize it for your needs
  3. If you want to load the test data you can uncomment the line in `entrypoint.sh` file with:
  ```
  # python manage.py loaddata api/fixtures/db_fixtures.json
  ``` 
  
  4. Use provided `Dockerfile` and `docker-compose.yml`, build the image and run the container
  ```
  docker-compose up -d --build
  ```
  5. If You're not using the test data, you need to create Django admin user
  
  ```
  docker exec -ti <container_id> python manage.py createsuperuser
  ```
  If everything went well, you now have a server running on http://localhost:8000
  
  Run `docker image prune --filter label=stage=builder` to remove a builder image

  You can also run tests to make sure everything is ok, for that run:
  ```
  docker exec -ti <container_id> pytest
  ```
  
  You can find API specification and all available endpoints on documentation page http://localhost:8000/redoc/
  
  To obtain a confirmation code for the subsequent receipt of the token use `sent_emails` folder on container `workdir`
  ```
  docker exec -ti <container_id> /bin/sh
  ```
  and then look into ``*.log`` files

#### Without Docker

If You want to test API locally:
  1. Clone this repository
  2. Rename `.env-example` file to `.env.dev`
  3. Create and activate a virtual environment
  ```
python3 -m venv venv
source ./venv/bin/activate
  ```
  4. Install dependencies
  ```
pip install -r requirements.txt
```
  5. If you want to load the test data you need to run:
  ```
  python manage.py migrate
  python manage.py loaddata api/fixtures/db_fixtures.json
  ```
  6. If You're not using the test data, You need to create a Django admin user and apply migrations
 ```
 python manage.py migrate
 python manage.py createsuperuser
 ```
  7. Start API server locally
```
python manage.py runserver
```
If everything went well, you now have a server running on http://localhost:8000

You can also run `pytest` to make sure everything is ok

API specification and all endpoints available on documentation page http://localhost:8000/redoc/

To obtain a confirmation code for the subsequent receipt of the token use `sent_emails` folder and then look into ``*.log`` files.

### Default credentials

If You use the test data, use default django admin user `admin` and default password `django_admin`
