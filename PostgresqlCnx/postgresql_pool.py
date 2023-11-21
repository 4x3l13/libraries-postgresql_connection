# -*- coding: utf-8 -*-
"""
Created on Mon Dic 26 10:00:00 2022

@author: Jhonatan Martínez
"""
import threading

from loguru import logger
from typing import Dict, List
import psycopg2
from psycopg2 import pool
from .constants import *


class PoolDB:
    """ Permite realizar una conexión a una Base de Datos"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(PoolDB, cls).__new__(cls)
            cls._instance.__attributes = ['host', 'port', 'sdi', 'user', 'password', 'driver']
            cls._instance._initialized = False
            return cls._instance

    def __init__(self, setup: Dict[str, str], pool_size: int = 5) -> None:
        """Constructor.

        Args:
        setup (Dict[str, str]):
            El diccionario necesita de las siguientes keys:
                - host: Server host.
                - port: Server port.
                - sdi: Database SDI.
                - user: Database user.
                - password: Database password.
                - driver: Database driver.

        Returns:
            None.
        """
        if self._initialized:
            return
        self._initialized = True
        self.__attributes = ['host', 'port', 'sdi', 'user', 'password', 'driver']
        self.__setup: Dict = setup
        self.__pool_size = pool_size
        self.__pool: pool.SimpleConnectionPool = None
        self.__main()

    def __main(self) -> None:
        logger.debug(self.__setup)
        """Válida que el diccionario contenga los atributos necesarios para que la clase funcione."""
        missing = [key for key in self.__attributes if str(key).lower() not in self.__setup.keys()]
        if len(missing) > 0:
            logger.error(MISSING_ATTRIBUTES)
            logger.error(missing)
        try:
            self.__pool = pool.SimpleConnectionPool(
                minconn=self.__pool_size,
                maxconn=self.__pool_size,
                host=self.__setup["host"],
                database=self.__setup["sdi"],
                user=self.__setup["user"],
                password=self.__setup["password"],
                port=self.__setup["port"]
            )
        except Exception as exc:
            logger.error(f"Error initializing connection pool: {exc}", exc_info=True)

    def read_data(self, query: str, parameters: tuple = (), datatype: str = "dict") -> [Dict, List]:
        """Obtener los datos de una consulta.

        Args:
            query (str): Consulta a ejecutar.
            parameters (tuple, optional): Parámetros de la consulta.
            datatype (str, optional): Tipo de datos a retornar.

        Returns:
            show_data[Dict,List]: Datos obtenidos.
        """
        show_data = None
        datatype = datatype.lower()
        if datatype in ['dict', 'list']:
            try:
                with self.__pool.getconn() as cnx:
                    with cnx.cursor() as cursor:
                        # Ejecutar la consulta
                        cursor.execute(query, parameters)
                        query = cursor.mogrify(query, parameters)
                        data = cursor.fetchall()
                        # Gets column_names
                        columns = [column[0].upper() for column in cursor.description]
                        # Validate the datatype to return
                        if datatype == 'dict':
                            dictionary = []
                            for item in data:
                                dictionary.append(dict(zip(columns, item)))
                            show_data = dictionary
                        elif datatype == 'list':
                            show_data = [columns, data]
                    logger.info(DATA_OBTAINED, query.decode('utf-8'))
                    return show_data
            except (psycopg2.DatabaseError, psycopg2.Error, Exception) as exc:
                logger.error(str(exc), exc_info=True)
        else:
            logger.warning(INVALID_DATATYPE)

        return show_data

    def execute_query(self, query: str, parameters: tuple = ()) -> bool:
        """
        Ejecutar una consulta.

        Args:
            query (str): Consulta a ejecutar.
            parameters (tuple, optional): Parámetros de la consulta.

        Returns:
            bool: True si se ejecuta correctamente, False en caso contrario.
        """
        try:
            with self.__pool.getconn() as cnx:
                with cnx.cursor() as cursor:
                    cursor.execute(query, parameters)
                cnx.commit()
                logger.info(EXECUTED_QUERY, query)
                return True
        except (psycopg2.DatabaseError, psycopg2.Error, Exception) as exc:
            logger.error(str(exc), exc_info=True)
            cnx.rollback()

        return False

    def execute_many(self, query: str, values: List) -> bool:
        """Ejecutar una consulta con varios valores.

        Args:
            query (str): Consulta a ejecutar.
            values (List): Valores de la consulta.

        Returns:
            bool: True si se ejecuta correctamente, False en caso contrario.
        """
        try:
            with self.__pool.getconn() as cnx:
                with cnx.cursor() as cursor:
                    cursor.prepare(query)
                    cursor.executemany(None, values)
                cnx.commit()
                logger.info(EXECUTED_QUERY, query)
                return True
        except (psycopg2.DatabaseError, psycopg2.Error, Exception) as exc:
            logger.error(str(exc), exc_info=True)
            cnx.rollback()

        return False
