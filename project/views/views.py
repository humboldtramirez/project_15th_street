import connexion
from flask import jsonify
from http import HTTPStatus

from project.controllers.battery import battery_controller
from project.controllers.smart_charger_controller import smart_charger_controller
from project.controllers.vehicle import vehicle_controller


def get():
    return jsonify({}), 200


def get_available_amps():
    return jsonify(battery_controller.get_available_amps()), 200


def get_charging_amps():
    return jsonify(smart_charger_controller.get_charging_amps()), 200


def set_charging_amps():
    available_amps = battery_controller.get_available_amps()
    charger_actual_current = vehicle_controller.get_charger_actual_current()
    amps = smart_charger_controller.calculate_charging_amps(available_amps, charger_actual_current)
    smart_charger_controller.set_charging_amps(amps, 'development', smart_charger_controller.features)
    return jsonify({'charging_amps': amps}), 200


def start_poll():
    status = smart_charger_controller.start_polling()
    return jsonify({status.description: status.phrase}), status.value


def status_poll():
    result = smart_charger_controller.status_polling()
    status = HTTPStatus.OK if result else HTTPStatus.NO_CONTENT
    return jsonify(result), status


def stop_poll():
    status = smart_charger_controller.stop_polling()
    return jsonify({status.description: status.phrase}), status.value


def search():
    return get()


def post():
    if connexion.request.is_json:
        data = connexion.request.get_json()
        return jsonify(data)
    return jsonify({})
