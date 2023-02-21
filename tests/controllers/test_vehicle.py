from pytest import mark, param

from project.controllers.vehicle import Vehicle


@mark.parametrize('available_amps, charger_actual_current, charge_current_request_max, expected', {
    param(0, 0, 32, 0, id='no amps available'),
    param(44, 0, 32, 32, id='max amps available'),
    param(2, 31, 32, 32, id='surplus amps available'),
    param(-1, 32, 32, 31, id='less amps available'),
    param(-1, 0, 32, 0, id='deficit amps available'),
    param(44, 32, 16, 16, id='max request amps'),
})
def test_calculate_charging_amps(mocker, available_amps, charger_actual_current, charge_current_request_max, expected):
    mocker.patch('project.controllers.vehicle.VehicleModel.get_charger_actual_current',
                 return_value=charger_actual_current)
    mocker.patch('project.controllers.vehicle.VehicleModel.get_charge_current_request_max',
                 return_value=charge_current_request_max)
    vehicle = Vehicle()
    assert vehicle.calculate_charging_amps(available_amps) == expected


@mark.parametrize('charging_amps, is_disconnected, is_stopped, is_charging, stop_charge, start_charge', {
    param(0, None, None, True, True, False, id='stop charging'),
    param(0, None, None, False, False, False, id='not charging no op'),
    param(5, True, None, True, False, False, id='disconnected no op'),
    param(5, False, False, True, False, False, id='sync only'),
    param(5, False, True, False, False, True, id='start charging'),
})
def test_manage_vehicle(mocker, charging_amps, is_disconnected, is_stopped, is_charging, stop_charge, start_charge):
    mocker.patch('project.controllers.vehicle.VehicleModel.is_charging_state_disconnected',
                 return_value=is_disconnected)
    mocker.patch('project.controllers.vehicle.VehicleModel.is_charging_state_stopped',
                 return_value=is_stopped)
    mocker.patch('project.controllers.vehicle.VehicleModel.is_charging_state_charging',
                 return_value=is_charging)
    mock_stop_charge = mocker.patch('project.controllers.vehicle.Vehicle.stop_charge')
    mock_start_charge = mocker.patch('project.controllers.vehicle.Vehicle.start_charge')
    mock_sync_charge = mocker.patch('project.controllers.vehicle.Vehicle.sync_charging_amps')
    vehicle = Vehicle()
    vehicle.charging_amps = charging_amps
    vehicle.manage_vehicle()
    stop_charge_call_count = 1 if stop_charge else 0
    assert mock_stop_charge.call_count == stop_charge_call_count

    sync_charge_call_count = 1 if charging_amps >= 5 and not is_disconnected else 0
    assert mock_sync_charge.call_count == sync_charge_call_count

    start_charge_call_count = 1 if start_charge else 0
    assert mock_start_charge.call_count == start_charge_call_count
