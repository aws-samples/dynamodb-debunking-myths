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
import json
import boto3
from datetime import date, datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


step_functions = boto3.client('stepfunctions')


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

        ddb_item = item["dynamodb"]["NewImage"]
        ddb_keys = item["dynamodb"]["Keys"]
        workflow_step = "NEW"

        if "workflow_status" in ddb_item:
            workflow_step = ddb_item["workflow_status"]["S"]

        step_payload = {"Keys": ddb_keys, "workflow_step": workflow_step}

        response = step_functions.start_execution(
            stateMachineArn=os.environ["STEP_FUNCTION_ARN"],
            input=json.dumps(step_payload, default=json_serial))

    return {"statusCode": 200, "result": response}
