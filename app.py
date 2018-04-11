from typing import List

from flask import Flask, jsonify, request, render_template, Response

from barcode_lookup import BarcodeLookupUPCDatabaseOrg, BarcodeLookupSQLite
from shopping_list import ShoppingList, ShoppingItem

app = Flask(__name__)

barcode_lookup = BarcodeLookupSQLite("upc_database.json")
shopping_list = ShoppingList(barcode_lookup)
shopping_list.add("4890008100309")


def barcode_validate(barcode: str) -> bool:
    """
    Ensures the barcode is valid, i.e. not sqli, xss or other nonsense.
    :param barcode: The barcode to validate.
    :return: Whether the barcode is valid or not.
    """
    return barcode.isdigit()


def dict_shopping_list(list_data: ShoppingList) -> List[dict]:
    """
    Returns a shopping list as a list of dictionaries, sorted by shopping item name.
    :param list_data: The shopping list.
    :return: A sorted list of dictionaries.
    """
    dict_list = list_data.to_dict()
    dict_list.sort(key=lambda i: i["name"])
    return dict_list


def json_base(data: dict, status: int = 200, message: str = '') -> Response:
    data['status'] = status
    data['message'] = message
    return jsonify(data)


def json_shopping_list(list_data: ShoppingList) -> Response:
    return json_base({'shoppingList': dict_shopping_list(list_data)})


def json_shopping_item(item: ShoppingItem) -> Response:
    return json_base(item.to_dict())


def json_barcode_does_not_exist(barcode: str) -> Response:
    return json_base({'barcode': barcode}, 404, 'The barcode does not exist.')


def api_add_to_shopping_item(barcode: str, addend: int):
    try:
        shopping_list.add(barcode, addend)
        return json_shopping_item(shopping_list.get(barcode))
    except KeyError:
        return json_barcode_does_not_exist(barcode), 404


def api_remove_from_shopping_item(barcode: str, subtrahend: int):
    try:
        item = shopping_list.get(barcode)
        shopping_list.remove(barcode, subtrahend)
        try:
            return json_shopping_item(shopping_list.get(barcode))
        except KeyError:
            item.quantity = 0
            return json_shopping_item(item)
    except KeyError:
        return json_barcode_does_not_exist(barcode), 404


@app.route('/')
def home():
    return render_template('index.html', items=dict_shopping_list(shopping_list))


@app.route('/api/shopping')
def api_get_shopping_list():
    """
    Returns the current shopping list, in the form of:
    [
        {'barcode': '1234567890123', 'name': 'Hamburger', 'quantity': 10},
        {'barcode': '0000000000000', 'name': 'Milk', 'quantity': 2}
    ]
    :return: JSON list of shopping items.
    """
    return json_shopping_list(shopping_list)


@app.route('/api/item/<barcode>', methods=['DELETE', 'GET', 'POST'])
def api_shopping_item(barcode):
    """
    Alters a shopping item.

    #GET:
        Returns the item.

    #POST:
        Adds or removes from the quantity of the selected item, requires input in the form of:
        {'barcode': '1234567890123', 'quantity_change': -1}.
        If the quantity is reduce to 0, the item is deleted.
        Throws a 400 error if a 0 quantity is provided.

    #DELETE:
        Removes the item from the shopping list.

    :param barcode: The barcode to alter.
    :return: A JSON blob representing the result of the operation, in the form:
    {'barcode': '1234567890123', 'name': 'Hamburger', 'quantity': 10}
    :except: 404, if the item is not on the shopping list.
    :except: 400, if a POST with an invalid quantity is provided.
    :except: 400, if the barcode is not valid.
    """
    if not barcode_validate(barcode):
        return jsonify({'status': 400, 'message': 'The barcode was a not a valid UPC or EAN code.'}), 400

    if request.method == 'DELETE':
        try:
            shopping_list.delete(barcode)
            return jsonify({"barcode": barcode, 'status': 200, 'message': ''})
        except KeyError:
            return json_barcode_does_not_exist(barcode), 404
    elif request.method == 'GET':
        try:
            item = shopping_list.get(barcode)
            return json_shopping_item(item)
        except KeyError:
            return json_barcode_does_not_exist(barcode), 404
    elif request.method == 'POST':
        data = request.form
        quantity_change = int(data["quantity_change"])
        if quantity_change > 0:
            return api_add_to_shopping_item(barcode, quantity_change)
        elif quantity_change < 0:
            return api_remove_from_shopping_item(barcode, -quantity_change)
        else:
            return jsonify({'barcode': barcode, 'status': 400, 'message': 'Can\'t add or subtract 0.'}), 400
    else:
        return 403


if __name__ == '__main__':
    # Default port is 41040: Numeric values of LIST multiplied together, very cute indeed.
    app.run(host='0.0.0.0', port=41040)
