"""Dyson Pure Link Device Logic"""

import base64, json, hashlib, os, time, yaml
import paho.mqtt.client as mqtt

#from Queue import Queue, Empty
import queue, empty

from value_types import CONNECTION_STATE, DISCONNECTION_STATE, FanMode, StandbyMonitoring, ConnectionError, DisconnectionError, SensorsData, StateData

class DysonPureLink(object):
    """Plugin to connect to Dyson Pure Link device and get its sensors readings"""

    def __init__(self):
        self.client = None
        self.config = None
        self.connected = queue.Queue()
        self.disconnected = queue.Queue()
        self.state_data_available = queue.Queue()
        self.sensor_data_available = queue.Queue()
        self.sensor_data = None
        self.state_data = None
        self._is_connected = None

    @property
    def has_valid_data(self):
        return self.sensor_data and self.sensor_data.has_data

    @property
    def password(self):
        return self.config['DYSON_PASSWORD']

    @property
    def serial_number(self):
        return self.config['DYSON_SERIAL']

    @property
    def device_type(self):
        return self.config['DYSON_TYPE']

    @property
    def ip_address(self):
        return self.config['DYSON_IP']

    @property
    def port_number(self):
        return self.config['DYSON_PORT']

    @property
    def device_command(self):
        return '{0}/{1}/command'.format(self.device_type, self.serial_number)

    @property
    def device_status(self):
        return '{0}/{1}/status/current'.format(self.device_type, self.serial_number)

    @staticmethod
    def on_connect(client, userdata, flags, return_code):
        """Static callback to handle on_connect event"""
        # Connection is successful with return_code: 0
        if return_code:
            userdata.connected.put_nowait(False)
            raise ConnectionError(return_code)

        # We subscribe to the status message
        client.subscribe(userdata.device_status)
        userdata.connected.put_nowait(True)

    @staticmethod
    def on_disconnect(client, userdata, return_code):
        """Static callback to handle on_disconnect event"""
        if return_code:
            raise DisconnectionError(return_code)

        userdata.disconnected.put_nowait(True)

    @staticmethod
    def on_message(client, userdata, message):
        """Static callback to handle incoming messages"""
        payload = message.payload.decode("utf-8")
        json_message = json.loads(payload)
        
        if StateData.is_state_data(json_message):
            userdata.state_data_available.put_nowait(StateData(json_message))

        if SensorsData.is_sensors_data(json_message):
            userdata.sensor_data_available.put_nowait(SensorsData(json_message))

    def _request_state(self):
        """Publishes request for current state message"""
        if self.client:
            command = json.dumps({
                    'msg': 'REQUEST-CURRENT-STATE',
                    'time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
            
            self.client.publish(self.device_command, command)

    def _change_state(self, data):
        """Publishes request for change state message"""
        if self.client:
            
            command = json.dumps({
                'msg': 'STATE-SET',
                'time': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'mode-reason': 'LAPP',
                'data': data
            })

            self.client.publish(self.device_command, command, 1)

            self.state_data = self.state_data_available.get(timeout=5)

    def _hashed_password(self):
        """Hash password (found in manual) to a base64 encoded of its shad512 value"""
        hash = hashlib.sha512()
        hash.update(self.password.encode('utf-8'))
        return base64.b64encode(hash.digest()).decode('utf-8')

    def parse_config(self):
        """Parses config file if any"""
        file_name = '{}/dyson_pure_link.yaml'.format(os.path.dirname(os.path.abspath(__file__)))

        if os.path.isfile(file_name):
            self.config = yaml.safe_load(open(file_name))

        return self.config
        
    def connect_device(self):
        """
        Connects to device using provided connection arguments

        Returns: True/False depending on the result of connection
        """

        self.client = mqtt.Client(clean_session=True, protocol=mqtt.MQTTv311, userdata=self)
        self.client.username_pw_set(self.serial_number, self._hashed_password())
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.connect(self.ip_address, port=self.port_number)
        self.client.loop_start()

        self._is_connected = self.connected.get(timeout=10)

        if self._is_connected:
            self._request_state()

            self.state_data = self.state_data_available.get(timeout=5)
            self.sensor_data = self.sensor_data_available.get(timeout=5)

            # Return True in case of successful connect and data retrieval
            return True

        # If any issue occurred return False
        self.client = None
        return False

    def set_fan_speed(self, speed):
        """Changes fan speed: 1-10"""
        if speed.lower() == 'up':
            p_speed = int(self.state_data.speed) + 1
        elif speed.lower() == 'down':
            p_speed = int(self.state_data.speed) - 1
        else:
            p_speed = int(speed)

        if self._is_connected:
            self._change_state({'fnsp': p_speed})

    def set_oscillation(self, mode):
        """Changes oscillation: ON|OFF"""
        if self._is_connected:
            self._change_state({'oson': mode.upper()})
    def set_fan_mode(self, mode):
        """Changes fan mode: ON|OFF|AUTO"""
        if self._is_connected:
            self._change_state({'fmod': mode.upper()})

    def set_standby_monitoring(self, mode):
        """Changes standby monitoring: ON|OFF"""
        if self._is_connected:
            self._change_state({'rhtm': mode.upper()})

    def get_data(self):
        return (self.state_data, self.sensor_data) if self.has_valid_data else tuple()

    def disconnect_device(self):
        """Disconnects device and return the boolean result"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            
            # Wait until we get on disconnect message
            return self.disconnected.get(timeout=5)
