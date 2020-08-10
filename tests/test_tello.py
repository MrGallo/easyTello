import easytello


from .helpers import FakeSocketManagerMixin


class FakeTello(easytello.CommandLoggerMixin, FakeSocketManagerMixin, easytello.BaseTello):
    def send_command(self, command: str) -> str:
        command_log = self.add_to_log(command)
        self.send_through_socket(command)
        response = self.await_socket_response()
        self.update_log(command_log, response)
        return command_log.get_response()


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
