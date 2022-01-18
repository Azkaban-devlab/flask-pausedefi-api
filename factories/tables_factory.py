import sys
sys.path.append('/var/www/pausedefi')


from pausedefi_api import db


db.create_all()