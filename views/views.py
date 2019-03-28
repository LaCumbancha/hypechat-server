from models import Message
from run import app


@app.route('/', methods=['GET'])
def get_messages():
    all_messages = Message.query.all()
    contents = [message.text_content for message in all_messages]
    return 'Mensajes: ' + ', '.join(contents)
