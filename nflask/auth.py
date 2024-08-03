import json
import random
import string
from flask import current_app as app, request
from datetime import datetime, timedelta
from itsdangerous import JSONWebSignatureSerializer
from functools import wraps
from nflask.exceptions import Unauthorized, TokenNotFound, InvalidTokenType, DontHavePermission, ExpiredSession

def generate_token(user):
    s = JSONWebSignatureSerializer(app.config['SECRET_KEY'])
    _user = {
        # "id": str(user.profile_id),
        # "email": str(user.username),
        "phoneNo": str(user.get('From')),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    token = s.dumps(_user)

    return token.decode('ASCII')

def generate_session(user, token):
    _created = datetime.now()
    _expired = _created + timedelta(hours=1)

    # permission = get_permissions(str(user.id))
    # user_level = get_user_level(str(user.id))

    # if user.no_limit:
    #     expired_session = 0
    # else:
    expired_session = _expired.strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate session data with active user
    # information so frontend should not
    # request multiple times
    return {
        "token": token,
        "created": _created.strftime("%Y-%m-%d %H:%M:%S"),
        "expired": expired_session,
        "user": {
            # "id": str(user.id),
            # "email": user.email,
            "phone_number": str(user.get('From')),
            "nama_lengkap": str(user.get('ProfileName')),
        }
    }


def save_session(session):
    # Get session prefix from config
    session_prefix = app.config['SESSION_PREFIX']

    # Clear all previous session
    phoneNo = session["user"]["phone_number"]
    clear_session(phoneNo=phoneNo)

    # Save session information
    app.redis.set(
        "{}:{}:{}".format(
            session_prefix,
            session["token"],
            session["user"]["phone_number"]
        ),
        json.dumps(session),
        ex=14400
    )

def get_session_list(phoneNo=None, token=None):
    if phoneNo is not None:
        pattern = "*{}".format(phoneNo)
    elif token is not None:
        pattern = "*{}*".format(token)
    else:
        return []

    # print(pattern, app.redis)

    return app.redis.keys(pattern)

def get_session(phoneNo=None, token=None):
    if phoneNo is not None:
        pattern = "*{}".format(phoneNo)
    elif token is not None:
        pattern = "*{}*".format(token)
    else:
        return None

    keys = app.redis.keys(pattern)
    print('keys', keys)
    key = keys[0].decode('ASCII')
    print('key', key)
    session = app.redis.get(key).decode('ASCII')
    print('session', session)

    if session is not None:
        return json.loads(session)

    return None

def clear_session(phoneNo=None, token=None):
    if phoneNo is not None:
        prev_session = get_session_list(phoneNo=phoneNo)
    elif token is not None:
        prev_session = get_session_list(token=token)

    if len(prev_session) > 0:
        prev_session = list(key.decode('ASCII') for key in prev_session)
        app.redis.delete(*prev_session)


def authenticate(f):
    # Check if user is logged in or return 401
    @wraps(f)
    def func_wrapper(*args, **kwargs):
        # Get real args so it doesnt mix with reqparser
        _realargs = args
        _realkwargs = kwargs
        # Get request headers
        authorization = request.headers.get("Authorization")
        # Throw error if authorization header is not found
        if authorization is None:
            raise Unauthorized()
        # Get token from header
        headers = authorization.split()
        bearer = headers[0]
        token = headers[1]
        # Detect invalid scheme
        if bearer != "Bearer":
            raise InvalidTokenType()
        # Detect invalid token
        session_list = get_session_list(token=token)
        if len(session_list) < 1:
            raise TokenNotFound()
        # Get current session
        session = get_session(token=token)
        if session is None:
            raise TokenNotFound()
        if session['expired'] != 0:
            expired = datetime.strptime(session['expired'], "%Y-%m-%d %H:%M:%S")
            if datetime.now() >= expired:
                raise ExpiredSession()
        _realkwargs.update(session=session)
        try:
            return f(*_realargs, **_realkwargs)
        except TypeError:
            return f(*_realargs)
        except Exception as e:
            print(e)

    return func_wrapper

def auth_permission(fn):
    @wraps(fn)
    def func_wrapper(*args, **kwargs):
        # Get real args so it doesnt mix with reqparser
        _realargs = args
        _realkwargs = kwargs

        authorization = request.headers.get("Authorization")
        headers = authorization.split()
        token = headers[1]

        path = func_wrapper.__module__
        this_module = path.split(".")[0]

        perm = get_session(token=token)

        if perm is not None:
            list_permission = perm['permissions']
            for i in list_permission:
                if i['kode'] == this_module:
                    list_action = i['permissions']
        else:
            print('permission not assigned!')

        # assign permission to methods
        this_action = ""
        this_func = str(func_wrapper.__name__)

        options = {
            'get': 'reads',
            'post': 'creates',
            'put': 'updates',
            'delete': 'deletes'
        }

        this_action = options.get(this_func, 'method not be detected')

        if list_action[this_action] is False:
            raise DontHavePermission()
        try:
            return fn(*_realargs, **_realkwargs)
        except:
            return fn(*_realargs)

        # return fn(*_realargs, **_realkwargs)
    return func_wrapper

def generate_otp(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def generate_key(size=32, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))