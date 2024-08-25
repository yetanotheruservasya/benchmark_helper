import eventlet
from flask import Flask, render_template, request, jsonify
from flask_socketio import send, SocketIO, join_room, leave_room
from dotenv import load_dotenv
import openai
import secrets
import json
import os
from prompts.prompt_generator import *  # Импортируем всё

# Создание секретного ключа
secret_key = secrets.token_hex(16)
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
socketio = SocketIO(app, async_mode='eventlet')

# Загрузите переменные окружения из .env файла
load_dotenv()
# Ключ API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Для хранения истории сообщений для каждого пользователя
user_histories = {}
user_contexts = {}

# Функция для сохранения истории в JSON
def save_user_history_to_json(user_id):
    file_path = f"{user_id}_history.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(user_histories[user_id], f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_context', methods=['POST'])
def save_context():
    global user_contexts, user_histories, welcome_prompt

    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_contexts[user_id] = {}
    # Обновляем user_contexts, исключая ключ 'user_id' из данных
    user_contexts[user_id] = {k: v for k, v in data.items() if k != 'user_id'}

    user_contexts[user_id]['system_prompt'] = generate_system_prompt(user_contexts[user_id])
   
    # Проверяем, что системный промпт не пустой
    if not user_contexts[user_id]['system_prompt'].strip():
        return jsonify({"error": "System prompt cannot be empty"}), 400
    
    try:
        print(f"Preparing message for room: {user_id}")
        context_description = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": user_contexts[user_id]['system_prompt']},
                {"role": "user", "content": welcome_prompt}
            ]
        ).choices[0].message['content'].strip()

        print(f"Context Description: {context_description}")
        socketio.emit('message', {"msg": context_description, "room": user_id}, room=user_id)

        if user_id not in user_histories:
            user_histories[user_id] = []  # Инициализация пустой истории для нового пользователя

        # Добавление сообщения пользователя и ответа ассистента в историю пользователя
        user_histories[user_id].append({"role": "System", "content": context_description})
            # Проверяем, существует ли user_id в user_histories
    
        # Сохранение истории пользователя в JSON после обработки сообщения
        save_user_history_to_json(user_id)

        print(f"Context SAVED!!!: {user_id}")
    except Exception as e:
        socketio.emit('message', {"msg": "Error", "response": str(e)}, room=user_id)

    response = {
        "user_id": user_id,
        "context": user_contexts[user_id]
    }
    
    return jsonify(response)

@socketio.on('message')
def handle_message(data):
    global user_contexts, user_histories

    user_id = data.get('user_id')
    message = data.get('msg')
    
    if not user_id or user_id not in user_contexts:
        print("Error: User ID is required or context not found")
        socketio.emit('error_message', {"msg": "Error: User ID is required or context not found"}, room=None)
        return

    # Получаем системный prompt для пользователя
    system_prompt = user_contexts[user_id].get('system_prompt', '')
     
    # Получаем историю для конкретного пользователя
    if user_id not in user_histories:
        user_histories[user_id] = []

    # Формируем историю сообщений для передачи �� модель
    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": f"{message}"})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages
        ).choices[0].message['content'].strip()

        print(messages)

        # Добавление сообщения пользователя и ответа ассистента в историю пользователя
        user_histories[user_id].append({"role": "user", "content": message})
        user_histories[user_id].append({"role": "assistant", "content": response})

        # Сохранение истории пользователя в JSON после обработки сообщения
        save_user_history_to_json(user_id)

        socketio.emit('message', {"msg": response, "room": user_id}, room=user_id)
    except Exception as e:
        print(f"Exception: {str(e)}")
        socketio.emit('message', {"msg": "Error", "response": str(e)}, room=None)

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    if room:
        join_room(room)
        print(f"Client joined room: {room}")
        # Можно отправить сообщение, чтобы подтвердить присоединение
        socketio.emit('room_joined', {"room": room}, room=room)
    else:
        print("Error: Room ID is required")
        # Отправляем сообщение об ошибке обратно клиенту
        socketio.emit('error_message', {"msg": "Error: Room ID is required"}, room=None)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
