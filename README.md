# Hypechat Server

## Project Bootstrapping

### 1. Clone repository
```
git clone https://github.com/MaxiSuppes/hypechat-server.git
```
### 2. Installing and creating virtual env (will be replaced by Docker)
```
pip install virtualenv
```

Create a new virtual environment in the project folder
```
virtualenv -p python3 hypechat
```
And run the following command to activate it
```
source hypechat/bin/activate
```

Run `source .env` to set environment variables
### 3. Installing postgres
```
sudo apt-get install postgresql postgresql-contrib
```
### 4. Creating databases
```
createdb hypechat
createdb hypechat_test
```
### 5. Initializing db and running migrations
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```
### 6. Installing packages
In the project root directory:
```
pip install -Ur requirements.txt
```

### 7. Generating Docker image
##### Installing Docker:
```
sudo apt-get docker.io
```
##### Creating image
```
docker build -t hypechat-server:latest
```
##### Running image
```
docker run --net host -d -p 5000:5000 hypechat-server
```

## Environments

### Running
Run `source .env` to set environment variables, and then run `flask run`. The app is 
running by default on http://127.0.0.1:5000/ 
 
### Testing
```
python -m unittest -v tests
```

## Endpoints
The public API provides the following endpoints:

### Users:

##### Register new user:
```
POST /users
```
Expected body:
```json
{
  "id": String,
  "email": String,
  "password": String,
}
```
Response: **200 OK**
```json
{
  "auth_token": String
}
```
Possible errors: **400 BAD REQUEST**
```json
{
  "message": String
}
```

##### User login:
```
POST /users/login
```
Expected body:
```json
{
  "email": String,
  "password": String,
}
```
Response: **200 OK**
```json
{
  "auth_token": String
}
```
Possible errors: **400 BAD REQUEST**
```json
{
  "message": String
}
```

##### User logout:
```
POST /users/login
```
Expected body:
```json
{
  "auth_token": String
}
```
Response: **200 OK**
```json
{
  "message": String
}
```
Possible errors: **401 UNAUTHORIZED**
```json
{
  "message": String
}
```

##### User list:
```
GET /users
```
Response: **200 OK**
```
Users: User list
```

##### Messages list:
```
GET /messages
```
Response: **200 OK**
```
Messages: Message list
```
