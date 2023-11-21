# -*- coding: utf-8 -*-
"""
Created on Mon Dic 26 10:00:00 2022

@author: Jhonatan Martínez
"""

from loguru import logger
from typing import Dict, List
import psycopg2
from .constants import *


class ConnectionDB:
    """ Permite realizar una conexión a una Base de Datos"""

    def __init__(self, setup: Dict[str, str]) -> None:
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

        self.__attributes = ['host', 'port', 'sdi', 'user', 'password', 'driver']
        self.__connection = None
        self.__setup: Dict = setup
        self.__main()

    def __main(self) -> None:
        logger.debug(self.__setup)
        """Válida que el diccionario contenga los atributos necesarios para que la clase funcione."""
        missing = [key for key in self.__attributes if str(key).lower() not in self.__setup.keys()]
        if len(missing) > 0:
            logger.error(MISSING_ATTRIBUTES)
            logger.error(missing)

    def __close_connection(self) -> None:
        """Cerrar la conexión a la base de datos."""
        try:
            if self.__connection is not None:
                self.__connection.close()
                logger.debug(CLOSE_CONNECTION)
        except (ConnectionError, Exception) as exc:
            logger.error(str(exc), exc_info=True)

    def __get_connection(self) -> bool:
        """Crear y obtener la conexión a una base de datos

        Returns:
            bool: True si se establece la conexión, False en caso contrario.
        """

        self.__connection = None
        try:
            self.__connection = psycopg2.connect(host=self.__setup["host"],
                                                 database=self.__setup["sdi"],
                                                 user=self.__setup["user"],
                                                 password=self.__setup["password"],
                                                 port=self.__setup["port"])
            logger.debug(f"{ESTABLISHED_CONNECTION} {self.__setup['host']}")
            return True
        except (ConnectionError, Exception) as exc:
            self.__connection = None
            logger.error(str(exc), exc_info=True)
            return False

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
        if self.__get_connection():
            datatype = datatype.lower()
            if datatype in ['dict', 'list']:
                try:
                    with self.__connection as cnx:
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
                        logger.info(f"{DATA_OBTAINED} {query.decode('utf-8')}")
                        return show_data
                except (psycopg2.DatabaseError, psycopg2.Error, Exception) as exc:
                    logger.error(str(exc), exc_info=True)
                finally:
                    self.__close_connection()
            else:
                logger.warning(INVALID_DATATYPE)
        else:
            logger.warning(NO_CONNECTION)

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
        if self.__get_connection():
            try:
                with self.__connection as cnx:
                    with cnx.cursor() as cursor:
                        cursor.execute(query, parameters)
                    cnx.commit()
                    logger.info(f"{EXECUTED_QUERY} {query}")
                    return True
            except (psycopg2.DatabaseError, psycopg2.Error, Exception) as exc:
                logger.error(str(exc), exc_info=True)
                cnx.rollback()

                return False
            finally:
                self.__close_connection()
        else:
            logger.warning(NO_CONNECTION)
            return False

    def execute_many(self, query: str, values: List) -> bool:
        """Ejecutar una consulta con varios valores.

        Args:
            query (str): Consulta a ejecutar.
            values (List): Valores de la consulta.

        Returns:
            bool: True si se ejecuta correctamente, False en caso contrario.
        """
        if self.__get_connection():
            try:
                with self.__get_connection() as cnx:
                    with cnx.cursor() as cursor:
                        cursor.prepare(query)
                        cursor.executemany(None, values)
                    cnx.commit()
                    logger.info(f"{EXECUTED_QUERY} {query}")
                    return True
            except (psycopg2.DatabaseError, psycopg2.Error, Exception) as exc:
                logger.error(str(exc), exc_info=True)
                cnx.rollback()
                return False
            finally:
                self.__close_connection()
        else:
            logger.warning(NO_CONNECTION)
            return False
