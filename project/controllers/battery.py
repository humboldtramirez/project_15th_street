from typing import Dict, Any

from project.models.battery_model import BatteryModel

RECEPTACLE_V = 240
DISCHARGE_MAX_W = 4900  # Battery only discharges at most 4900 Watts (DISCHARGE_MAX_W)
MIN_IMPORT_W = 8  # minimum import from grid
MIN_W = 120  # Setting floor to run 120 W for 1 hour.


class Battery:
    """
    Controller for the home energy storage system
    """

    def __init__(self):
        self.battery_model = BatteryModel()
        self.features = {}

    def get_available_battery_power_watts(self) -> int:
        """
        Get Watts available from the battery without consuming the reserved amount.  Available Watts is determined by
        energy left on the battery, reserve amount, and a buffer amount.  The buffer amount prevents the system from
        overestimating the available watts resulting in unnecessary import from the grid.

        :return: DISCHARGE_MAX_W if Watts from the battery is available else 0
        """
        energy_left_watts = self.battery_model.get_energy_left_watts()
        self.features['energy_left'] = energy_left_watts

        reserved_pack_energy_watt = self.battery_model.get_reserved_pack_energy()
        self.features['reserved_pack_energy_watt'] = reserved_pack_energy_watt

        # 'energy_left' value seems to update every 5 minutes so add W buffer to avoid pulling from grid before update
        buffer_watt = (DISCHARGE_MAX_W // 60) * 5
        reserve_energy_watt = reserved_pack_energy_watt + buffer_watt
        self.features['reserve_energy_watt'] = reserve_energy_watt

        is_battery_watt_available = energy_left_watts > reserve_energy_watt
        available_battery_power_watts = DISCHARGE_MAX_W if is_battery_watt_available else 0
        self.features['available_battery_power_watts'] = available_battery_power_watts
        return available_battery_power_watts

    def get_available_amps(self) -> int:
        """
        Get amps available (A) to charge EV without importing W from the grid.  'A' is based on Watts available
        from solar generation and battery storage minus Watts from existing load and grid import.  If 'A' > 0
        then the system can increase the EV's charging amps by 'A' without importing W from the grid.  If amps < 0 then
        the system must decrease the EV's charging amps by 'A' or risk importing W from the grid.

        :return: available amps
        """
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

    def get_status(self) -> Dict[str, Any]:
        """
        Gets current status and time remaining for the battery.  Status of the battery is either 'Charging',
        'Discharging', or 'Standby'.  Time remaining is the hours:minutes:seconds before the battery is done charging
        or discharging depending on status.

        :return: a dictionary containing the battery status and time remaining (h:m:s)
        """

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
