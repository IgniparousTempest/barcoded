import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path

import requests
from flask import json


class BarcodeLookup(ABC):
    @abstractmethod
    def name(self, barcode: str) -> str:
        """
        Retrieves the name from the barcode.
        :param barcode: The barcode to lookup
        :return: The name of the product.
        :except: ValueError if the barcode is not found.
        """
        pass


class BarcodeLookupUPCDatabaseOrg(BarcodeLookup):
    def __init__(self, api_key: str):
        """
        Uses the website: https://www.upcdatabase.org.
        :param api_key: The secret API key.
        """
        self.api_key = api_key

    def name(self, barcode: str) -> str:
        url = 'https://api.upcdatabase.org/product/{}/{}'.format(barcode, self.api_key)
        response = requests.get(url).json()
        if response.get("error"):
            raise ValueError("Barcode not found")
        name = response.get("alias")
        title = response.get("title")

        if name != "":
            return name
        elif title != "":
            return title
        else:
            return response.get("description")


class BarcodeLookupSQLite(BarcodeLookup):
    def __init__(self, json_name: str, database_name: str = None):
        """
        Uses a SQLite database. The first time the class is run, it constructs the SQLite DB from a JSON file.
        The JSON file makes version control with git easier.
        :param json_name: The name of the JSON file to construct db with.
        :param database_name: The name of the database file. If None is provided an in memory db will be created on launch.
        """
        if database_name is None:
            db_exists = False
            database_name = ":memory:"
        else:
            db_exists = Path(database_name).is_file()

        self.database_name = database_name
        self.conn = sqlite3.connect(database_name)
        with self.conn as curr:
            curr.execute('create table if not exists ShoppingList(barcode text NOT NULL PRIMARY KEY, name text NOT NULL);')

        if not db_exists:
            curr = self.conn.cursor()
            with open(json_name, 'r', encoding='utf-8') as f:
                for item in json.load(f):
                    curr.execute('INSERT INTO ShoppingList VALUES (?, ?);', (item['barcode'], item['name']))
            self.conn.commit()
            curr.close()

    def name(self, barcode: str) -> str:
        curr = self.conn.cursor()
        curr.execute('SELECT * FROM ShoppingList WHERE barcode=?', (barcode,))
        row = curr.fetchone()
        if row is None:
            raise ValueError("Barcode not found")
        curr.close()
        return row[1]
