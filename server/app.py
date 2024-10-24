from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    # Handle GET request
    if request.method == 'GET':
        ordered_messages = Message.query.order_by(Message.created_at.asc()).all()
        
        # Check if the message list is empty
        if not ordered_messages:
            return {"message": "No messages found in the database."}, 404
        else:
            ordered_messages_dict = [message.to_dict() for message in ordered_messages]
            return jsonify(ordered_messages_dict), 200

    # Handle POST request
    elif request.method == 'POST':
        data = request.get_json()
        body = data.get('body')  
        username = data.get('username')
        if not body:
            return jsonify({'error': 'Message body is required!'}), 400
        
        new_message = Message(body=body, username=username)
        db.session.add(new_message)
        db.session.commit()
        
        new_message_dict = new_message.to_dict()
        return jsonify(new_message_dict), 201

# PATCH and DELETE route
@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter(Message.id == id).first()
    
    if message is None:
        return jsonify({"message": "Message can not be found in the database."}), 404  
    
    #  Hanlde PATCH request
    if request.method == 'PATCH':
        for attr in request.json:  
            setattr(message, attr, request.json.get(attr))  
        db.session.commit()  

        message_dict = message.to_dict()  
        return jsonify(message_dict), 200 

    # Handle DELETE request
    elif request.method == 'DELETE':
        db.session.delete(message)  
        db.session.commit()  
        return jsonify({"message": "Message deleted successifuly."}), 204  


if __name__ == '__main__':
    app.run(port=5555)
