from typing import Optional, Tuple

import pytest

from easytello import Tello


Address = Tuple[str, int]


class FakeSocket:
    def sendto(self, data: bytes, address: Address) -> int:
        pass
        # print(f"socket.sendto(): sending {data} to {address}")

    def bind(self, address: Address):
        self.bound_address = address

    def recvfrom(self, bufsize: int) -> Tuple[bytes, Address]:
        return (b'ok', self.bound_address)


class FakeTello(Tello):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = False
        self.socket = FakeSocket()
        self.socket.bind((self.local_ip, self.local_port))

    def _receive_thread(self):
        while self._stop_thread is False:
            # Checking for Tello response, throws socket error
            try:
                self.response, ip = self.socket.recvfrom(1024)
                self.log[-1].add_response(self.response)
            except IndexError as exc:
                pass


Tello = FakeTello


def test_create_tello_object():
    my_tello = Tello()
    assert my_tello.local_ip == ''
    assert my_tello.local_port == 8889


def test_tello_start():
    my_tello = Tello()
    my_tello.start()
    assert my_tello.log[-1].command == "command"
    my_tello.stop()


def test_context_manager():
    with Tello() as my_tello:
        assert my_tello.local_port == 8889
        assert isinstance(my_tello.socket, FakeSocket)
        assert my_tello.log[-1].command == "command"
        assert my_tello._stop_thread is False

    assert my_tello._stop_thread is True


# def test_sdk_version():
#     with Tello(sdk=Tello.SDK) as my_tello:
#         assert