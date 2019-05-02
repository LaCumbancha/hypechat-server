# Hypechat Server

### Project Bootstrapping

First things first, clone the repository:
```
git clone https://github.com/MaxiSuppes/hypechat-server.git
```

Then, you could choose between running locally in your OS, or running with Docker.

####Local OS

1. Install Python's virtual environment.
```
pip install virtualenv
```

2. Create a new virtualenv in the project folder
```
virtualenv -p python3 hypechat
```

3. Install Python's modules
```
pip install -Ur requirements.txt
```

4. Activate it
```
source hypechat/bin/activate
```

5. Set environment variables
```
source .env
```

6. Run
```
flask run
```

##### Database:

Development mode will connect with a local database for fastest connection. To install PostgreSQL and create the tables: 
```
sudo apt-get install postgresql postgresql-contrib
createdb hypechat
createdb hypechat_test
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

The tables structures are located in the file `tables-scripts.sql`.

####Doker

1. Install Docker
```
sudo apt-get docker.io
```

2. Create the Server image
```
docker build -t hypechat-server:latest .
```

3. Run
```
docker run --net host -d -p 5000:5000 hypechat-server
```

### Testing
The test module uses Unittest framework. To run tests:
```
python -m unittest -v tests
```

### Deployment
The Hypechat Server is hosted in Heroku. To deploy using Heroku CLI:
```
heroku login -i
heroku container:login
heroku container:push web --app hypechat-server
heroku container:release web --app hypechat-server
```
Heroku's host is: https://hypechat-server.herokuapp.com