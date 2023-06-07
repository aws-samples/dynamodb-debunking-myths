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

3_occ_with_history.py


"""

import boto3
import uuid
import sys

TABLE_NAME = "pk-only"
INIT_COUNTER = len( sys.argv ) < 2
PK = "abc123"

table = boto3.resource("dynamodb").Table(TABLE_NAME)

if INIT_COUNTER:
    response = table.put_item(Item={"pk": PK, "quantity": 4, "entityTag": ""})

# OCC - GET THE COUNTER
current = table.get_item(Key={"pk": PK})

currentValue = current["Item"]["quantity"]
currentEntityTagValue = current["Item"]["entityTag"]
str(uuid.uuid4())[0:8]
newEntityTag = [currentEntityTagValue, str(uuid.uuid4())[0:8]]
if "" in newEntityTag:
    newEntityTag.remove("")
newEntityTagValue = "-".join(newEntityTag)

# UPDATE THE COUNTER, BUT ONLY IF currentEntityTagValue HAS NOT CHANGED
response = table.update_item(
    Key={"pk": PK},
    UpdateExpression="SET quantity = :newValue, entityTag = :newEntityTagValue",
    ConditionExpression="attribute_not_exists(entityTag) OR entityTag = :oldEntityTagValue",
    ExpressionAttributeValues={
        ":newValue": currentValue + 1,
        ":oldEntityTagValue": currentEntityTagValue,
        ":newEntityTagValue": newEntityTagValue,
    },
    ReturnValues="UPDATED_NEW",
)

counterValue = response["Attributes"]

print(counterValue)

