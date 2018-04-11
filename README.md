# barcoded

![Screenshot](/../images/screenshot.png?raw=true "Screenshot")

## REST end points:

| Title            | Retrieve Shopping List                                        |
|------------------|---------------------------------------------------------------|
| URL              | /api/shopping                                                 |
| Method           | GET                                                           |
| URL Params       | None                                                          |
| Data Params      | None                                                          |
| Success Response | **Example:**<br/>**Code:** 200<br/>**Content:** {<br/>'shoppingList': [<br/>     {'barcode': '1234567890123', 'name': 'Hamburger', 'quantity': 10},<br/>     {'barcode': '1234567890123', 'name': 'Hamburger', 'quantity': 10}<br/>],<br/>'status': 200,<br/>'message': ''<br/>} |
| Error Response   | None                                                          |
| Sample Call      | curl -X GET http://localhost:5000/api/shopping                |

| Title            | Retrieve Shopping List Item                                   |
|------------------|---------------------------------------------------------------|
| URL              | /api/item/<barcode>                                           |
| Method           | GET                                                           |
| URL Params       | **Required:**<br/>barcode: The barcode to lookup              |
| Data Params      | None                                                          |
| Success Response | **Example:**<br/>**Code:** 200<br/>**Content:** {'barcode': '1234567890123', 'name': 'Hamburger', 'quantity': 10, 'status': 200, message': ''} |
| Error Response   | **Code:** 400 BAD REQUEST<br/>**Content:** {'status': 400, 'message': 'The barcode was a not a valid UPC or EAN code.'<br/>OR<br/>**Code:** 404 NOT FOUND<br/>**Content:** {'barcode': '1234567890123', 'status': 404, 'message': 'The barcode does not exist.'} |
| Sample Call      | curl -X GET http://localhost:5000/api/item/6009510800043      |

| Title            | Update Shopping List Item Quantity                            |
|------------------|---------------------------------------------------------------|
| URL              | /api/item/<barcode>                                           |
| Method           | POST                                                          |
| URL Params       | **Required:**<br/>barcode: The barcode to lookup              |
| Data Params      | {'quantity_change': -1}                                       |
| Success Response | **Example:**<br/>**Code:** 200<br/>**Content:** {'barcode': '1234567890123', 'name': 'Hamburger', 'quantity': 9, 'status': 200, message': ''} |
| Error Response   | **Code:** 400 BAD REQUEST<br/>**Content:** {'barcode': '1234567890123', 'status': 400, 'message': 'Can't add or subtract 0.'OR<br/>**Code:** 400 BAD REQUEST<br/>**Content:** {'status': 400, 'message': 'The barcode was a not a valid UPC or EAN code.'<br/>OR<br/>**Code:** 404 NOT FOUND<br/>**Content:** {'barcode': '1234567890123', 'status': 404, 'message': 'The barcode does not exist.' |
| Sample Call      | curl --data "quantity_change=1" http://localhost:5000/api/item/6009510800043 |

| Title            | Delete Shopping List Item                                     |
|------------------|---------------------------------------------------------------|
| URL              | /api/item/<barcode>                                           |
| Method           | DELETE                                                        |
| URL Params       | **Required:**<br/>barcode: The barcode to delete              |
| Data Params      | None                                                          |
| Success Response | **Example:**<br/>**Code:** 200<br/>**Content:** {'barcode': '1234567890123', 'status': 200, message': ''} |
| Error Response   | **Code:** 400 BAD REQUEST<br/>**Content:** {'status': 400, 'message': 'The barcode was a not a valid UPC or EAN code.'<br/>OR<br/>**Code:** 404 NOT FOUND<br/>**Content:** {'barcode': '1234567890123', 'status': 404, 'message': 'The barcode does not exist.' |
| Sample Call      | curl -X DELETE http://localhost:5000/api/item/6009510800043   |
