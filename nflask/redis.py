import redis


def init_redis(app):
    # Setup elastic search connection
    app.logger.info("Initializing Redis connection...")

    # Get redis configuration
    config = app.config["REDIS"]

    # Redis configuration
    if 'redis' not in app.__dict__.keys():
        r = redis.Redis(
            host=config['HOST'],
            port=config['PORT'])

        # print(r)

        setattr(app, "redis", r)
