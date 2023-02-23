import datetime
from typing import Dict, Union

from sqlalchemy import Column, Integer, DateTime, JSON
from project.models.init_db import db

# Rating for Charging Outlet.  W = VA
CHARGING_MAX_AMP = 32


class VehicleModel(db.Model):
    """Vehicle model"""
    __tablename__ = 'vehicle_model'

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    @classmethod
    def get_vehicle_data(cls) -> str:
        result = cls.query.order_by(cls.timestamp.desc()).first()
        vehicle_data = result.data
        return vehicle_data

    def get_charge_state(self) -> Dict[str, Union[str, int]]:
        charge_state = self.get_vehicle_data().get('charge_state', {})
        return charge_state

    def get_charger_actual_current(self) -> int:
        charger_actual_current = self.get_charge_state().get('charger_actual_current', 0)
        return charger_actual_current

    def get_charge_current_request_max(self) -> int:
        charge_current_request_max = self.get_charge_state().get('charge_current_request_max', CHARGING_MAX_AMP)
        return charge_current_request_max

    def get_minutes_to_full_charge(self) -> int:
        minutes_to_full_charge = self.get_charge_state().get('minutes_to_full_charge', 0)
        return minutes_to_full_charge

    def get_charging_state(self) -> str:
        """
        'Charging', 'Disconnected', 'Stopped'
        """
        return self.get_charge_state().get('charging_state', '')

    def get_charge_port_latch(self) -> str:
        return self.get_charge_state().get('charge_port_latch', '')

    def get_battery_range(self) -> int:
        return int(self.get_charge_state().get('battery_range', 0))

    def is_charging_state_charging(self) -> bool:
        charging_state = self.get_charging_state()
        return bool(charging_state == 'Charging')

    def is_charging_state_disconnected(self) -> bool:
        charging_state = self.get_charging_state()
        return bool(charging_state == 'Disconnected')

    def is_charging_state_stopped(self) -> bool:
        charging_state = self.get_charging_state()
        return bool(charging_state == 'Stopped')

    def is_charge_port_latch_engaged(self) -> bool:
        charge_port_latch = self.get_charge_port_latch()
        return bool(charge_port_latch == 'Engaged')
