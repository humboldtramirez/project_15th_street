from threading import Thread
from time import time
from typing import Any, Dict, Optional

import requests
from polling2 import is_value, poll, poll_decorator

from project.models.smart_charger_model import SmartChargerModel

DEFAULT_TIMEOUT = 5


class SmartChargerController:
    """
    Controller for the smart charger engine
    """

    is_polling_disabled = None
    daemon = None

    def __init__(self):
        self.smart_charger_model = SmartChargerModel()
        self.features = {}

    def get_charging_amps(self) -> int:
        """
        Get the most recent calculated charging amps.

        :return: calculated charging amps
        """
        return self.smart_charger_model.get_amps()

    def set_charging_amps(self, amps, model_name: str = 'scratch', features: dict = None):
        """
        Store calculated charging amps, name of model used for calculation, and model features in DB
        :param amps: calculated charging amps
        :param model_name: name of model used to calculate amps
        :param features: dictionary of features used to calculate amps
        :return: None
        """
        self.smart_charger_model.set_amps(amps, model_name, features)

    @poll_decorator(step=30, poll_forever=True)
    def poll_tesla_service(self):
        """
        Get latest battery and vehicle data, calculate available charging amps, and manage EV every 30s.

        Source: https://polling2.readthedocs.io/en/latest/examples.html#wrap-a-target-function-in-a-polling-decorator

        :return: is_polling_disabled
        """
        endpoint_name = None
        try:
            endpoint_name = 'battery'
            requests.get('http://127.0.0.1:5000/project_10th_street/battery', timeout=DEFAULT_TIMEOUT)
            endpoint_name = 'vehicle'
            requests.get('http://127.0.0.1:5000/project_10th_street/vehicle', timeout=DEFAULT_TIMEOUT)
            endpoint_name = 'battery-status'
            requests.get('http://127.0.0.1:5001/project_15th_street/battery-status', timeout=DEFAULT_TIMEOUT)
            endpoint_name = 'set-charging-amps'
            requests.get('http://127.0.0.1:5001/project_15th_street/set-charging-amps', timeout=DEFAULT_TIMEOUT)
            endpoint_name = 'manage-vehicle'
            requests.get('http://127.0.0.1:5001/project_15th_street/manage-vehicle', timeout=DEFAULT_TIMEOUT)
        except requests.exceptions.Timeout as e:
            print(f'polling timeout error {endpoint_name}: {e}')

        return self.is_polling_disabled

    def start_polling(self) -> None:
        """
        Start poll_tesla_service

        Source:
        https://superfastpython.com/thread-long-running-background-task/
        https://realpython.com/intro-to-python-threading/
        :return: None
        """
        self.is_polling_disabled = False
        self.daemon = Thread(target=self.poll_tesla_service, daemon=True, name='PollingSmartCharger')
        self.daemon.start()

    def status_polling(self) -> Optional[Dict[str, Any]]:
        """
        Get status of poll_tesla_service

        :return: ident, is_alive, name of poll_tesla_service thread
        """
        if self.daemon is None:
            return {}
        return {'ident': self.daemon.ident, 'is_alive': self.daemon.is_alive(), 'name': self.daemon.getName()}

    def stop_polling(self) -> None:
        """
        Stop poll_tesla_service

        :return: seconds elapsed to stop background task
        """
        start_time = time()
        self.is_polling_disabled = True
        local_daemon = Thread(target=self.status_daemon, daemon=True, name='PollingDaemonStatus')
        local_daemon.start()
        end_time = time()
        return int(end_time-start_time)

    def status_daemon(self) -> None:
        """
        Poll poll_tesla_service thread until its terminated

        :return: None
        """
        poll(target=self.daemon.is_alive, step=1, poll_forever=True, check_success=is_value(False))


smart_charger_controller = SmartChargerController()
