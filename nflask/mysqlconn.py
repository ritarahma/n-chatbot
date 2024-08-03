import os
# from flask_mysqldb import MySQL
import mysql.connector


def init_db(app):
    # Setup mysql connection used by object mapper
    app.logger.info("Initializing MySQL DB Connection...")

    config = app.config['MYSQL']
    database = mysql.connector.connect(
            host=config['HOSTS'],
            user=config['USER'],
            passwd=config['PASSWD'],
            database=config['DATABASE']
        )

    setattr(app, "mysql", database)
