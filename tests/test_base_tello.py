# TODO: Evaluate necessity of this test file.

# from typing import Union

# import easytello

# from .helpers import FakeLoggerMixin, FakeSocketManagerMixin


# class Tello(FakeLoggerMixin,
#             FakeSocketManagerMixin,
#             easytello.BaseTello):
#     def __init__(self, tello_ip: str = '192.168.10.1', debug: bool = True):
#         self.tello_ip = tello_ip
#         self.debug = debug

#     def send_command(self, command: str) -> Union[str, int]:
#         command_log = self.add_to_log(command)
#         self.send_through_socket(command)
#         response = self.await_socket_response()
#         self.update_log(command_log, response)
#         return command_log.get_response()


# def test_command_constants():
#     assert easytello.command.COMMAND == "command"
#     assert easytello.command.TAKEOFF == "takeoff"


# def test_inherits_from_base_tello():
#     my_tello = Tello()
#     assert isinstance(my_tello, easytello.BaseTello)


# def test_command():
#     my_tello = Tello()
#     response = my_tello.command()
#     assert response == "ok"


# def test_takeoff():
#     my_tello = Tello()
#     response = my_tello.takeoff()
#     assert response == "ok"


# def test_land():
#     my_tello = Tello()
#     response = my_tello.land()
#     assert response == "ok"
