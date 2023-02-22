import json
import os
import unittest
from unittest.mock import patch

from project.app import MyMicroservice
from pyms.constants import CONFIGMAP_FILE_ENVIRONMENT


class ProjectTestCase(unittest.TestCase):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        os.environ[CONFIGMAP_FILE_ENVIRONMENT] = os.path.join(self.BASE_DIR, "config-tests.yml")
        ms = MyMicroservice(path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "project", "test_views.py"))
        self.app = ms.create_app()
        self.base_url = self.app.config["APPLICATION_ROOT"]
        self.client = self.app.test_client()

    def tearDown(self):
        pass  # os.unlink(self.app.config['DATABASE'])

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(404, response.status_code)

    def test_healthcheck(self):
        response = self.client.get('/healthcheck')
        self.assertEqual(200, response.status_code)

    def test_list_view(self):
        response = self.client.get('/project_15th_street/')
        self.assertEqual(200, response.status_code)

    def test_create_view(self):
        name = "blue"
        response = self.client.post('/project_15th_street/',
                                    data=json.dumps(dict(name=name)),
                                    content_type='application/json'
                                    )
        self.assertEqual(200, response.status_code)

    @patch('project.views.views.battery_controller.get_status')
    def test_get_battery_status(self, mock_get_status):
        mock_get_status.return_value = {'status': 'Standby', 'time_remaining': None}
        response = self.client.get('/project_15th_street/battery-status')
        self.assertEqual(200, response.status_code)

    @patch('project.views.views.smart_charger_controller.set_charging_amps')
    @patch('project.views.views.vehicle_controller.calculate_charging_amps')
    @patch('project.views.views.battery_controller.get_available_amps')
    def test_set_charging_amps(self, mock_available_amps, mock_calc_amps, mock_set_amps):
        mock_available_amps.return_value = 0
        mock_calc_amps.return_value = 5
        mock_set_amps.return_value = None
        response = self.client.get('/project_15th_street/set-charging-amps')
        self.assertEqual(200, response.status_code)

    @patch('project.views.views.vehicle_controller.manage_vehicle')
    def test_manage_vehicle(self, mock_manage_vehicle):
        mock_manage_vehicle.return_value = None
        response = self.client.get('/project_15th_street/manage-vehicle')
        self.assertEqual(200, response.status_code)

    def test_start_poll(self):
        response = self.client.get('/project_15th_street/start-poll')
        self.assertEqual(200, response.status_code)

    def test_status_poll(self):
        response = self.client.get('/project_15th_street/status-poll')
        self.assertEqual(200, response.status_code)

    def test_stop_poll(self):
        response = self.client.get('/project_15th_street/stop-poll')
        self.assertEqual(200, response.status_code)
