from project.models.battery_model import BatteryModel

RECEPTACLE_V = 240
DISCHARGE_MAX_W = 4900  # Battery only discharges at most 4900 Watts (DISCHARGE_MAX_W)
MIN_IMPORT_W = 8  # minimum import from grid
MIN_W = 120  # Setting floor to run 120 W for 1 hour.


class Battery:

    def __init__(self):
        self.battery_model = BatteryModel()
        self.features = {}

    def get_available_battery_power_watts(self):
        """
        Basic Mode:  Round down to the nearest absolute watt.

        # Dryer Requirements:  240V, 30A or 7200W
        # Washer Requirements: 120V, 10A or 1200W
        # Laundry Req:  8.4kW
        # AC Req: ?
        # Powerwall Capacity:  13.5 kWh
        """
        energy_left_watts = self.battery_model.get_energy_left_watts()
        self.features['energy_left'] = energy_left_watts

        reserved_pack_energy_watt = self.battery_model.get_reserved_pack_energy()
        self.features['reserved_pack_energy_watt'] = reserved_pack_energy_watt

        # TODO:  Consider buffer to prevent grid import
        buffer_watt = 0
        reserve_energy_watt = reserved_pack_energy_watt + buffer_watt
        self.features['reserve_energy_watt'] = reserve_energy_watt

        # 'energy_left' value seems to update every 5 minutes so add W buffer to avoid pulling from grid before update
        is_battery_watt_available = energy_left_watts > reserve_energy_watt + (DISCHARGE_MAX_W // 60) * 5
        available_battery_power_watts = DISCHARGE_MAX_W if is_battery_watt_available else 0
        self.features['available_battery_power_watts'] = available_battery_power_watts
        return available_battery_power_watts

    def get_available_amps(self):
        solar_power_watts = self.battery_model.get_solar_power_watts()
        self.features['solar_power_watts'] = solar_power_watts

        grid_power_watts = self.battery_model.get_grid_power_watt()
        self.features['grid_power_watts'] = grid_power_watts

        load_power = self.battery_model.get_load_power()
        self.features['load_power'] = load_power

        available_battery_power_watts = self.get_available_battery_power_watts()

        total_available_watts = solar_power_watts + available_battery_power_watts - load_power - grid_power_watts
        self.features['total_available_watts'] = total_available_watts

        # solar + battery + load + grid = 0
        available_amp = total_available_watts // RECEPTACLE_V
        self.features['available_amp'] = available_amp

        return available_amp

    def get_status(self):
        # Remaining Calculations
        total_pack_energy = self.battery_model.get_total_pack_energy()
        self.features['total_pack_energy'] = total_pack_energy

        energy_left_watts = self.battery_model.get_energy_left_watts()
        self.features['energy_left'] = energy_left_watts

        battery_capacity_watts = self.battery_model.get_battery_capacity_watts()
        self.features['battery_capacity_watts'] = battery_capacity_watts

        battery_power_watts = self.battery_model.get_battery_power_watts()
        self.features['battery_power_watts'] = battery_power_watts

        remaining_charge_time = self.battery_model.get_remaining_charge_time()
        self.features['remaining_charge_time'] = remaining_charge_time

        remaining_discharge_time = self.battery_model.get_remaining_discharge_time()
        self.features['remaining_discharge_time'] = remaining_discharge_time

        if battery_power_watts < 0:
            status = 'Charging'
            time_remaining = f'{remaining_charge_time[0]}:{remaining_charge_time[1]}:{remaining_charge_time[2]}'
        elif battery_power_watts > 0:
            status = 'Discharging'
            time_remaining = \
                f'{remaining_discharge_time[0]}:{remaining_discharge_time[1]}:{remaining_discharge_time[2]}'
        else:
            status = 'Standby'
            time_remaining = None

        return {'status': status, 'time_remaining': time_remaining}


battery_controller = Battery()
