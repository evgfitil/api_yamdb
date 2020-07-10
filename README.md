# api_yamdb
***api_yamdb (YaMDb)*** is a training Rest API project based on Django REST framework.

The YaMDb project collects user feedback on the different content types. Contents are divided into categories: "Books", "Films", "TV Shows" and "Music".

All available endpoints and API specifications here https://yamdb.ea4ws.tk/redoc/

You can try most of the functionality use endpoints on this demo site https://yamdb.ea4ws.tk/api/v1/ or testing it locally.

### Developing and testing locally (Quick Start)

#### With Docker
  
  1. Clone this repository
  2. Rename `.env-docker-example` file to `.env.dev`. Customize it for your needs.
  3. If you want to load the test data you can uncomment the line in `entrypoint.sh` file with:
  ```
  # python manage.py loaddata api/fixtures/db_fixtures.json
  ``` 
  
  4. Use provided `Dockerfile` and `docker-compose.yml`, build the image and run the container
  ```
  docker-compose up -d
  ```
  5. If You're not using the test data, you need to create Django admin user
  
  ```
  docker exec -ti <container_id> python manage.py createsuperuser
  ```
  If everything went well, you now have a server running on http://localhost:8000

  You can also run tests to make sure is everything is ok, for that run:
  ```
  docker exec -ti <container_id> pytest
  ```
  
  You can find API specification and all available endpoints on documentation page http://localhost:8000/redoc/
  
  In order to obtain a confirmation code for the subsequent receipt of the token use `sent_emails` folder on container `workdir`
  ```
  docker exec -ti <container_id> /bin/sh
  ```
  and then look into ``*.log`` files

#### Without Docker

If You want to test API locally:
  1. Fork this repository and clone your version of the repo
  2. Create and activate a virtual environment
  ```
python3 -m venv venv
source ./venv/bin/activate
  ```
  3. Install dependencies
  ```
pip install -r requirements.txt
```
  4. Apply migrations
  ```
python manage.py migrate
```
  5. Create Django admin user
 ```
 python manage.py createsuperuser
 ```
  6. Start API server locally
```
python manage.py runserver
```
If everything went well, you now have a server running on http://localhost:8000

You can find API specification and all available endpoints on documentation page http://localhost:8000/redoc/

To obtain a confirmation code for the subsequent receipt of the token use `sent_emails` folder and then look into ``*.log`` files.
