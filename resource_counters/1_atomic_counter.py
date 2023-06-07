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

1_atomic_counter.py


"""

import boto3
import sys

TABLE_NAME = "pk-only"
INIT_COUNTER = len( sys.argv ) < 2
PK = "abc123"

table = boto3.resource("dynamodb").Table(TABLE_NAME)

if INIT_COUNTER:
    # Initialise the counter
    print("*** Initialised the counter ***")
    response = table.put_item(Item={"pk": "abc123", "quantity": 7})

# Update the counter with a threshold
response = table.update_item(
    Key={"pk": PK},
    UpdateExpression="ADD quantity :change",
    ConditionExpression="quantity >= :threshold",
    ExpressionAttributeValues={":change": -3, ":threshold": 3},
    ReturnValues="UPDATED_NEW",
)

counterValue = response["Attributes"]

print(counterValue)

