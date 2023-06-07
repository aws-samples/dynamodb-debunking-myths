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

app = Chalice(app_name="twitch-episode-two-ddb")
dynamodb = boto3.resource("dynamodb")
dynamodb_table = dynamodb.Table(os.environ.get("APP_TABLE_NAME", ""))
dynamodb_client = boto3.client("dynamodb")


"""
All the Access patterns:

- 1. Set company by company_id
- 2. Get company by company_id
- 3. Set product to company by company_id and product_id
- 4. Get company products by company_id
- 5. Set product total by company by product_category
- 6. Get product total by company_id and product_category
- 7. Get product total by company_id and product_category
- 8. Get product total by company_id and categories

"""


# - 1. Set company by company_id
@app.route("/company", methods=["POST"])
def set_company_role():
    request = app.current_request.json_body
    item = {
        "PK": "COMPANY#%s" % request["company_id"],
        "SK": "#ROOT#",
    }
    item.update(request)
    dynamodb_table.put_item(Item=item)
    item["SK"] = "TOTAL"
    dynamodb_table.put_item(Item=item)
    # TODO: Return a useful response for the API in all cases
    return {}


# - 2. Get company by company_id
@app.route("/company/{company_id}", methods=["GET"])
def get_company_root(company_id):
    key = {
        "PK": "COMPANY#%s" % company_id,
        "SK": "#ROOT#",
    }
    item = dynamodb_table.get_item(Key=key)["Item"]
    del item["PK"]
    del item["SK"]
    return item


# - 3. Set product to company by company_id and product_id
@app.route("/company/{company_id}/product", methods=["POST"])
def set_copmany_product(company_id):
    request = app.current_request.json_body
    # TODO exception when the categories are not present
    item = {
        "PK": {"S": f"COMPANY#{company_id}"},
        "SK": {
            "S": "PRODUCT#%s#%s#%s"
            % (
                request["cat_1"].upper(),
                request["cat_2"].upper(),
                request["product_id"],
            )
        },
    }
    print(request)
    ddb_json = {}
    for element in request:
        ddb_json[element] = (
            {"N": request[element]}
            if request[element].isdigit()
            else {"S": request[element]}
        )
        item.update(ddb_json)
    dynamodb_client.put_item(TableName=os.environ.get("APP_TABLE_NAME", ""), Item=item)

    return {}


# - 4. Get company products by company_id
@app.route("/company/{company_id}/products", methods=["GET"])
def get_company_products(company_id):
    items = dynamodb_client.query(
        TableName=os.environ.get("APP_TABLE_NAME", ""),
        KeyConditionExpression="#pk = :pk and begins_with(#sk, :sk)",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk": {"S": f"COMPANY#{company_id}"},
            ":sk": {"S": "PRODUCT"},
        },
    )["Items"]
    return items


# - 5. Set product total by company by product_category
@app.route("/company/{company_id}/product/category", methods=["POST"])
def set_company_totals_category(company_id):
    request = app.current_request.json_body
    item = {
        "PK": "COMPANY#%s" % company_id,
        "SK": "CATEGORY#%s" % request["category_id"],
    }
    item.update(request)
    dynamodb_table.put_item(Item=item)
    return {}


# - 6. Get product totals by company_id
@app.route("/company/{company_id}/totals", methods=["GET"])
def get_company_total_category(company_id):
    items = dynamodb_client.query(
        TableName=os.environ.get("APP_TABLE_NAME", ""),
        KeyConditionExpression="#pk = :pk and begins_with(#sk, :sk)",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk": {"S": f"COMPANY#{company_id}"},
            ":sk": {"S": "TOTAL"},
        },
    )["Items"]
    return items


# - 7. Get product total by company_id and product_category
@app.route("/company/{company_id}/category/{cat_1}", methods=["GET"])
def get_company_total_by_category_1(company_id, cat_1):
    items = dynamodb_client.query(
        TableName=os.environ.get("APP_TABLE_NAME", ""),
        KeyConditionExpression="#pk = :pk and begins_with(#sk, :sk)",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk": {"S": f"COMPANY#{company_id}"},
            ":sk": {"S": f"TOTAL#{cat_1.upper()}"},
        },
    )["Items"]
    return items


# - 8. Get product total by company_id and categories
@app.route("/company/{company_id}/category/{cat_1}/{cat_2}", methods=["GET"])
def get_company_total_by_category_1_and_2(company_id, cat_1, cat_2):
    items = dynamodb_client.query(
        TableName=os.environ.get("APP_TABLE_NAME", ""),
        KeyConditionExpression="#pk = :pk and begins_with(#sk, :sk)",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk": {"S": f"COMPANY#{company_id}"},
            ":sk": {"S": f"TOTAL#{cat_1.upper()}#{cat_2.upper()}"},
        },
    )["Items"]
    return items
