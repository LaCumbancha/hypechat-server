
### Project bootstrapping

##### 1. Clone repository
```
git clone https://github.com/MaxiSuppes/hypechat-server.git
```
##### 2. Installing and creating virtual env (will be replaced by Docker)
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
##### 3. Installing postgres
```
sudo apt-get install postgresql postgresql-contrib
```
##### 4. Creating databases
```
createdb hypechat
createdb hypechat_test
```
##### 5. Initializing db and running migrations
```
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```
##### 6. Installing packages
In the project root directory:
```
pip install -Ur requirements.txt
```

### Running
Run `source .env` to set environment variables, and then run `flask run`. The app is 
running by default on http://127.0.0.1:5000/ 
 
### Testing
```
python -m unittest -v tests
```
### Deploying
....
