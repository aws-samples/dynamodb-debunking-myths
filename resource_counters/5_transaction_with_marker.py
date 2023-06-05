"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

5_transaction_with_marker.py


"""

import boto3
import uuid

TABLE_NAME = "pk-only"
INIT_COUNTER = True
PK = "abc123"
CRT_VALUE = "edaf-4999-9878-23tf2"

dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table(TABLE_NAME)

if INIT_COUNTER:
    response = table.put_item(Item={"pk": PK, "quantity": 21})

response = dynamodb.transact_write_items(
    TransactItems=[
        {
            "Update": {
                "TableName": TABLE_NAME,
                "Key": {"pk": {"S": PK}},
                "UpdateExpression": "ADD quantity :change",
                "ConditionExpression": "quantity >= :threshold",
                "ExpressionAttributeValues": {
                    ":change": {"N": "-5"},
                    ":threshold": {"N": "5"},
                },
            }
        },
        {
            "Put": {
                "TableName": TABLE_NAME,
                "Item": {"pk": {"S": CRT_VALUE}},
                "ConditionExpression": "attribute_not_exists(pk)",
            }
        },
    ]
)

counter = table.get_item(Key={"pk": PK})

print(counter["Item"])
