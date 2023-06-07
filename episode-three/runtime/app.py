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

runtime/app.py
This file generates the API methods required to write to the DynamoDB tables, 

"""
import os
import boto3
from chalice import Chalice

app = Chalice(app_name="twitch-episode-three-ddb")
dynamodb = boto3.resource("dynamodb")
dynamodb_table = dynamodb.Table(os.environ.get("APP_TABLE_NAME", ""))
dynamodb_client = boto3.client("dynamodb")


# - 1. Set company by company_id
@app.route("/task", methods=["POST"])
def set_company_role():
    request = app.current_request.json_body
    item = {
        "PK": "TASK#%s" % request["task_id"],
    }
    item.update(request)
    dynamodb_table.put_item(Item=item)
    # TODO: Return a useful response for the API in all cases
    return {}


# - 2. Get company by company_id
@app.route("/task/{task_id}", methods=["GET"])
def get_company_root(task_id):
    key = {
        "PK": "TASK#%s" % task_id,
    }
    item = dynamodb_table.get_item(Key=key)["Item"]
    del item["PK"]
    return item
