import datetime
from sqlalchemy import Column, Integer, DateTime, String, JSON
from project.models.init_db import db


class SmartChargerModel(db.Model):
    """smart charger model"""
    __tablename__ = 'smart_charger_model'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amps = Column(Integer, nullable=False)
    ai_model = Column(String(50), nullable=False)
    features = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    @classmethod
    def select_last(cls):
        result = cls.query.all()
        return result[-1]

    @classmethod
    def set_amps(cls, amps, ai_model, features):
        new_data = SmartChargerModel(amps=amps, ai_model=ai_model, features=features)
        db.session.add(new_data)
        db.session.commit()

    def get_amps(self) -> int:
        result = self.select_last()
        amps = result.amps
        return amps
