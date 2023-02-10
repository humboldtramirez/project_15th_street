from project.models.battery_model import BatteryModel

RECEPTACLE_V = 240


class Battery:

    def __init__(self):
        self.battery_model = BatteryModel()
        self.features = {}

    def get_available_amps(self):
        solar_power_watts = self.battery_model.get_power_reading().get('solar_power', 0)
        self.features['solar_power_watts'] = solar_power_watts
        battery_power_watts = self.battery_model.get_battery_power_watts()
        self.features['energy_left'] = battery_power_watts

        grid_power_watts = self.battery_model.get_grid_power_watt() if self.battery_model.get_grid_power_watt() > 8 else 0  # 8 is minimum import
        self.features['grid_power_watts'] = grid_power_watts

        load_power = self.battery_model.get_power_reading().get('load_power', 0)
        self.features['load_power'] = load_power

        # Basic Mode:  Round down to the nearest absolute watt.
        buffer_watts = 150
        self.features['buffer_watts'] = buffer_watts
        reserve_energy = self.battery_model.get_reserved_pack_energy() + buffer_watts
        self.features['reserved_pack_energy_watt'] = reserve_energy

        # Battery only discharges at most 4900 Watts
        available_battery_power_watts = min(battery_power_watts - reserve_energy,
                                            4900) if battery_power_watts > reserve_energy else 0
        self.features['available_battery_power_watts'] = available_battery_power_watts

        total_available_watts = solar_power_watts + available_battery_power_watts - load_power - grid_power_watts

        # solar + battery + load + grid = 0
        available_amp = total_available_watts // RECEPTACLE_V
        self.features['load_power'] = load_power
        self.features['solar_power_watts'] = solar_power_watts
        self.features['grid_power_watts'] = grid_power_watts
        self.features['total_available_watts'] = total_available_watts
        self.features['available_amp'] = available_amp
        print(f'features:\n{self.features}')
        return available_amp


battery_controller = Battery()
