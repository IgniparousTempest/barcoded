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
    def __init__(self, lookup: BarcodeLookup, cache: BarcodeLookup = None):
        """
        The shopping list object, it translates barcodes into items on the list.
        :param lookup: The barcode translation service.
        :param cache: An optional local cache that is searched before the lookup.
        """
        self._lookup = lookup
        self._cache = cache
        self._items: Dict[str, ShoppingItem] = {}

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
        self._items[barcode].quantity += quantity

    def remove(self, barcode: str, quantity: int = 1):
        if barcode in self._items:
            self._items[barcode].quantity -= quantity
            if self._items[barcode].quantity <= 0:
                del self._items[barcode]

    def delete(self, barcode: str):
        if barcode in self._items:
            del self._items[barcode]

    def get_all(self) -> List[ShoppingItem]:
        return [item for _, item in self._items.items()]

    def get(self, barcode: str) -> ShoppingItem:
        return self._items[barcode]

    def to_dict(self) -> List[dict]:
        return [i.to_dict() for i in self.get_all()]
