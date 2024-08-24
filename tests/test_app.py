import os
import json
import pytest
import time
import openai
from flask import Flask
from flask_socketio import SocketIO
from flask_testing import TestCase
from app import app, socketio, user_contexts
from unittest.mock import patch
from prompts.prompt_generator import generate_system_prompt

class TestApp(TestCase):
    def create_app(self):
        # Настройка приложения для тестирования
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        return app

    def test_index(self):
        response = self.client.get('/')
        self.assert200(response)
        # Проверьте наличие ключевых элементов в HTML-коде
        self.assertIn(b"Set Context", response.data)
        self.assertIn(b"Save Context", response.data)

    def test_save_context(self):
        response = self.client.post('/save_context', json={
            'user_id': 'test_user',
            'company_size': 'Large',
            'scope': 'Custom Software Development',
            'customers': 'IT',
            'department': 'Operations',
            'lifecycle': 'Startup',
            'goal': 'Performance Increasement',
            'market': 'Country'
        })
        self.assert200(response)
        
        # Проверяем, что user_id находится внутри объекта context
        response_json = response.get_json()
        self.assertEqual(response_json['user_id'], 'test_user')
        self.assertIn('context', response_json)
        
        context = response_json['context']
        self.assertIn('company_size', context)
        self.assertIn('scope', context)
        self.assertIn('customers', context)
        self.assertIn('department', context)
        self.assertIn('lifecycle', context)
        self.assertIn('goal', context)
        self.assertIn('market', context)
        
        self.assertEqual(context['company_size'], 'Large')
        self.assertEqual(context['scope'], 'Custom Software Development')
        self.assertEqual(context['customers'], 'IT')
        self.assertEqual(context['department'], 'Operations')
        self.assertEqual(context['lifecycle'], 'Startup')
        self.assertEqual(context['goal'], 'Performance Increasement')
        self.assertEqual(context['market'], 'Country')

    def test_openai_key(self):
        # Проверяем, что переменная окружения доступна
        api_key = os.getenv('OPENAI_API_KEY')
        self.assertIsNotNone(api_key, "OPENAI_API_KEY is not set")

        # Устанавливаем ключ API для openai
        openai.api_key = api_key

        # Пробуем выполнить запрос к OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello"}]
            )
            # Выводим ответ для проверки
            print(response.choices[0].message['content'].strip())
        except Exception as e:
            self.fail(f"Failed to call OpenAI API: {e}")

    def test_handle_message(self):
        with patch('app.user_contexts', {'test_user': {
            'company_size': 'Large',
            'scope': 'Custom Software Development',
            'customers': 'IT',
            'department': 'Operations',
            'lifecycle': 'Startup',
            'goal': 'Performance Increasement',
            'market': 'Country'
        }}):
            # Создаем экземпляр клиента сокетов
            client = socketio.test_client(app)

            try:
                # Подключаемся к комнате и отправляем сообщение
                client.emit('join_room', {'room': 'test_user'})
                time.sleep(1)  # Подождите немного, чтобы клиент присоединился к комнате

                # Убедитесь, что клиент подключен
                self.assertTrue(client.is_connected(), "Client failed to connect")

                # Отправляем сообщение через сокеты
                client.emit('message', {'user_id': 'test_user', 'msg': 'Hello'}, room='test_user')

                # Дайте немного времени для получения сообщения
                time.sleep(2)

                # Проверяем, что сообщение получено
                received = client.get_received()
                print("Received data:", received)  # Для отладки
                for event in received:
                    print(f"Received event: {event['name']}")
                    print(f"With args: {event['args']}")

                # Проверьте, содержит ли одно из сообщений ожидаемый текст
                self.assertTrue(any('Hello' in str(event.get('args', [])) for event in received), 
                                "Expected message 'Hello' not found in received data")
            finally:
                # Закрываем соединение
                client.disconnect()

    def test_handle_join_room(self):
        # Создаем экземпляр клиента сокетов
        client = socketio.test_client(app)
        
        try:
            # Подключаемся к комнате
            client.emit('join_room', {'room': 'test_room'})
            
            # Проверяем, что было получено сообщение о присоединении
            received = client.get_received()
            print("Received events:", received)  # Для отладки
            
            # Проверьте структуру событий и найдите нужные данные
            room_joined = False
            for event in received:
                if event['name'] == 'room_joined':  # Предположим, что событие называется 'room_joined'
                    if 'room' in event['args'][0]:  # Предполагается, что данные находятся в args
                        if event['args'][0]['room'] == 'test_room':
                            room_joined = True
                            break

            self.assertTrue(room_joined, "Expected room 'test_room' not found in received data")

        finally:
            # Закрываем соединение
            client.disconnect()

    def test_save_user_history(self):
        with patch('app.user_contexts', {'test_user': {
            'company_size': 'Large',
            'scope': 'Custom Software Development',
            'customers': 'IT',
            'department': 'Operations',
            'lifecycle': 'Startup',
            'goal': 'Performance Increasement',
            'market': 'Country'
        }}):
            # Создаем экземпляр клиента сокетов
            client = socketio.test_client(app)

            try:
                # Подключаемся к комнате и отправляем сообщение
                client.emit('join_room', {'room': 'test_user'})
                client.emit('message', {'user_id': 'test_user', 'msg': 'Test message'}, room='test_user')

                # Проверьте, что история сообщений была сохранена
                history_file = 'test_user_history.json'
                self.assertTrue(os.path.exists(history_file), "History file does not exist")
                
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    print("History content:", history)  # Для отладки
                    self.assertTrue(any(entry['content'] == 'Test message' for entry in history),
                                    "Expected message 'Test message' not found in history")
            
            finally:
                # Закрываем соединение и удаляем файл истории
                client.disconnect()
                if os.path.exists(history_file):
                    os.remove(history_file)

    def test_save_context_partial_fields(self):
        # Создаем частично заполненный контекст
        partial_context = {
            'user_id': 'test_user',
            'company_size': 'Large'
            # Другие поля пропущены
        }

        # Отправляем запрос на сохранение контекста
        response = self.client.post('/save_context', json=partial_context)

        # Проверяем, что статус код 200 (OK) и запрос выполнен успешно
        self.assertEqual(response.status_code, 200)

        # Проверяем, что ответ содержит user_id и частично сохраненный контекст
        response_json = response.json
        self.assertEqual(response_json.get('user_id'), 'test_user')
        self.assertIn('company_size', response_json.get('context', {}))
        self.assertEqual(response_json['context']['company_size'], 'Large')

        # Проверяем, что другие поля контекста отсутствуют или заполнены значениями по умолчанию
        # В данном случае нужно заменить 'No field specified' на значение по умолчанию, если такие значения есть
        self.assertEqual(response_json['context'].get('goal', 'No goal specified'), 'No goal specified')
        self.assertEqual(response_json['context'].get('scope', 'No scope specified'), 'No scope specified')
        self.assertEqual(response_json['context'].get('lifecycle', 'No lifecycle specified'), 'No lifecycle specified')
        self.assertEqual(response_json['context'].get('customers', 'No customers specified'), 'No customers specified')

    def test_save_context_no_user_id(self):
        # Проверка на отсутствие user_id в запросе
        response = self.client.post('/save_context', json={
            'company_size': 'Large',
            'scope': 'Custom Software Development',
            'customers': 'IT',
            'department': 'Operations',
            'lifecycle': 'Startup',
            'goal': 'Performance Increasement',
            'market': 'Country'
        })
        self.assert400(response)
        self.assertEqual(response.json['error'], 'User ID is required')

    def test_save_user_history_multiple_messages(self):
        with patch('app.user_contexts', {'test_user': {
            'company_size': 'Large',
            'scope': 'Custom Software Development',
            'customers': 'IT',
            'department': 'Operations',
            'lifecycle': 'Startup',
            'goal': 'Performance Increasement',
            'market': 'Country'
        }}):
            # Создаем экземпляр клиента сокетов
            client = socketio.test_client(app)

            try:
                # Подключаемся к комнате и отправляем несколько сообщений
                client.emit('join_room', {'room': 'test_user'})
                client.emit('message', {'user_id': 'test_user', 'msg': 'First message'}, room='test_user')
                client.emit('message', {'user_id': 'test_user', 'msg': 'Second message'}, room='test_user')

                # Проверьте, что история сообщений была сохранена
                history_file = 'test_user_history.json'
                self.assertTrue(os.path.exists(history_file), "History file does not exist")
                
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    print("History content:", history)  # Для отладки
                    self.assertTrue(any(entry['content'] == 'First message' for entry in history),
                                    "Expected message 'First message' not found in history")
                    self.assertTrue(any(entry['content'] == 'Second message' for entry in history),
                                    "Expected message 'Second message' not found in history")
            
            finally:
                # Закрываем соединение и удаляем файл истории
                client.disconnect()
                if os.path.exists(history_file):
                    os.remove(history_file)

    def test_join_multiple_rooms(self):
        # Создаем экземпляр клиента сокетов
        client = socketio.test_client(app)
        
        try:
            # Подключаемся к нескольким комнатам
            client.emit('join_room', {'room': 'room1'})
            client.emit('join_room', {'room': 'room2'})
            
            # Проверяем, что было получено сообщение о присоединении в обе комнаты
            received = client.get_received()
            print("Received events:", received)  # Для отладки
            
            rooms_joined = []
            for event in received:
                if event['name'] == 'room_joined':
                    rooms_joined.append(event['args'][0]['room'])
            
            self.assertIn('room1', rooms_joined, "Room 'room1' not found in received data")
            self.assertIn('room2', rooms_joined, "Room 'room2' not found in received data")

        finally:
            # Закрываем соединение
            client.disconnect()

    def test_join_room_no_room_name(self):
        # Создаем экземпляр клиента сокетов
        client = socketio.test_client(app)
        
        try:
            # Пытаемся подключиться к комнате без указания имени
            client.emit('join_room', {})
            
            # Проверяем, что было получено сообщение об ошибке
            received = client.get_received()
            print("Received events:", received)  # Для отладки
            
            error_message_found = any('Error: Room ID is required' in str(event.get('args', [])) for event in received)
            self.assertTrue(error_message_found, "Expected error message not found in received data")
        
        finally:
            # Закрываем соединение
            client.disconnect()

    def test_handle_message_no_user_id(self):
        # Создаем экземпляр клиента сокетов
        client = socketio.test_client(app)

        try:
            # Пытаемся отправить сообщение без user_id
            client.emit('message', {'msg': 'Hello'}, room='test_room')

            # Проверяем, что было получено сообщение об ошибке
            received = client.get_received()
            print("Received events:", received)  # Для отладки
            
            error_message_found = any('Error: User ID is required or context not found' in str(event.get('args', [])) for event in received)
            self.assertTrue(error_message_found, "Expected error message not found in received data")
        
        finally:
            # Закрываем соединение
            client.disconnect()

    def test_generate_system_prompt_full_context(self):
        # Полный контекст с данными
        context = {
            "company_size": "Large",
            "scope": "Custom Software Development",
            "customers": "IT companies",
            "department": "Operations",
            "lifecycle": "Growth",
            "goal": "Increase efficiency",
            "market": "Global"
        }

        result = generate_system_prompt(context)

        assert context['company_size'] in result
        assert context['scope'] in result
        assert context['customers'] in result
        assert context['department'] in result
        assert context['lifecycle'] in result
        assert context['goal'] in result
        assert context['market'] in result

    def test_generate_system_prompt_invalid_context(self):
        # Некорректный контекст, где значения имеют неподходящий тип
        context = {
            "company_size": 123,  # Число вместо строки
            "scope": ["Software", "Development"],  # Список вместо строки
            "customers": {"key": "value"},  # Словарь вместо строки
            "department": None,  # None вместо строки
            "lifecycle": True,  # Булевое значение вместо строки
            "goal": False,  # Булевое значение вместо строки
            "market": "Global"
        }

        result = generate_system_prompt(context)
        context_strs = {k: str(v) for k, v in context.items()}

        # Проверяем, что результат содержит корректные преобразования в строки
        assert context_strs['company_size'] in result
        assert context_strs['scope'] in result
        assert context_strs['customers'] in result
        assert context_strs['department'] in result
        assert context_strs['lifecycle'] in result
        assert context_strs['goal'] in result
        assert context_strs['market'] in result

if __name__ == '__main__':
    pytest.main()
