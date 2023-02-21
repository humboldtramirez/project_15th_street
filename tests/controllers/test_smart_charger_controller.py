from unittest.mock import MagicMock

import pytest

from project.controllers.smart_charger_controller import SmartChargerController, SmartChargerModel


def test_get_charging_amps(mocker):
    mocker.patch('project.controllers.smart_charger_controller.SmartChargerModel.get_amps', return_value=5)
    smart_charger_controller = SmartChargerController()
    assert smart_charger_controller.get_charging_amps() == 5


@pytest.mark.skip
def test_set_charging_amps(mocker):
    mock_set_amps = mocker.patch('project.controllers.smart_charger_controller.SmartChargerModel.set_amps')
    smart_charger_controller = SmartChargerController()
    smart_charger_controller.smart_charger_model = MagicMock(spec=SmartChargerModel)
    smart_charger_controller.set_charging_amps(5, 'test', {})
    assert mock_set_amps.assert_called_once_with(5, 'test', {})
