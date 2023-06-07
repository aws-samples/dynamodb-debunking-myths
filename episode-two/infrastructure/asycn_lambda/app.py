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


async_lambda/app.py
Async lambda will receive the events from DynamoDB Streams and generate real time
aggreagations by category and subcategory for given company. This example assuemes
3 categories are always provided.

All other events are sent to a SQS for further processing, (role, menu_role and users).

"""

import os
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
dynamodb_table = dynamodb.Table(os.environ.get("APP_TABLE_NAME", ""))
dynamodb_client = boto3.client("dynamodb")


def update_counters(item, sort_key, quantity):
    """
    This method updates the product counters by category.

    Args:
        item (DDB JSON): The DDB JSON for the product
        sort_key (String): Generated sort key for the counter
        quantity (String): Total number of products to add

    Returns:
        _type_: _description_
    """
    try:
        response = dynamodb_client.update_item(
            TableName=os.environ.get("APP_TABLE_NAME", ""),
            Key={"PK": item["PK"], "SK": {"S": sort_key}},
            UpdateExpression="SET #total = #total + :product",
            ExpressionAttributeNames={
                "#total": "TOTAL",
            },
            ExpressionAttributeValues={
                ":product": {"N": quantity},
            },
        )
        return response
    except ClientError as e:
        """
        If there is an error it means this is the first product of this category
        Set the product value instead of in crement
        """

        if e.response["Error"]["Code"] == "ValidationException":
            response = dynamodb_client.update_item(
                TableName=os.environ.get("APP_TABLE_NAME", ""),
                Key={"PK": item["PK"], "SK": {"S": sort_key}},
                UpdateExpression="SET #total = :product",
                ExpressionAttributeNames={
                    "#total": "TOTAL",
                },
                ExpressionAttributeValues={
                    ":product": {"N": item["products"]["N"]},
                },
            )
            return response


def handler(event, context):
    """Lambda Handler it process all the events from a dynamoDB stream prefiltered
    by the lambda rules.

    Args:
        event (JSON): DynamoDB Streams event
        context (JSON): Lambda context

    Returns:
        _type_: _description_
    """

    for item in event["Records"]:
        print(item)
        sort_key = "TOTAL"
        if "COMPANY" in item["dynamodb"]["NewImage"]["PK"]["S"]:
            if "INSERT" in item["eventName"]:
                for i in range(2):
                    sort_key += (
                        "#"
                        + item["dynamodb"]["NewImage"]["cat_" + str(i + 1)]["S"].upper()
                    )
                    print(sort_key)
                    result = update_counters(
                        item["dynamodb"]["NewImage"],
                        sort_key,
                        item["dynamodb"]["NewImage"]["products"]["N"],
                    )

            if "MODIFY" in item["eventName"]:
                for i in range(2):
                    sort_key += (
                        "#"
                        + item["dynamodb"]["NewImage"]["cat_" + str(i + 1)]["S"].upper()
                    )
                    print(sort_key)
                    product_diff = int(
                        item["dynamodb"]["NewImage"]["products"]["N"]
                    ) - int(item["dynamodb"]["OldImage"]["products"]["N"])
                    result = update_counters(
                        item["dynamodb"]["NewImage"], sort_key, str(product_diff)
                    )

    return {"statusCode": 200, "result": result}
