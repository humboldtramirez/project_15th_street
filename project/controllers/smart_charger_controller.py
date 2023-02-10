import requests
from http import HTTPStatus
from polling2 import is_value, poll, poll_decorator
from time import time
from threading import Thread

from project.models.smart_charger_model import SmartChargerModel

# Rating for Charging Outlet.  W = VA
CHARGING_MAX_AMP = 32


class SmartChargerController:
    polling_disabled = None
    daemon = None

    def __init__(self):
        self.smart_charger_model = SmartChargerModel()
        self.features = {}

    def get_charging_amps(self) -> int:
        result = self.smart_charger_model.select_last()
        amps = result.amps
        return amps

    def set_charging_amps(self, amps, ai_model: str = 'scratch', features: dict = {}):
        self.smart_charger_model.insert_data(amps, ai_model, features)

    def calculate_charging_amps(self, available_amps: int, charger_actual_current: int) -> int:
        # TODO:
        # Dryer Requirements:  240V, 30A or 7200W
        # Washer Requirements: 120V, 10A or 1200W
        # Laundry Req:  8.4kW
        # AC Req: ?
        # Powerwall Capacity:  13.5 kWh

        charging_amps = min(charger_actual_current + available_amps,
                            CHARGING_MAX_AMP)
        self.features['charging_amps'] = charging_amps
        self.features['available_amps'] = available_amps
        self.features['charger_actual_current'] = charger_actual_current
        return charging_amps

    @poll_decorator(step=60, poll_forever=True)
    def poll_tesla_service(self):
        """
        Source: https://polling2.readthedocs.io/en/latest/examples.html#wrap-a-target-function-in-a-polling-decorator
        :return:
        """
        requests.get('http://127.0.0.1:5001/project_15th_street/set-charging-amps')
        return self.polling_disabled

    def start_polling(self):
        """
        Source:
        https://superfastpython.com/thread-long-running-background-task/
        https://realpython.com/intro-to-python-threading/

        :return:
        """
        self.polling_disabled = False
        print('Starting background task ...')
        self.daemon = Thread(target=self.poll_tesla_service, daemon=True, name='PollingSmartCharger')
        self.daemon.start()
        return HTTPStatus.OK

    def status_polling(self) -> dict:
        if self.daemon is None:
            return {}
        print(f'is_alive: {self.daemon.is_alive()}')
        print(f'ident: {self.daemon.ident}')
        print(f'name: {self.daemon.getName()}')
        return {'ident': self.daemon.ident, 'is_alive': self.daemon.is_alive(), 'name': self.daemon.getName()}

    def stop_polling(self) -> int:
        print('Stopping background task ...')
        self.polling_disabled = True
        start_time = time()
        local_daemon = Thread(target=self.status_daemon, args=(start_time,), daemon=True, name='PollingDaemonStatus')
        local_daemon.start()
        return HTTPStatus.OK

    def status_daemon(self, start_time):
        poll(target=self.daemon.is_alive, step=1, poll_forever=True, check_success=is_value(False))
        end_time = time()
        print(f'Background task stopped in {end_time-start_time}s.')
        return


smart_charger_controller = SmartChargerController()
