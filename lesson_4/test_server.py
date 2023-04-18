import json
import unittest

from server import create_server_message, send_message, get_message


class TestSocket:
    def __init__(self, default_dict={"response": 200, "alert": "OK"}):
        self.dict = default_dict
        self.recever = None
        self.transmiter = None

    def accept(self):
        return self, 7777


    def send(self, message):
        self.transmiter = self.dict
        self.recever = json.loads(message.decode('utf-8'))

    def recv(self, max_length=1000000):
        return json.dumps(self.dict).encode('utf-8')


class TestClient(unittest.TestCase):
    def test_create_server_message(self):
        result = json.loads(create_server_message())
        self.assertEqual(result, {"response": 200, "alert": "OK"})

    def test_send_message(self):
        my_test_socket = TestSocket()
        send_message(my_test_socket, 200)
        self.assertEqual(my_test_socket.transmiter, my_test_socket.recever)

    def test_get_message(self):
        my_test_socket = TestSocket()
        result = get_message(my_test_socket)
        self.assertEqual(result, my_test_socket)


if __name__ == '__main__':
    unittest.main()
