import requests

from project.models.vehicle_model import VehicleModel

DEFAULT_TIMEOUT = 5


class Vehicle:
    """
    Controller for the electric vehicle
    """

    def __init__(self):
        self.charging_amps = None
        self.features = {}
        self.vehicle_model = VehicleModel()

    @staticmethod
    def start_charge():
        """
        Start EV charging
        :return: None
        """
        requests.get('http://127.0.0.1:5000/project_10th_street/start-charge', timeout=DEFAULT_TIMEOUT)

    @staticmethod
    def stop_charge():
        """
        Stop EV charging
        :return: None
        """
        requests.get('http://127.0.0.1:5000/project_10th_street/stop-charge', timeout=DEFAULT_TIMEOUT)

    @staticmethod
    def sync_charging_amps():
        """
        Set charging_amps on EV
        :return: None
        """
        requests.get('http://127.0.0.1:5000/project_10th_street/charging-amps', timeout=DEFAULT_TIMEOUT)

    @staticmethod
    def wake_up():
        """
        Send wake up to EV.  EV will not respond if the connection is idle for 60s
        :return: None
        """
        requests.get('http://127.0.0.1:5000/project_10th_street/wake-up', timeout=DEFAULT_TIMEOUT)

    def calculate_charging_amps(self, available_amps: int) -> int:
        """
        Calculate charging amps for EV based on current amps + available_amps.
        :param available_amps:  total amps available to charge EV
        :return: charging amps for EV in range from 0 to charge_current_request_max.
        """
        self.features['available_amps'] = available_amps

        charger_actual_current = self.vehicle_model.get_charger_actual_current()
        self.features['charger_actual_current'] = charger_actual_current

        charge_current_request_max = self.vehicle_model.get_charge_current_request_max()
        self.features['charge_current_request_max'] = charge_current_request_max

        self.charging_amps = max(min(charger_actual_current + available_amps, charge_current_request_max), 0)
        self.features['charging_amps'] = self.charging_amps
        return self.charging_amps

    def manage_vehicle(self) -> str:
        """
        Handles setting charging amps, start charging, or stop charging on EV depending on charging_amps and EV
        charge state.
        :return: result of handling
        """
        if self.vehicle_model.is_charging_state_disconnected():
            return "EV Disconnected"

        # Wake-up EV to avoid losing connection after 60s
        self.wake_up()

        self.sync_charging_amps()

        if self.vehicle_model.is_charging_state_stopped():
            if self.charging_amps >= 5 and self.vehicle_model.get_battery_range() < 60:
                self.start_charge()
                return "Start Charge"

        if self.vehicle_model.is_charging_state_charging():
            if self.charging_amps < 5:
                self.stop_charge()
                return "Stop Charge"

        return "Set Charge Amps"


vehicle_controller = Vehicle()
