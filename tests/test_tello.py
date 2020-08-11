from _pytest.python_api import _non_numeric_type_error
import pytest

import easytello

from .helpers import FakeSocketManagerMixin


class FakeTello(easytello.CommandLoggerMixin, FakeSocketManagerMixin, easytello.BaseTello):
    def send_command(self, command: str) -> str:
        command_log = self.add_to_log(command)
        self.send_through_socket(command)
        response = self.await_socket_response()
        self.update_log(command_log, response)
        return command_log.get_response()


def assert_move_limits(t: FakeTello, direction: str):
    with pytest.raises(ValueError) as excinfo:
        t.move(direction, 19)

    assert f"Distance for '{direction}' command" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        t.move(direction, 501)

    assert f"Distance for '{direction}' command" in str(excinfo.value)


def test_includes_appropriate_mixins():
    t = easytello.Tello()
    assert isinstance(t, easytello.BaseTello)
    assert isinstance(t, easytello.CommandLoggerMixin)
    assert isinstance(t, easytello.SocketManagerMixin)
    assert t.local_port == 8889
    assert t.tello_ip == '192.168.10.1'


def test_can_override_tello_ip():
    t = easytello.Tello(tello_ip='1.1.1.1')
    assert t.tello_ip == "1.1.1.1"


def test_send_command_creates_log():
    t = FakeTello()
    response = t.command()
    assert response == "ok"
    assert t.logs[-1].command == "command"


def test_command_gets_response():
    t = FakeTello()
    response = t.command()
    assert response == "ok"
    assert t.logs[-1].response == "ok"


def test_command_gets_forced_error_response():
    t = FakeTello()
    FakeSocketManagerMixin.force_response('error')
    t.command()
    assert t.logs[-1].response == "error"


def test_get_battery():
    t = FakeTello()
    FakeSocketManagerMixin.force_response('87')
    response = t.get_battery()
    assert response == 87


def test_distance_limits():
    t = FakeTello()
    directions = "up down forward back left right".split()
    for direction in directions:
        assert_move_limits(t, direction)


def test_up():
    t = FakeTello()
    t.up(50)
    assert t.logs[-1].command == "up 50"


def test_down():
    t = FakeTello()
    t.down(150)
    assert t.logs[-1].command == "down 150"


def test_forward():
    t = FakeTello()
    t.forward(77)
    assert t.logs[-1].command == "forward 77"


def test_back():
    t = FakeTello()
    t.back(33)
    assert t.logs[-1].command == "back 33"


def test_left():
    t = FakeTello()
    t.left(22)
    assert t.logs[-1].command == "left 22"


def test_right():
    t = FakeTello()
    t.right(66)
    assert t.logs[-1].command == "right 66"


def test_emergency():
    t = FakeTello()
    t.emergency()
    assert t.logs[-1].command == 'emergency'
    assert t.logs[-1].response == 'ok'


