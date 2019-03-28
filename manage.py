import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app
from models import *

app = create_app(config_name=os.getenv('APP_SETTINGS'))
migrate = Migrate(app, db)
manager = Manager(app)


@manager.command
def create_db():
    os.system('createdb hypechat')
    os.system('createdb hypechat_test')
    print('Databases created')


@manager.command
def drop_db():
    os.system(
        'psql -c "DROP DATABASE IF EXISTS hypechat_test"')
    os.system(
        'psql -c "DROP DATABASE IF EXISTS hypechat"')
    print('Databases dropped')


manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
