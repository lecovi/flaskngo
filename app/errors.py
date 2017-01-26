# Standard Lib imports
# Third-party imports
from flask import jsonify
# BITSON imports


CUSTOM_ERRORS = [400, 401, 404, 405, 415, 500]


class CustomErrors(object):
    pass


def add_method(cls, app, error_code):
    @app.errorhandler(error_code)
    def inner_method(error):
        response = jsonify({
                            'error': error.description,
                            'code': error.code
                            })
        response.status_code = error.code
        return response
    setattr(cls, inner_method.__name__, inner_method)


def error_response_template(code, data, message, error):
    response = dict(data=data, error=error, message=message)
    response = jsonify(response)
    response.status_code = code
    return response


def bad_request(message, code=400, data=None):
    return error_response_template(message=message, code=code, data=data,
                                   error='bad request')


def unauthorized(message, code=401, data=None):
    return error_response_template(message=message, code=code, data=data,
                                   error='unauthorized')


def forbidden(message, code=403, data=None):
    return error_response_template(message=message, code=code, data=data,
                                   error='forbidden')


def not_found(message, code=404, data=None):
    return error_response_template(message=message, code=code, data=data,
                                   error='not found')
