from flask_restful import Api as FlaskApi
from werkzeug.datastructures import Headers
from nflask.errors import errors, werkzeug_errors
from nflask import exceptions


class Api(FlaskApi):
    def handle_error(self, e):
        # Get error class name
        error_name = type(e).__name__
        # Get defined error list
        error_list = list(
            error for error in exceptions.__dict__.keys()
            if not error.startswith("__"))

        # Define default response
        response = {
            "code": 500,
            "status": "SERVER_ERROR",
            "message": "Internal Server Error",
            "extras": None
        }

        # If error is in error list
        # map error attribute into response
        if error_name in error_list:
            response = e.to_dict()
        # If error is derived from werkzeug
        # map error attribute into response
        elif error_name in werkzeug_errors.keys():
            response['code'] = werkzeug_errors[error_name]['code']
            response['status'] = error_name
            response['message'] = werkzeug_errors[error_name]['message']

            if 'data' in e.__dict__.keys():
                if 'message' in e.data:
                    response['extras'] = e.data['message']
        # Flask-restful error handling style
        elif error_name in errors.keys():
            response['code'] = self.errors[error_name]['code']
            response['status'] = self.errors[error_name]['status']
            response['message'] = self.errors[error_name]['message']

            if 'extras' in self.errors[error_name]:
                response['extras'] = self.errors[error_name]['extras']
        # Default error handler to ensure
        # app is safe to throw exception
        else:
            return super(FlaskApi, self).handle_error(e)

        # Return error response
        return self.make_response(
            response,
            response['code'],
            Headers()
        )
