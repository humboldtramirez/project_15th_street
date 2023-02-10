from project.models.vehicle_model import VehicleModel


class Vehicle:

    def __init__(self):
        self.vehicle_model = VehicleModel()
        self.features = {}

    def get_charger_actual_current(self) -> int:
        charger_actual_current = self.vehicle_model.get_charger_actual_current()
        self.features['charger_actual_current'] = charger_actual_current
        print(f'features:\n{self.features}')
        return charger_actual_current


vehicle_controller = Vehicle()
