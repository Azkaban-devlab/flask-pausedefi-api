import sys
sys.path.insert(0, '/var/www/pausedefi')

activate_this = '/home/toto/.local/share/virtualenvs/pausedefi-7-KaKzYS/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from pausedefi_api import app as application