import sys
sys.path.append('/var/www/pausedefi')

print(sys.path)

from pausedefi_api import app
import mysql.connector


connection = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD']
)


cursor = connection.cursor()
cursor.execute(f"DROP DATABASE IF EXISTS {app.config['MYSQL_DB']}")
cursor.execute(f"CREATE DATABASE {app.config['MYSQL_DB']}")


connection.close()