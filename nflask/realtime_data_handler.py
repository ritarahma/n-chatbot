from flask import current_app as app, request
import json
from flask import jsonify

def save_to_redis(prefix, keyword, start, end, limit, data):
    # Save session information
    app.redis.set(
        "{}:{}:{}:{}".format(
            prefix,
            keyword,
            start + '-' + end,
            limit
        ),
        json.dumps(data),
        ex=14400
    )

def get_data_list(prefix=None, keyword=None, start=None, end=None):
    if prefix is not None and keyword is not None:
        pattern = "{}:{}*".format(prefix, keyword)
    elif keyword is not None:
        pattern = "*{}*".format(keyword)
    elif start is not None and end is not None:
        pattern = "*{}*".format(start + '-' + end)
    else:
        return []

    results = []
    list_key = app.redis.keys(pattern)
    if list_key is not None:
        for key in list_key:
            results.append(key.decode('ASCII'))
    return results

def get_data_from_redis(prefix=None, keyword=None, start=None, end=None, limit=None):
    if prefix is not None and keyword is not None and start is not None and end is not None and limit is not None:
        pattern = "{}:{}:{}:{}".format(
            prefix,
            keyword,
            start + '-' + end,
            limit
        )
    else:
        return None

    data = None
    keys = app.redis.keys(pattern)
    if len(keys) != 0:
        key = keys[0].decode('ASCII')
        data = app.redis.get(key).decode('ASCII')

    if data is not None:
        return json.loads(data)

    return None

def clear_data(prefix=None, keyword=None):
    if prefix is not None and keyword is not None:
        prev_session = get_data_list(prefix=prefix, keyword=keyword)

    if len(prev_session) > 0:
        prev_session = list(key for key in prev_session)
        app.redis.delete(*prev_session)