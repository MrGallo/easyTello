import socket
import threading
import time
from typing import Any, Callable, List, Optional, Tuple, Union

import cv2
import easytello.command as command
from easytello.command_log import CommandLog

Address = Tuple[str, int]


class BaseTello:
    """
    - command
    - takeoff
    - land
    - send_command
    - etc.
    """
    def send_command(self, command: str) -> Union[str, int]:
        raise NotImplementedError

    def command(self) -> str:
        return self.send_command(command.COMMAND)

    def takeoff(self) -> str:
        return self.send_command(command.TAKEOFF)

    def land(self) -> str:
        return self.send_command(command.LAND)

    def get_battery(self) -> int:
        return self.send_command(command.GET_BATTERY)


class CommandLoggerMixin:
    """
    - send_command (override/wrap)
    - self.add_log_response(response: str)
    - self.last_log_item
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logs: List[CommandLog] = []

    def add_to_log(self, command: str) -> CommandLog:
        log = CommandLog(command)
        self.logs.append(log)
        return log

    def update_log(self, command_log: CommandLog, response: str) -> None:
        command_log.add_response(response)


class SocketManagerMixin:
    local_ip: str = ''
    local_port: int = 8889
    tello_port: int = 8889
    tello_ip: Optional[str] = None
    MAX_TIME_OUT = 15
    _socket: Optional[socket.socket] = None
    _receive_thread: Optional[threading.Thread] = None
    _response: Optional[str] = None
    _stop_thread = False

    def send_through_socket(self, command: str) -> None:
        if self.tello_ip is None:
            self.tello_ip = '192.168.10.1'

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self.local_ip, self.local_port))

        self._receive_thread = threading.Thread(target=self._receive_thread_func)
        self._receive_thread.daemon = True
        self._receive_thread.start()

        self.send_through_socket = self._send_through_socket
        self.send_through_socket(command)

    def _send_through_socket(self, command: str) -> None:
        self._socket.sendto(command.encode('utf-8'), (self.tello_ip, self.tello_port))

    def await_socket_response(self) -> str:
        start = time.time()
        while self._response is None:
            now = time.time()
            difference = now - start
            if difference > self.MAX_TIME_OUT:
                print('Connection timed out!')
                break

        response = self._response
        self._response = None
        return response

    def _receive_thread_func(self):
        while self._stop_thread is False:
            # Checking for Tello response, throws socket error
            try:
                self._response, _ = self.socket.recvfrom(1024)
            except socket.error as exc:
                print('Socket error: {}'.format(exc))

    def stop_thread(self):
        self._stop_thread = True
        print("waiting for thread to close...", end=" ")
        self._receive_thread.join()
        print("done")


class TelloOld:
    class Direction:
        UP = "up"
        DOWN = "down"
        FORWARD = "forward"
        BACK = "back"
        LEFT = "left"
        RIGHT = "right"

    def __init__(self, tello_ip: str = '192.168.10.1', debug: bool = False):
        self.local_ip = ''
        self.local_port = 8889
        self.socket: Optional[socket.socket] = None
        self._sdk_version: Optional[str] = None

        # Setting Tello ip and port info
        self.tello_ip = tello_ip
        self.tello_port = 8889
        self.tello_address = (self.tello_ip, self.tello_port)
        self.log: List[CommandLog] = []
        self.receive_thread: Optional[threading.Thread] = None

        # easyTello runtime options
        self._stop_thread = False
        self.stream_state = False
        self.MAX_TIME_OUT = 15
        self.debug = debug

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, tb):
        self.stop()

    def start(self):
        """Initiate sequence to allow the Tello to send and recieve commands and data."""
        if self.socket is None:
            self._create_and_bind_socket()

        self._initialize_response_thread()

        # Setting Tello to command mode
        response = self.command()
        self.debug_print(response)

        self._check_sdk_version()

    def _create_and_bind_socket(self):
        # Open local UDP port on 8889 for Tello communication
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.local_ip, self.local_port))

    def _initialize_response_thread(self):
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def _check_sdk_version(self):
        sdk_response = self.get_sdk()
        if "unknown command" in sdk_response:
            self._sdk_version = "1.3"
        else:
            self._sdk_version = sdk_response

        self.debug_print(f"SDK Version: {self._sdk_version}")

    def debug_print(self, msg: str):
        if self.debug is True:
            print(msg)

    def stop(self):  # TODO: name conflict with SDK 2.0 'stop' command
        self._stop_thread = True
        self.receive_thread.join()

    # TODO: # query should not be a parameter to Tello.send_command.
    def send_command(self, command: str, query: bool = True) -> Union[str, int]:
        # New log entry created for the outbound command
        self.log.append(CommandLog(command))

        # Sending command to Tello
        self._send_command(command)
        # Displaying conformation message (if 'debug' os True)
        if self.debug is True:
            print('Sending command: {}'.format(command))

        if self._sdk_version == "1.3":
            NON_RESPONSE_COMMANDS = "emergency rc".split()
            if command.split()[0] in NON_RESPONSE_COMMANDS:
                self.log[-1].add_response("sent")

        # Checking whether the command has timed out or not (based on value in 'MAX_TIME_OUT')
        start = time.time()
        try:
            while not self.log[-1].got_response():  # Runs while no repsonse has been received in log
                now = time.time()
                difference = now - start
                if difference > self.MAX_TIME_OUT:
                    print('Connection timed out!')
                    break
        except KeyboardInterrupt:
            print("EMERGENCY STOP")
            self._send_command('emergency')
            exit()

        # Prints out Tello response (if 'debug' is True)
        if self.debug is True and query is False:
            print('Response: {}'.format(self.log[-1].get_response()))

        return self.log[-1].get_response()

    def _send_command(self, command: str):
        self.socket.sendto(command.encode('utf-8'), self.tello_address)

    def _receive_thread(self):
        while self._stop_thread is False:
            # Checking for Tello response, throws socket error
            try:
                self.response, ip = self.socket.recvfrom(1024)
                self.log[-1].add_response(self.response)
            except socket.error as exc:
                print('Socket error: {}'.format(exc))

    def _video_thread(self):
        # Creating stream capture object
        cap = cv2.VideoCapture('udp://'+self.tello_ip+':11111')
        # Runs while 'stream_state' is True
        while self.stream_state:
            ret, frame = cap.read()
            cv2.imshow('DJI Tello', frame)

            # Video Stream is closed if escape key is pressed
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    def wait(self, delay: float):
        # Displaying wait message (if 'debug' is True)
        if self.debug is True:
            print('Waiting {} seconds...'.format(delay))
        # Log entry for delay added
        self.log.append(CommandLog('wait'))
        # Delay is activated
        time.sleep(delay)

    def get_log(self):
        return self.log

    # Control Commands
    def command(self):
        return self.send_command('command')

    def takeoff(self):
        self.send_command('takeoff')

    def land(self, override_rc=True):
        if override_rc is True:  # otherwise it will keep rc settings
            self.remote_control()
        self.send_command('land')

    def streamon(self):
        self.send_command('streamon')
        self.stream_state = True
        self.video_thread = threading.Thread(target=self._video_thread)
        self.video_thread.daemon = True
        self.video_thread.start()

    def streamoff(self):
        self.stream_state = False
        self.send_command('streamoff')

    def emergency(self):
        return self.send_command('emergency')

    # Movement Commands
    def up(self, dist: int):
        return self._move(Tello.Direction.UP, dist)

    def down(self, dist: int):
        return self._move(Tello.Direction.DOWN, dist)

    def left(self, dist: int):
        return self._move(Tello.Direction.LEFT, dist)

    def right(self, dist: int):
        return self._move(Tello.Direction.RIGHT, dist)

    def forward(self, dist: int):
        return self._move(Tello.Direction.FORWARD, dist)

    def back(self, dist: int):
        return self._move(Tello.Direction.BACK, dist)

    def _move(self, direction: str, dist: int):
        self._assertDistanceValue(direction, dist)
        return self.send_command(f'{direction} {dist}')

    def _assertDistanceValue(self, direction: str, dist: int) -> None:
        if dist < 20 or dist > 500:
            raise ValueError(f"{direction.capitalize()} distance must be 20-500.")

    def cw(self, degr: int):
        self.send_command('cw {}'.format(degr))

    def ccw(self, degr: int):
        self.send_command('ccw {}'.format(degr))

    def flip(self, direc: str):
        self.send_command('flip {}'.format(direc))

    def go(self, x: int, y: int, z: int, speed: int):
        self.send_command('go {} {} {} {}'.format(x, y, z, speed))

    def curve(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int, speed: int):
        self.send_command('curve {} {} {} {} {} {} {}'.format(x1, y1, z1, x2, y2, z2, speed))

    # Set Commands
    def set_speed(self, speed: int):
        self.send_command('speed {}'.format(speed))

    def remote_control(self, roll: int = 0, pitch: int = 0,
                       elevation: int = 0, yaw: int = 0):
        """Set remote controller via four channels.

        Args:
            roll: left/right. -100 to 100.
            pitch: forward/back. -100 to 100.
            elevation: up/down. -100 to 100.
            yaw: clockwise rotation/counterclockwise rotation. -100 to 100.
        """
        return self.send_command(f"rc {roll} {pitch} {elevation} {yaw}")

    def set_wifi(self, ssid: str, passwrd: str):
        self.send_command('wifi {} {}'.format(ssid, passwrd))

    # Read Commands
    def get_speed(self):
        self.send_command('speed?', True)
        return self.log[-1].get_response()

    def get_battery(self):
        self.send_command('battery?', True)
        return self.log[-1].get_response()

    def get_time(self):
        self.send_command('time?', True)
        return self.log[-1].get_response()

    def get_height(self):
        self.send_command('height?', True)
        return self.log[-1].get_response()

    def get_temp(self):
        self.send_command('temp?', True)
        return self.log[-1].get_response()

    def get_attitude(self):
        self.send_command('attitude?', True)
        return self.log[-1].get_response()

    def get_baro(self):
        self.send_command('baro?', True)
        return self.log[-1].get_response()

    def get_acceleration(self):
        self.send_command('acceleration?', True)
        return self.log[-1].get_response()

    def get_tof(self):
        self.send_command('tof?', True)
        return self.log[-1].get_response()

    def get_wifi(self):
        self.send_command('wifi?', True)
        return self.log[-1].get_response()

    def get_sdk(self):
        if self._sdk_version is None:
            return self.send_command('sdk?', True)
        else:
            return self._sdk_version


class Tello(CommandLoggerMixin, SocketManagerMixin, BaseTello):
    def __init__(self, tello_ip: str = '192.168.10.1', debug: bool = True):
        self.tello_ip = tello_ip
        self.debug = debug

        if self.debug is True:
            self.send_command = self._print_wrap_send_command(self.send_command)

    def send_command(self, command: str) -> Union[str, int]:
        command_log = self.add_to_log(command)
        self.send_through_socket(command)

        try:
            response = self.await_socket_response()
        except KeyboardInterrupt:
            print("EMERGENCY STOP")
            self.send_through_socket('emergency')
            self.stop_thread()
            exit()

        self.update_log(command_log, response)

        return command_log.get_response()

    def _print_wrap_send_command(self, func) -> Callable:
        def wrapper(self, *args, **kwargs) -> Union[str, int]:
            print(f"Command: {command}...", end=" ")
            result = func(*args, **kwargs)
            print(result)
        return wrapper
