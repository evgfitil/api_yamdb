# api_yamdb
***api_yamdb (YaMDb)*** is a training Rest API project based on Django REST framework.

The YaMDb project collects user feedback on the works. Works are divided into categories: "Books", "Films", "TV Shows" and "Music".

All available endpoints and API specifications here https://yamdb.ea4ws.tk/redoc/

You can try most of the functionality use endpoints on this demo site https://yamdb.ea4ws.tk/ or testing it locally.

### Developing and testing locally (Quick Start)

#### With Docker

##### With prepared image from the DockerHub:
  1. Copy provided `docker-compose-run.yml` and customize for your needs
  2. Create `.env` file with `SECRET_KEY` env (You can use Django secret key generator or something like this)
  3. Run
  ```
  docker-compose -f docker-compose-run.yml up -d
  ```
  4. Create Django admin user
  ```
  docker exec -ti yamdb python ./manage.py createsuperuser
  ```
  
##### Without prepared image:

  1. Fork this repository and clone your version of the repo
  2. Create `.env` file with `SECRET_KEY` env (You can use Django secret key generator or something like this)
  3. Use provided `Dockerfile` and `docker-compose.yml`, build the image and run the container
  ```
  docker-compose build
  docker-compose up -d
  ```
  4. Create Django admin user
  
  ```
  docker exec -ti <container_id> python ./manage.py createsuperuser
  ```
  If everything went well, you now have server running on http://localhost:8000
  
  You can find API specification and all available endpoints on documentation page http://localhost:8000/redoc/
  
  In order to obtain a confirmation code for the subsequent receipt of the token use `sent_emails` folder on container workdir
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
  5. Start API server locally
```
python manage.py runserver
```
If everything went well, you now have server running on http://localhost:8000

You can find API specification and all available endpoints on documentation page http://localhost:8000/redoc/
