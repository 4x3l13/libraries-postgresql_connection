Librería Conectar a bases de datos


Por Jhonatan Martínez - jhonatanmartinez130220@gmail.com


Librería te permite crear conexiones para base de datos PostgreSQL:

Para utilizarla solo necesitas pasar un diccionario con los datos solicitados, estos se pueden ver al invocar la clase ConnectionDB.

💡 Prerequisitos:
Python 3.8.9,

psycopg2==2.9.7,

📚 Ejemplo de uso:

    from PostgresqlCnx import ConnectionDB
    
    cnx = ConnectionDB(setup=my_dictionary)
    
    data = cnx.read_data(query='select * from table')
