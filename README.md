Librería Conectar a bases de datos


Por Jhonatan Martínez - jhonatanmartinez130220@gmail.com


Librería que  permite crear conexiones normal, con pool y asincronas para base de datos PostgreSQL:

Para utilizarla solo necesitas pasar un diccionario con los siguientes datos:
                - host: Server host.
                - port: Server port.
                - sdi: Database SDI.
                - user: Database user.
                - password: Database password.
                - driver: Database driver.

💡 Prerequisitos:
Python 3.8.9,
psycopg2==2.9.7,
loguru==0.7.2,
asyncpg==0.29.0

📚 Ejemplo de uso para conexión normal:

    from PostgresqlCnx import CnxPostgresql
    
    cnx = ConnectionDB(setup=my_dictionary)
    
    data = cnx.read_data(query='select * from table')

Ejemplo de uso para conexión pool:

    from PostgresqlCnx import PoolPostgresql
    
    cnx = PoolDB(setup=my_dictionary, pool_size=10)
    
    data = cnx.read_data(query='select * from table')

Ejemplo de uso para conexión asincrona:

    from PostgresqlCnx import AsyncPostgresql
    
    cnx = AsyncDB(setup=my_dictionary)
    
    data = awaiit cnx.read_data(query='select * from table')