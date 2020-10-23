import socket
import threading
import time
from typing import Any, Callable, List, Optional, Tuple, Union

# import cv2
import easytello.command
import easytello.error
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
    NON_RESPONSE_COMMANDS = [
        easytello.command.EMERGENCY,
        easytello.command.REMOTE_CONTROL
    ]

    @classmethod
    def is_non_response_command(cls, command: str) -> bool:
        return command.split()[0] in tuple(c.split()[0] for c in cls.NON_RESPONSE_COMMANDS)

    def send_command(self, command: str) -> Union[str, int]:
        raise NotImplementedError("Must override 'send_command' method when inheriting from BaseTello class.")

    def command(self) -> str:
        return self.send_command(easytello.command.COMMAND)

    def emergency(self) -> None:
        self.send_command(easytello.command.EMERGENCY)

    def takeoff(self) -> str:
        return self.send_command(easytello.command.TAKEOFF)

    def land(self) -> str:
        return self.send_command(easytello.command.LAND)

    def wait(self, seconds: float):
        # Displaying wait message (if 'debug' is True)
        if self.debug is True:
            print('Waiting {} seconds...'.format(seconds))
        # Log entry for delay added
        self.logs.append(CommandLog('wait'))
        # Delay is activated
        try:
            time.sleep(seconds)
        except KeyboardInterrupt:
            print("\nEMERGENCY LAND")
            self.land()

    # Movement commands
    def move(self, direction: str, distance: int) -> str:
        # if dist < 20 or dist > 500:
        #     raise ValueError(f"Distance for '{direction}' command must be between 20-500. Got {dist}.")
        return self.send_command(easytello.command.MOVE.format(direction=direction, distance=distance))

    def move_up(self, distance: int) -> str:
        return self.move(easytello.command.UP, distance)

    def move_down(self, distance: int) -> str:
        return self.move(easytello.command.DOWN, distance)

    def move_forward(self, distance: int) -> str:
        """Move Tello forward.

        Arguments:
            distance: The distance to move in centimeters.
                      Must be between 20 cm and 500 cm.

        Returns:
            Response string.
        """
        return self.move(easytello.command.FORWARD, distance)

    def move_backward(self, distance: int) -> str:
        return self.move(easytello.command.BACK, distance)

    def move_left(self, distance: int) -> str:
        return self.move(easytello.command.LEFT, distance)

    def move_right(self, distance: int) -> str:
        return self.move(easytello.command.RIGHT, distance)

    def rotate_right(self, degrees: int):
        self.send_command('cw {}'.format(degrees))

    def rotate_left(self, degrees: int):
        self.send_command('ccw {}'.format(degrees))

    def flip(self, direction: str):
        self.send_command('flip {}'.format(direction))

    # TODO: Rename to move? or move_to_point?
    # TODO: Consider translating so tello faces along y axis
    def go(self, x: int, y: int, z: int, speed: int = 10):
        """Move Tello to a point relative to the current position.

        Relative to the direction Tello is facing.
        Facing along the x axis.
        """
        self.send_command('go {} {} {} {}'.format(x, y, z, speed))

    # TODO: FIGURE OUT CURVE ??
    """
    (20, 50, 0), (0, 0, -50) - radius too large
    (20, 100, 20), (-20, -100, 20) - arc length too long

    (20, 50, 20), (-20, -50, 20) - to the cieling
    """
    def curve(self,
              point1: Tuple[int, int, int],
              point2: Tuple[int, int, int],
              speed: int = 10):
        """Fly the Tello in a curve from one point to the other.

        The points are in 3D space. The Tello will fly in a
        curve from (X^1, Y^1, Z^1) to (X^2, Y^2, Z^2).

        Individual x, y, z components must be between 20 and 500.

        Args:
            point1: The first point. (x, y, z).
            point2: The second point. (x, y, z).
            speed: How fast to move. Between 10 cm/s to 60 cm/s. 
        """
        x1, y1, z1 = point1
        x2, y2, z2 = point2

        self.send_command('curve {} {} {} {} {} {} {}'.format(x1, y1, z1, x2, y2, z2, speed))

    # Video commands
    def video_on(self) -> str:
        return self.send_command(easytello.command.STREAMON)

    # TODO: Better name
    def video_off(self) -> str:
        return self.send_command(easytello.command.STREAMOFF)

    # Set Commands
    def set_speed(self, speed: int):
        """Sets the speed of the aircraft.

        Args:
            speed: The value between 10-100.
        """
        self.send_command(easytello.command.SET_SPEED.format(speed=speed))

    def remote_control(self, roll: int = 0, pitch: int = 0,
                       elevation: int = 0, yaw: int = 0):
        """Set remote controller via four channels.

        Args:
            roll: left/right. -100 to 100.
            pitch: forward/back. -100 to 100.
            elevation: up/down. -100 to 100.
            yaw: clockwise rotation/counterclockwise rotation. -100 to 100.
        """
        return self.send_command(
            easytello.command.REMOTE_CONTROL.format(roll=roll,
                                                    pitch=pitch,
                                                    elevation=elevation,
                                                    yaw=yaw))

    def set_wifi(self, ssid: str, password: str):
        self.send_command(easytello.command.WIFI.format(ssid=ssid, password=password))

    # Read Commands
    def get_speed(self):
        return self.send_command('speed?')

    def get_battery(self) -> int:
        return self.send_command(easytello.command.GET_BATTERY)

    def get_time(self):
        return self.send_command('time?')

    def get_height(self):
        return self.send_command('height?')

    def get_temp(self):
        return self.send_command('temp?')

    def get_attitude(self):
        return self.send_command('attitude?')

    def get_baro(self):
        return self.send_command('baro?')

    def get_acceleration(self):
        return self.send_command('acceleration?')

    def get_tof(self):
        return self.send_command('tof?')

    def get_wifi(self):
        return self.send_command('wifi?')

    def get_sdk(self):
        # if self._sdk_version is None:
        #     return self.send_command('sdk?')
        # else:
        #     return self._sdk_version
        return self.send_command('sdk?')


class CommandLoggerMixin:
    """
    - send_command (override/wrap)
    - self.add_log_response(response: str)
    - self.last_log_item
    """
    logs: List[CommandLog] = []

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
    local_video_port: int = 11111
    MAX_TIMEOUT = 15
    _socket: Optional[socket.socket] = None
    _video_socket: Optional[socket.socket] = None
    _receive_thread: Optional[threading.Thread] = None
    _video_thread: Optional[threading.Thread] = None
    _response: Optional[str] = None
    _stop_thread = False
    _stop_video_thread = False

    def initialize_socket_manager(self) -> None:
        if self.tello_ip is None:
            self.tello_ip = '192.168.10.1'

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self.local_ip, self.local_port))

        self._receive_thread = threading.Thread(target=self._receive_thread_func)
        self._receive_thread.daemon = True
        self._receive_thread.start()

    def send_through_socket(self, command: str) -> None:
        self._socket.sendto(command.encode('utf-8'), (self.tello_ip, self.tello_port))

    def await_socket_response(self) -> str:
        start = time.time()
        while self._response is None:
            now = time.time()
            difference = now - start
            if difference > self.MAX_TIMEOUT:
                return "timeout"

        response = self._response
        self._response = None
        return str(response, encoding='utf-8')

    def _receive_thread_func(self):
        while self._stop_thread is False:
            # Checking for Tello response, throws socket error
            try:
                self._response = self._socket.recv(1024)
            except socket.error as exc:
                print('Socket error: {}'.format(exc))

    def stop_thread(self):
        self._stop_thread = True
        print("waiting for thread to close...", end=" ")
        self._receive_thread.join()
        print("done")

    def start_video_thread(self):
        self._video_recv_thread = threading.Thread(target=self._video_recv_thread_func)
        self._video_recv_thread.daemon = True
        self._video_recv_thread.start()

        self._video_render_thread = threading.Thread(target=self._video_render_thread_func)
        self._video_render_thread.daemon = True
        self._video_render_thread.start()

    def stop_video_thread(self):
        self._stop_video_thread = True
        self._video_recv_thread.join()
        self._video_render_thread.join()

    def _video_render_thread_func(self):
        while self._stop_video_thread is False:
            try:
                cv2.imshow('DJI Tello', self._frame)
            except cv2.error:
                pass

            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
        cv2.destroyAllWindows()

    def _video_recv_thread_func(self):
        cap = cv2.VideoCapture('udp://'+self.tello_ip+':11111')
        while self._stop_video_thread is False:
            _, self._frame = cap.read()

        cap.release()


class Tello(CommandLoggerMixin, SocketManagerMixin, BaseTello):
    ABORTABLE_RESPONSES = (
        easytello.error.TIMEOUT,
        easytello.error.NOT_JOYSTICK,
        easytello.error.NO_IMU,
        easytello.error.OUT_OF_RANGE,
        easytello.error.CURVE_RADIUS_TOO_LARGE,
        easytello.error.CURVE_COLINEAR,
        easytello.error.ARC_LENGTH_TOO_LONG
    )
    MAX_TIMEOUT = 10
    _frame = None

    def __init__(self, tello_ip: str = '192.168.10.1', debug: bool = True):
        self.tello_ip = tello_ip
        self.debug = debug
        self.initialize_socket_manager()
        self.command()

    def send_command(self, command: str) -> Union[str, int]:
        if self.debug is True:
            print(f"Command: {command}...", end=" ", flush=True)

        command_log = self.add_to_log(command)
        self.send_through_socket(command)

        if BaseTello.is_non_response_command(command):
            response = "sent"
        else:
            try:
                response = self.await_socket_response()
            except KeyboardInterrupt:
                if command == easytello.command.LAND:
                    print("\nEMERGENCY STOP")
                    self.emergency()
                else:
                    print("\nEMERGENCY LANDING")
                    self.land()
                print("stopping thread")
                self.stop_thread()
                exit()

        self.update_log(command_log, response)

        if self.debug is True:
            print(command_log.response)

        if (response in Tello.ABORTABLE_RESPONSES
                and command != easytello.command.LAND):
            print(f"\nEMERGENCY LANDING ({response})")
            self.land()
            exit()

        return command_log.response

    def video_on(self) -> str:
        self.start_video_thread()
        return super().video_on()

    def video_off(self) -> str:
        self.stop_video_thread()
        return super().video_off()
