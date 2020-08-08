from typing import Optional, Tuple

import pytest

from easytello import Tello


class WithFakeSocketMixin:
    class FakeSocket:
        Address = Tuple[str, int]

        def __init__(self):
            self.address: Optional[self.Address] = None

        def sendto(self, data: bytes, address: Address) -> int:
            self.address = address
            print(f"socket.sendto(): sending {data} to {address}")

        def recvfrom(self, bufsize: int) -> Tuple[bytes, Address]:
            return (b'ok', self.address)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = self.FakeSocket()


class FakeTello(WithFakeSocketMixin, Tello):
    pass

Tello = FakeTello


@pytest.mark.skip()
def test_create_tello_object():
    my_tello = Tello()
    assert my_tello.local_ip == ''
    assert my_tello.local_port == 8889


def test_tello_start():
    my_tello = Tello()
    my_tello.start()
    assert my_tello.log[-1].command == "command"
    my_tello.stop()

# query should not be a parameter to Tello.send_command.