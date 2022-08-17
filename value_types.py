"""Value types, enums and mappings package"""

# Map for connection return code and its meaning
CONNECTION_STATE = {
    0: 'Connection successful',
    1: 'Connection refused: incorrect protocol version',
    2: 'Connection refused: invalid client identifier',
    3: 'Connection refused: server unavailable',
    4: 'Connection refused: bad username or password',
    5: 'Connection refused: not authorised',
    99: 'Connection refused: timeout'
}

DISCONNECTION_STATE = {
    0: 'Disconnection successful',
    50: 'Disconnection error: unexpected error',
    99: 'Disconnection error: timeout'
}

class FanMode(object):
    """Enum for fan mode"""

    OFF = 'OFF'
    ON = 'FAN'
    AUTO = 'AUTO'

class StandbyMonitoring(object):
    """Enum for monitor air quality when on standby"""

    ON = 'ON'
    OFF = 'OFF'

"""Custom Errors"""

class ConnectionError(Exception):
    """Custom error to handle connect device issues"""

    def __init__(self, return_code, *args):
        super(ConnectionError, self).__init__(*args)
        self.message = CONNECTION_STATE[return_code]

class DisconnectionError(Exception):
    """Custom error to handle disconnect device issues"""
    def __init__(self, return_code, *args):
        super(DisconnectionError, self).__init__(*args)
        self.message = DISCONNECTION_STATE[return_code] if return_code in DISCONNECTION_STATE else DISCONNECTION_STATE[50]

class SensorsData(object):
    """Value type for sensors data"""

    def __init__(self, message):
        data = message['data']
        humidity = data['hact']
        temperature = data['tact']
        volatile_compounds = data['vact']
        particles = data['pact']


        self.humidity = None if humidity == 'OFF' else int(humidity)
        self.temperature = None if temperature == 'OFF' else self.kelvin_to_fahrenheit(float(temperature) / 10)
        self.volatile_compounds = 0 if volatile_compounds == 'OFF' or volatile_compounds == 'INIT' else int(
            volatile_compounds)
        self.particles = 0 if particles == 'OFF' or particles == 'INIT' else int(particles)

    def __repr__(self):
        """Return a String representation"""
        return 'Temperature: {0} F, Humidity: {1} %, Volatile Compounds: {2}, Particles: {3}'.format(
            self.temperature, self.humidity, self.volatile_compounds, self.particles)

    @property
    def has_data(self):
        return self.temperature is not None or self.humidity is not None

    @staticmethod
    def is_sensors_data(message):
        return message['msg'] in ['ENVIRONMENTAL-CURRENT-SENSOR-DATA']

    @staticmethod
    def kelvin_to_fahrenheit (kelvin_value):
        return kelvin_value * 9 / 5 - 459.67

class StateData(object):
    """Value type for state data"""

    def __init__(self, message):
        data = message['product-state']

        self.fan_mode = self._get_field_value(data['fmod'])
        self.fan_state = self._get_field_value(data['fnst'])
        self.night_mode = self._get_field_value(data['nmod'])
        self.speed = self._get_field_value(data['fnsp'])
        self.oscillation = self._get_field_value(data['oson'])
        self.filter_life = self._get_field_value(data['filf'])
        self.quality_target = self._get_field_value(data['qtar'])
        self.standby_monitoring = self._get_field_value(data['rhtm'])

    def __repr__(self):
        """Return a String representation"""
        return 'Fan mode: {0}, Oscillation: {1}, Filter life: {2}, Standby monitoring: {3}, Fan speed: {4}'.format(
            self.fan_mode, self.oscillation, self.filter_life, self.standby_monitoring, self.speed, )

    @staticmethod
    def _get_field_value(field):
        """Get field value"""
        return field[-1] if isinstance(field, list) else field

    @staticmethod
    def is_state_data(message):
        return message['msg'] in ['CURRENT-STATE', 'STATE-CHANGE']
