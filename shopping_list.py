import sqlite3
from abc import abstractmethod, ABC
from typing import Dict, List

from barcode_lookup import BarcodeLookup


class ShoppingItem(object):
    def __init__(self, barcode: str, name: str, quantity: int):
        self.barcode = barcode
        self.name = name
        self.quantity = quantity

    def to_dict(self) -> dict:
        return {"barcode": self.barcode, "name": self.name, "quantity": self.quantity}


class ShoppingList(object):
    def __init__(self, lookup: BarcodeLookup, persistence_db: str, cache: BarcodeLookup = None):
        """
        The shopping list object, it translates barcodes into items on the list.
        :param lookup: The barcode translation service.
        :param persistence_db: The name of the sqlite db to persist the shopping list to.
        :param cache: An optional local cache that is searched before the lookup.
        """
        self._persistence = ShoppingListSqliteStore(persistence_db)
        self._lookup = lookup
        self._cache = cache
        self._items: Dict[str, ShoppingItem] = self._persistence.load()

    def add(self, barcode: str, quantity: int = 1):
        if barcode not in self._items:
            # Try local cache first
            try:
                if self._cache is None:
                    raise ValueError()
                name = self._cache.name(barcode)
            except ValueError:
                # Try external source afterwards
                try:
                    name = self._lookup.name(barcode)
                except ValueError:
                    name = f"Unknown Product ({barcode})"
            self._items[barcode] = ShoppingItem(barcode, name, 0)
            self._persistence.create(barcode, name, 0)
        self._items[barcode].quantity += quantity
        self._persistence.update(barcode, self._items[barcode].quantity)

    def remove(self, barcode: str, quantity: int = 1):
        if barcode in self._items:
            self._items[barcode].quantity -= quantity
            if self._items[barcode].quantity <= 0:
                del self._items[barcode]
                self._persistence.delete(barcode)
            else:
                self._persistence.update(barcode, self._items[barcode].quantity)

    def delete(self, barcode: str):
        if barcode in self._items:
            del self._items[barcode]
            self._persistence.delete(barcode)

    def get_all(self) -> List[ShoppingItem]:
        return [item for _, item in self._items.items()]

    def get(self, barcode: str) -> ShoppingItem:
        return self._items[barcode]

    def to_dict(self) -> List[dict]:
        return [i.to_dict() for i in self.get_all()]


class ShoppingListStore(ABC):
    @abstractmethod
    def create(self, barcode: str, name: str, quantity: int):
        pass

    @abstractmethod
    def update(self, barcode: str, quantity: int):
        pass

    @abstractmethod
    def delete(self, barcode: str):
        pass

    @abstractmethod
    def load(self) -> Dict[str, ShoppingItem]:
        pass


class ShoppingListSqliteStore(ShoppingListStore):
    def __init__(self, database_name: str):
        self.conn = sqlite3.connect(database_name)
        with self.conn as curr:
            curr.execute('create table if not exists ShoppingList('
                         '  barcode text NOT NULL PRIMARY KEY,'
                         '  name text NOT NULL,'
                         '  quantity integer NOT NULL'
                         ');')

    def create(self, barcode: str, name: str, quantity: int):
        curr = self.conn.cursor()
        curr.execute('INSERT OR REPLACE INTO ShoppingList VALUES (?, ?, ?);', (barcode, name, quantity))
        self.conn.commit()
        curr.close()

    def update(self, barcode: str, quantity: int):
        curr = self.conn.cursor()
        curr.execute('UPDATE ShoppingList SET quantity = ? WHERE barcode = ?;', (quantity, barcode))
        self.conn.commit()
        curr.close()

    def delete(self, barcode: str):
        curr = self.conn.cursor()
        curr.execute('DELETE FROM ShoppingList WHERE barcode=?;', (barcode,))
        self.conn.commit()
        curr.close()

    def load(self) -> Dict[str, ShoppingItem]:
        shopping_list = {}
        curr = self.conn.cursor()
        for row in curr.execute('SELECT * FROM ShoppingList'):
            shopping_list[row[0]] = ShoppingItem(row[0], row[1], row[2])
        curr.close()
        return shopping_list
