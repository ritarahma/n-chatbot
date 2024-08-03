import os
import imp


def import_modules(app, path, name=None):
    try:
        name = name or os.path.split(path)[-1].replace(".", "_")
        fp, pathname, description = imp.find_module(path)
        return imp.load_module(name, fp, pathname, description)
    except ImportError as e:
        app.logger.debug(e)
        app.logger.debug("Module not found: {}".format(path))
        return None
    # flake8: noqa
    except Exception as e:
        app.logger.debug("Module Load Error")
        app.logger.debug(e)
        return None
