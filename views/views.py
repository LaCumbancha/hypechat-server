from models.models import Message
from models.users import RegularUser
from run import app


@app.route('/messages', methods=['GET'])
def get_messages():
    all_messages = Message.query.all()
    contents = [message.text_content() for message in all_messages]
    return "Mensajes: " + ", ".join(contents)


@app.route('/users', methods=['GET'])
def get_users():
    all_users = RegularUser.query.all()
    emails = [user.email() for user in all_users]
    return "Usuarios: " + ", ".join(emails)
