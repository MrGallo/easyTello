from easytello.tello import Tello
import pytest
from mock import Mock
from typing import Union

import easytello


class TestTello(easytello.BaseTello):
    def send_command(self, command: str) -> Union[str, int]:
        """For testing purposes, simply return the command.

        The send_command would normally return response info.
        """
        return command


def test_child_class_must_override_send_command():
    class BadTello(easytello.BaseTello):
        pass

    bt = BadTello()
    with pytest.raises(NotImplementedError,
                       match="Must override 'send_command' .*"):
        bt.send_command("command")


def test_command_command():
    t = TestTello()
    response = t.command()
    assert response == "command"


def test_emergency_command():
    t = TestTello()
    response = t.emergency()
    assert response == "emergency"


def test_takeoff_command():
    t = TestTello()
    response = t.takeoff()
    assert response == "takeoff"


