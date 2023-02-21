from http import HTTPStatus
from threading import Thread
from time import time

from flask import current_app
import requests
from polling2 import is_value, poll, poll_decorator

from project.models.smart_charger_model import SmartChargerModel


class SmartChargerController:
    polling_disabled = None
    daemon = None

    def __init__(self):
        self.smart_charger_model = SmartChargerModel()
        self.features = {}

    def get_charging_amps(self) -> int:
        return self.smart_charger_model.get_amps()

    def set_charging_amps(self, amps, ai_model: str = 'scratch', features: dict = None):
        self.smart_charger_model.set_amps(amps, ai_model, features)

    @poll_decorator(step=30, poll_forever=True)
    def poll_tesla_service(self):
        """
        Source: https://polling2.readthedocs.io/en/latest/examples.html#wrap-a-target-function-in-a-polling-decorator
        :return:
        """
        requests.get('http://127.0.0.1:5000/project_10th_street/battery')
        requests.get('http://127.0.0.1:5000/project_10th_street/vehicle')
        requests.get('http://127.0.0.1:5001/project_15th_street/battery-status')
        requests.get('http://127.0.0.1:5001/project_15th_street/set-charging-amps')
        requests.get('http://127.0.0.1:5001/project_15th_street/manage-vehicle')
        return self.polling_disabled

    def start_polling(self):
        """
        Source:
        https://superfastpython.com/thread-long-running-background-task/
        https://realpython.com/intro-to-python-threading/

        :return:
        """
        self.polling_disabled = False
        current_app.logger.info('Starting background task ...')
        self.daemon = Thread(target=self.poll_tesla_service, daemon=True, name='PollingSmartCharger')
        self.daemon.start()
        return HTTPStatus.OK

    def status_polling(self) -> dict:
        if self.daemon is None:
            return {}
        current_app.logger.info(f'is_alive: {self.daemon.is_alive()}')
        current_app.logger.info(f'ident: {self.daemon.ident}')
        current_app.logger.info(f'name: {self.daemon.getName()}')
        return {'ident': self.daemon.ident, 'is_alive': self.daemon.is_alive(), 'name': self.daemon.getName()}

    def stop_polling(self) -> int:
        current_app.logger.info('Stopping background task ...')
        self.polling_disabled = True
        start_time = time()
        local_daemon = Thread(target=self.status_daemon, args=(start_time,), daemon=True, name='PollingDaemonStatus')
        local_daemon.start()
        return HTTPStatus.OK

    def status_daemon(self, start_time):
        poll(target=self.daemon.is_alive, step=1, poll_forever=True, check_success=is_value(False))
        end_time = time()
        print(f'Background task stopped in {end_time-start_time}s.')


smart_charger_controller = SmartChargerController()
