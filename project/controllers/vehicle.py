import requests

from project.models.vehicle_model import VehicleModel


class Vehicle:

    def __init__(self):
        self.charging_amps = None
        self.features = {}
        self.vehicle_model = VehicleModel()

    @staticmethod
    def start_charge():
        requests.get('http://127.0.0.1:5000/project_10th_street/start-charge')

    @staticmethod
    def stop_charge():
        requests.get('http://127.0.0.1:5000/project_10th_street/stop-charge')

    @staticmethod
    def sync_charging_amps():
        requests.get('http://127.0.0.1:5000/project_10th_street/charging-amps')

    @staticmethod
    def update_vehicle_data():
        requests.get('http://127.0.0.1:5000/project_10th_street/vehicle')

    @staticmethod
    def wake_up():
        requests.get('http://127.0.0.1:5000/project_10th_street/wake-up')

    def calculate_charging_amps(self, available_amps: int) -> int:
        self.features['available_amps'] = available_amps

        charger_actual_current = self.vehicle_model.get_charger_actual_current()
        self.features['charger_actual_current'] = charger_actual_current

        charge_current_request_max = self.vehicle_model.get_charge_current_request_max()
        self.features['charge_current_request_max'] = charge_current_request_max

        self.charging_amps = max(min(charger_actual_current + available_amps, charge_current_request_max), 0)
        self.features['charging_amps'] = self.charging_amps
        return self.charging_amps

    def manage_vehicle(self):
        if self.charging_amps >= 5:
            if not self.vehicle_model.is_charging_state_disconnected():
                self.sync_charging_amps()

                if self.vehicle_model.is_charging_state_stopped():
                    self.start_charge()
        else:
            if self.vehicle_model.is_charging_state_charging():
                self.stop_charge()


vehicle_controller = Vehicle()
