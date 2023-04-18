import json
import unittest

from client import create_client_message, send_message, get_message


class TestSocket:
    def __init__(self, default_dict={"action": 'presence', "time": 0, "type": "status",
                                     "user": {"account_name": "C0deMaver1ck", "status": "Yep, I am here!"}}):
        self.dict = default_dict
        self.dict['time'] = 0
        self.recever = None
        self.transmiter = None

    def send(self, message):
        self.transmiter = self.dict
        rec = json.loads(message.decode('utf-8'))
        rec['time'] = 0
        self.recever = rec

    def recv(self, max_length=1024):
        return json.dumps(self.dict).encode('utf-8')


class TestClient(unittest.TestCase):
    def test_create_client_message(self):
        result = json.loads(create_client_message())
        result['time'] = 0
        self.assertEqual(result, {"action": 'presence', "time": 0, "type": "status",
                                  "user": {"account_name": "C0deMaver1ck", "status": "Yep, I am here!"}})

    def test_send_message(self):
        my_test_socket = TestSocket()
        send_message(my_test_socket, create_client_message())
        self.assertEqual(my_test_socket.transmiter, my_test_socket.recever)

    def test_get_message(self):
        my_test_socket = TestSocket()
        result = get_message(my_test_socket)
        self.assertEqual(result, f'Получен ответ{json.loads(my_test_socket.recv().decode("utf-8"))}')


if __name__ == '__main__':
    unittest.main()
