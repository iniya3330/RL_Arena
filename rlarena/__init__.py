import os
if os.environ.get("DB_ENGINE", "").lower() == "mysql":
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
