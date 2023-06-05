"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the pSoftware is furnished to do so.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

7_with_a_set.py


"""

import boto3
import uuid

TABLE_NAME = "pk-only"
INIT_COUNTER = True
PK = "abc123"

table = boto3.resource("dynamodb").Table(TABLE_NAME)

if INIT_COUNTER:
    # CREATE THE COUNTER
    # Note that DDB does not support empty sets, so we exclude that attribute
    response = table.put_item(Item={"pk": PK, "slotsFilled": 0})

token = str(uuid.uuid4())[0:4]

# ATOMIC COUNTER
response = table.update_item(
    Key={"pk": PK},
    UpdateExpression="ADD tokens :token, slotsFilled :change",
    ConditionExpression="attribute_not_exists(tokens) OR (size(tokens) < :maxsize AND NOT contains(tokens, :tokenstr))",
    ExpressionAttributeValues={
        ":token": set([token]),
        ":tokenstr": token,
        ":maxsize": 50,
        ":change": 1,
    },
    ReturnValues="UPDATED_NEW",
)

counterValue = response["Attributes"]

print(counterValue)
