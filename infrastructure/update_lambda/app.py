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

import os
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
dynamodb_table = dynamodb.Table(os.environ.get("APP_TABLE_NAME", ""))
dynamodb_client = boto3.client("dynamodb")


def handler(event, context):

    print(event)
    # Event should provide keys and update value
    try:
        update_expression = "SET "
        update_expression_att = {}
        update_epxression_att_val = {}
        event["Update"]["updated_datetime"] = datetime.now().isoformat()
        for k, v in event["Update"].items():
            print(k)
            print(v)
            update_expression += "#"+k + " = :" + k + ", "
            update_expression_att["#"+k] = k
            update_epxression_att_val[":"+k] = {"S": v}

        if "increment" in event:
            update_expression += "#attempts = #attempts + :attempts"
            update_expression_att["#attempts"] = "attempts"
            update_epxression_att_val[":attempts"] = {
                "N": str(event["increment"])}
        else:
            update_expression = update_expression[:-2]

        response = dynamodb_client.update_item(
            TableName=os.environ.get("APP_TABLE_NAME", ""),
            Key=event["Keys"],
            UpdateExpression=update_expression,
            ExpressionAttributeNames=update_expression_att,
            ExpressionAttributeValues=update_epxression_att_val
        )
        # return response
        return {"statusCode": 200, "result": response}
    except ClientError as e:

        if e.response["Error"]["Code"] == "ValidationException":
            # We need to rebuild the entire expression
            update_expression = "SET "
            update_expression_att = {}
            update_epxression_att_val = {}
            for k, v in event["Update"].items():
                print(k)
                print(v)
                update_expression += "#"+k + " = :" + k + ", "
                update_expression_att["#"+k] = k
                update_epxression_att_val[":"+k] = {"S": v}

            if "increment" in event:
                update_expression += "#attempts" + " = :attempts"
                update_expression_att["#attempts"] = "attempts"
                update_epxression_att_val[":attempts"] = {
                    "N": str(event["increment"])}
            else:
                update_expression = update_expression[:-2]

            response = dynamodb_client.update_item(
                TableName=os.environ.get("APP_TABLE_NAME", ""),
                Key=event["Keys"],
                UpdateExpression=update_expression,
                ExpressionAttributeNames=update_expression_att,
                ExpressionAttributeValues=update_epxression_att_val
            )
            return {"statusCode": 200, "result": response}

        print(e.response["Error"]["Code"])
        return {"statusCode": 500, "result": None}

# Fix this logic to make it generic and also auto-increment the values.
