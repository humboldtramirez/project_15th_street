import datetime
from typing import Dict, Union

from sqlalchemy import Column, Integer, DateTime, JSON
from project.models.init_db import db


class VehicleModel(db.Model):
    """Vehicle model"""
    __tablename__ = 'vehicle_model'

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    @classmethod
    def select_last(cls):
        result = cls.query.all()
        return result[-1]

    def get_vehicle_data(self) -> str:
        result = self.select_last()
        vehicle_data = result.data
        print(f'vehicle_data as of {result.timestamp}:\n{vehicle_data}')
        return vehicle_data

    def get_charge_state(self) -> Dict[str, Union[str, int]]:
        charge_state = self.get_vehicle_data().get('charge_state')
        print(f'charge_state: {charge_state}')
        return charge_state

    def get_charger_actual_current(self) -> int:
        charger_actual_current = self.get_charge_state().get('charger_actual_current', 0)
        print(f'charger_actual_current: {charger_actual_current}')
        return charger_actual_current
