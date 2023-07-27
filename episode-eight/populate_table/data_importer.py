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

"""

import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
cf_client = boto3.client("cloudformation")
stackname = "DdbPermissionsLabStack"
table_name = ""

try:
    response = cf_client.describe_stacks(StackName=stackname)
    outputs = response["Stacks"][0]["Outputs"]
    for output in outputs:
        keyName = output["OutputKey"]
        if keyName == "PermissionsTableName":
            print(output["OutputValue"])
            table_name = output["OutputValue"]
except ClientError:
    print("You need to run cdk deploy first to get the stack deployed.")

if table_name:
    table = dynamodb.Table(table_name)

    customers = []

    with open("base_transportation.json", "r") as file:
        customers = json.load(file)

    with table.batch_writer() as batch:

        for item in customers:
            record = {}
            record["PK"] = item["user_name"]
            record["SK"] = "#ROOT#"
            record["user_name"] = item["user_name"]
            record["first_name"] = item["first_name"]
            record["last_name"] = item["last_name"]
            record["email"] = item["email"]
            record["address"] = item["address"]
            batch.put_item(Item=record)

    trips = []
    with open("mock_data_trips.json", "r") as file2:
        trips = json.load(file2)

    with table.batch_writer() as batch:
        for item in trips:
            batch.put_item(Item=item)
