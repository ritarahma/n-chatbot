errors = {
    "LWTException": {
        "code": 400,
        "status": "DatabaseException",
        "message": "Database exception"
    },
    "DoesNotExist": {
        "code": 404,
        "status": "DataNotFound",
        "message": "Data tidak dapat ditemukan",
    },
    "NotFoundError": {
        "code": 404,
        "status": "DataNotFound",
        "message": "Data tidak dapat ditemukan"
    }
}

# Define explicitly about error derived from werkzeug
werkzeug_errors = {
    "BadRequest": {
        "code": 400,
        "message": "Bad Request"
    },
    "MethodNotAllowed": {
        "code": 405,
        "message": "HTTP Method not Allowed"
    }
}
