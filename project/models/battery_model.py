import datetime
from typing import Dict, Union

from sqlalchemy import Column, Integer, DateTime, JSON
from project.models.init_db import db


class BatteryModel(db.Model):
    """Battery model"""
    __tablename__ = 'battery_model'

    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    @classmethod
    def select_last(cls):
        result = cls.query.all()
        return result[-1]

    def get_battery_data(self) -> str:
        result = self.select_last()
        battery_data = result.data
        return battery_data

    def get_power_reading(self) -> Dict[str, Union[str, int]]:
        """
        power_reading
        timestamp:
        load_power (W):  home consumption
        solar_power (W):  solar generation
        grid_power (W): grid consumption / export (negative)
        battery_power (W):  battery charge (negative) / discharge.  Observed -10 when 100%
        generator_power (W):  generator generation
        """
        power_reading = self.get_battery_data().get('power_reading', [()])[0]  # Assumes only 1 power reading in list
        return power_reading

    def get_battery_power_watts(self) -> int:
        # TODO:  max W discharged by battery = 4900?
        energy_left = self.get_battery_data().get('energy_left', 0)
        return energy_left

    def get_grid_power_watt(self) -> int:
        grid_power_watts = self.get_power_reading().get('grid_power', 0)
        return grid_power_watts

    def get_reserved_pack_energy(self) -> int:
        total_pack_energy = int(self.get_battery_data().get('total_pack_energy', 0))
        print(f'total_pack_energy: {total_pack_energy}')
        reserved_pack_energy_watt = total_pack_energy * self.get_backup_reserve_percent() / 100
        return reserved_pack_energy_watt

    def get_backup_reserve_percent(self) -> int:
        backup = self.get_battery_data().get('backup')
        backup_reserve_percent = backup.get('backup_reserve_percent', 0) if backup else 0
        print(f'backup_reserve_percent: {backup_reserve_percent}')
        return backup_reserve_percent
