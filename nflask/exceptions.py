class APIError(Exception):
    code = 500
    status = "APIError"

    def __init__(
        self,
        code=None,
        status=None,
        message=None,
        extras=None
    ):
        if code is not None:
            self.code = code

        if status is not None:
            self.status = status

        if message is not None:
            self.message = message

        self.extras = extras

    def to_dict(self):
        return {
            "code": self.code,
            "status": self.status,
            "message": self.message,
            "extras": self.extras
        }


class DataNotFound(APIError):
    code = 404
    status = "DataNotFound"
    message = "Data tidak ditemukan"


class DataExists(APIError):
    code = 400
    status = "DataExists"
    message = "Data sudah terdaftar di dalam database"


class ValidationError(APIError):
    code = 400
    status = "ValidationError"
    message = "Kesalahan pada validasi data"


class InvalidCredentials(APIError):
    code = 400
    status = "InvalidCredentials"
    message = "Email / Password anda salah."


class UserNotActive(APIError):
    code = 401
    status = "UserNotActive"
    message = "Akun anda tidak aktif, silakan hubungi administrator."


class Unauthorized(APIError):
    code = 401
    status = "Unauthorized"
    message = "Anda harus login untuk mengakses sistem."


class InvalidTokenType(APIError):
    code = 401
    status = "InvalidTokenType"
    message = "Jenis token salah."


class TokenNotFound(APIError):
    code = 401
    status = "TokenNotFound"
    message = "Sesi anda tidak terdaftar / tidak aktif."
    
class ExpiredSession(APIError):
    code = 401
    status = "ExpiredSession"
    message = "Sesi anda telah habis."

class DontHavePermission(APIError):
    code = 401
    status = "DontHavePermission"
    message = "Anda tidak memiliki hak akses untuk fungsi ini."
