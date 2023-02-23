import connexion
from flask import current_app, jsonify, request
from http import HTTPStatus

from project.controllers.battery import battery_controller
from project.controllers.smart_charger_controller import smart_charger_controller
from project.controllers.vehicle import vehicle_controller


def get():
    return jsonify({}), HTTPStatus.OK


def get_battery_status():
    status = battery_controller.get_status()
    current_app.logger.info(f'battery_controller features: {battery_controller.features}')
    return jsonify(status), HTTPStatus.OK


def set_charging_amps():
    current_app.logger.info(f'Starting set_charging_amps: {request.headers}')

    current_app.logger.debug('get_available_amps')
    available_amps = battery_controller.get_available_amps()

    current_app.logger.debug('calculate_charging_amps')
    amps = vehicle_controller.calculate_charging_amps(available_amps)

    current_app.logger.debug('set_charging_amps')
    features = {
        'battery_controller': battery_controller.features,
        'vehicle_controller': vehicle_controller.features,
        'smart_charger_controller': smart_charger_controller.features,
    }
    current_app.logger.info(f'features: {features}')
    smart_charger_controller.set_charging_amps(amps, 'development', features)

    current_app.logger.info('Ending set_charging_amps successfully.')
    return jsonify({'charging_amps': amps}), HTTPStatus.OK


def manage_vehicle():
    vehicle_controller.manage_vehicle()
    return jsonify({}), HTTPStatus.OK


def start_poll():
    smart_charger_controller.start_polling()
    return jsonify({'start_poll': 'Success'}), HTTPStatus.OK


def status_poll():
    result = smart_charger_controller.status_polling()
    status = HTTPStatus.OK if result else HTTPStatus.NO_CONTENT
    return jsonify(result), status


def stop_poll():
    msg = 'Stop polling smart_charger_controller'
    current_app.logger.info(msg)
    stop_duration_seconds = smart_charger_controller.stop_polling()
    msg = f'Polling stopped in {stop_duration_seconds}s'
    current_app.logger.info(msg)
    return jsonify({'stop_poll': 'Success', 'stop_duration_seconds': stop_duration_seconds}), HTTPStatus.OK


def search():
    return get()


def post():
    if connexion.request.is_json:
        data = connexion.request.get_json()
        return jsonify(data)
    return jsonify({})
