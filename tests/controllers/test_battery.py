from pytest import mark, param

from project.controllers.battery import Battery, DISCHARGE_MAX_W, MIN_IMPORT_W

TOTAL_PACK_ENERGY_W = 13098
RECOMMENDED_RESERVE_PACK_ENERGY_W = int(TOTAL_PACK_ENERGY_W * .20)
SOLAR_GEN_MAX = 5700  # Feb 2023 Record
HVAC_W = 1500
COFFEE_W = 1000
BATTERY_AVAILABLE_W = RECOMMENDED_RESERVE_PACK_ENERGY_W + (DISCHARGE_MAX_W // 60) * 5


@mark.parametrize('energy_left_watts, reserved_pack_energy_watt, expected', {
    param(0, 0, 0, id='zero battery'),
    param(RECOMMENDED_RESERVE_PACK_ENERGY_W, RECOMMENDED_RESERVE_PACK_ENERGY_W, 0, id='reserved'),
    param(BATTERY_AVAILABLE_W + 1, RECOMMENDED_RESERVE_PACK_ENERGY_W,
          DISCHARGE_MAX_W, id='battery available'),
    param(BATTERY_AVAILABLE_W - 1, RECOMMENDED_RESERVE_PACK_ENERGY_W, 0, id='battery unavailable'),
    param(TOTAL_PACK_ENERGY_W, RECOMMENDED_RESERVE_PACK_ENERGY_W, DISCHARGE_MAX_W, id='full battery'),
})
def test_get_available_battery_power_watts(mocker, energy_left_watts, reserved_pack_energy_watt, expected):
    mocker.patch('project.controllers.battery.BatteryModel.get_energy_left_watts', return_value=energy_left_watts)
    mocker.patch('project.controllers.battery.BatteryModel.get_reserved_pack_energy',
                 return_value=reserved_pack_energy_watt)
    battery = Battery()

    reserve_energy_watt = reserved_pack_energy_watt
    available_battery_power_watts = battery.get_available_battery_power_watts()
    assert available_battery_power_watts == expected
    assert battery.features.get('reserve_energy_watt') == reserve_energy_watt
    assert battery.features.get('available_battery_power_watts') == available_battery_power_watts


@mark.parametrize('solar_power_watts, available_battery_power_watts, grid_power_watts, load_power, expected', {
    param(0, 0, 0, 0, 0, id='min night time charge'),
    param(0, DISCHARGE_MAX_W, 0, 0, 20, id='max night time charge'),
    param(SOLAR_GEN_MAX, DISCHARGE_MAX_W, 0, 0, 44, id='max day time charge'),
    param(0, DISCHARGE_MAX_W, MIN_IMPORT_W, HVAC_W + COFFEE_W, 9, id='sunrise'),
    param(0, 0, MIN_IMPORT_W, HVAC_W + COFFEE_W, -11, id='am discharge'),
})
def test_get_available_amps(mocker, solar_power_watts, available_battery_power_watts, grid_power_watts, load_power,
                            expected):
    mocker.patch('project.controllers.battery.BatteryModel.get_solar_power_watts', return_value=solar_power_watts)
    mocker.patch('project.controllers.battery.Battery.get_available_battery_power_watts',
                 return_value=available_battery_power_watts)
    mocker.patch('project.controllers.battery.BatteryModel.get_grid_power_watt', return_value=grid_power_watts)
    mocker.patch('project.controllers.battery.BatteryModel.get_load_power', return_value=load_power)
    battery = Battery()
    available_amps = battery.get_available_amps()
    assert available_amps == expected


@mark.parametrize(
    'total_pack_energy, energy_left_watts, battery_capacity_watts, battery_power_watts, remaining_charge_time, '
    'remaining_discharge_time, expected', {
        param(None, None, None, -1, (1, 2, 3), None, ('Charging', '1:2:3'), id='Charging'),
        param(None, None, None, 1, None, (4, 5, 6), ('Discharging', '4:5:6'), id='Discharging'),
        param(None, None, None, 0, None, None, ('Standby', None), id='Standby'),
})
def test_get_status(mocker, total_pack_energy, energy_left_watts, battery_capacity_watts, battery_power_watts,
                    remaining_charge_time, remaining_discharge_time, expected):
    mocker.patch('project.controllers.battery.BatteryModel.get_total_pack_energy', return_value=total_pack_energy)
    mocker.patch('project.controllers.battery.BatteryModel.get_energy_left_watts', return_value=energy_left_watts)
    mocker.patch('project.controllers.battery.BatteryModel.get_battery_capacity_watts',
                 return_value=battery_capacity_watts)
    mocker.patch('project.controllers.battery.BatteryModel.get_battery_power_watts', return_value=battery_power_watts)
    mocker.patch('project.controllers.battery.BatteryModel.get_remaining_charge_time',
                 return_value=remaining_charge_time)
    mocker.patch('project.controllers.battery.BatteryModel.get_remaining_discharge_time',
                 return_value=remaining_discharge_time)
    battery = Battery()
    assert battery.get_status() == {'status': expected[0], 'time_remaining': expected[1]}
