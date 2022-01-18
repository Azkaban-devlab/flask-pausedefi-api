# Initialisation de l'env
<pre>
pipenv shell
pipenv install
</pre>

# Initialisation BDD
### Ruben reminder
<pre>
pipenv install PyMySQL

import pymysql
pymysql.install_as_MySQLdb()
</pre>

Update `__init__.py` file if you need to set a password for your db

<pre>
python -m factories.db_factory.py
python -m factories.tables_factory.py
python -m factories.data_factory.py
</pre>

# Run app
<pre>
python run.py
</pre>
