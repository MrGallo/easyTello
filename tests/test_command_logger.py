import easytello


class Tello(easytello.CommandLoggerMixin):
    pass


def test_has_empty_logs():
    t = Tello()
    assert type(t.logs) is list
    assert len(t.logs) == 0


def test_add_to_log():
    t = Tello()
    t.add_to_log(easytello.command.COMMAND)
    assert t.logs[-1].command == easytello.command.COMMAND


