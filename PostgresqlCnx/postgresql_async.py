# -*- coding: utf-8 -*-
"""
Created on Mon Dic 26 10:00:00 2022

@author: Jhonatan Martínez
"""
import asyncio

from loguru import logger
from typing import Dict, List
import asyncpg
from .constants import *


class AsyncDB:
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
        self.__loop = asyncio.get_event_loop()
        self.__validate_attributes()

    def __validate_attributes(self) -> None:
        logger.debug(self.__setup)
        """Válida que el diccionario contenga los atributos necesarios para que la clase funcione."""
        missing_attributes = [key for key in self.__attributes if str(key).lower() not in self.__setup.keys()]
        if len(missing_attributes) > 0:
            logger.error(MISSING_ATTRIBUTES)
            logger.error(missing_attributes)

    async def __open_connection(self) -> bool:
        """Crear y obtener la conexión a una base de datos

        Returns:
            bool: True si se establece la conexión, False en caso contrario.
        """

        self.__connection = None
        try:
            self.__connection = await asyncpg.connect(host=self.__setup["host"],
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

    async def read_data(self, query: str, parameters: tuple = (), datatype: str = "dict") -> [Dict, List]:
        """Obtener los datos de una consulta.

        Args:
            query (str): Consulta a ejecutar.
            parameters (tuple, optional): Parámetros de la consulta.
            datatype (str, optional): Tipo de datos a retornar.

        Returns:
            show_data[Dict,List]: Datos obtenidos.
        """
        show_data = None
        if await self.__open_connection():
            datatype = datatype.lower()
            if datatype in ['dict', 'list']:
                try:
                    async with self.__connection.transaction():
                        query_result = await self.__connection.fetch(query, *parameters)
                        query = self.__connection.mogrify(query, *parameters)
                        data = [dict(row.items()) for row in query_result]
                        # Gets column_names
                        columns = [column.upper() for column in query_result[0].keys()] if query_result else []
                        # Validate the datatype to return
                        if datatype == 'dict':
                            show_data = data
                        elif datatype == 'list':
                            show_data = [columns, data]
                        logger.info(f"{DATA_OBTAINED} {query.decode('utf-8')}")
                except Exception as exc:
                    logger.error(str(exc), exc_info=True)
            else:
                logger.warning(INVALID_DATATYPE)
        else:
            logger.warning(NO_CONNECTION)

        return show_data