from easytello.command_log import CommandLog
from typing import Tuple, Optional

from easytello import Tello

Address = Tuple[str, int]


class FakeLoggerMixin:
    def add_to_log(self, command: str) -> CommandLog:
        pass

    def update_log(self, command_log: CommandLog, response: str) -> None:
        pass


class FakeSocketManagerMixin:
    _forced_response: Optional[str] = None

    def send_through_socket(self, command: str) -> None:
        pass

    def await_socket_response(self) -> str:
        if FakeSocketManagerMixin._forced_response is not None:
            response = FakeSocketManagerMixin._forced_response
            FakeSocketManagerMixin._forced_response = None
            return response

        return "ok"

    @staticmethod
    def force_response(response: str) -> None:
        """For testing purposes"""
        FakeSocketManagerMixin._forced_response = response

# class FakeSocket:
#     def sendto(self, data: bytes, address: Address) -> int:
#         pass
#         # print(f"socket.sendto(): sending {data} to {address}")

#     def bind(self, address: Address):
#         self.bound_address = address

#     def recvfrom(self, bufsize: int) -> Tuple[bytes, Address]:
#         return (b'ok', self.bound_address)


# class FakeThread:
#     def join(self):
#         pass


# class FakeTello(Tello):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.socket = FakeSocket()
#         self.socket.bind((self.local_ip, self.local_port))
#         self.receive_thread = FakeThread()

#     def _create_and_bind_socket(self):
#         pass

#     def _initialize_response_thread(self):
#         pass

#     def _send_command(self, command: str):
#         self.log[-1].add_response('ok')

#     def _receive_thread(self):
#         while self._stop_thread is False:
#             # Checking for Tello response, throws socket error
#             try:
#                 self.response, ip = self.socket.recvfrom(1024)
#                 self.log[-1].add_response(self.response)
#             except IndexError as exc:
#                 pass


# Tello = FakeTello
