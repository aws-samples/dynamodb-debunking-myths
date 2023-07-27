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


ddb_permissions_lab_stack.py
This is the main application code, it will generate all your infrastructure code and
up the required permissions.

"""

from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
)


from aws_solutions_constructs.aws_lambda_dynamodb import (
    LambdaToDynamoDBProps,
    LambdaToDynamoDB,
)
from constructs import Construct


class DdbPermissionsLabStack(Stack):
    def _create_ddb_table(self):
        dynamodb_table = dynamodb.Table(
            self,
            "PermissionsTable",
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=RemovalPolicy.DESTROY,
        )

        CfnOutput(self, "PermissionsTableName", value=dynamodb_table.table_name)

        return dynamodb_table

    def _scan_lambda(self, ddb_table):
        scan_lambda = _lambda.Function(
            self,
            "ScanLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("src/scan_lambda"),
            handler="app.handler",
            environment={
                "DDB_TABLE_NAME": ddb_table.table_name,
            },
            timeout=Duration.seconds(300),
        )
        # grant full access to the dynamodb table ddb_table
        # ddb_table.grant_full_access(scan_lambda)

        # Provides read only access to the table
        # ddb_table.grant_read_data(scan_lambda)

        # Provides query only acces to the dynamodb table
        dynamodb_policy = iam.Policy(
            self,
            "ddb-policy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    resources=[ddb_table.table_arn],
                    actions=["dynamodb:Query"],
                    conditions={
                        "DateGreaterThan": {"aws:CurrentTime": "2023-06-01T00:00:00Z"},
                        "DateLessThan": {"aws:CurrentTime": "2023-06-30T23:59:00Z"},
                    },
                )
            ],
        )
        scan_lambda.role.attach_inline_policy(dynamodb_policy)

        return scan_lambda

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creates a DynamoDB Table.
        ddb_table = self._create_ddb_table()

        # Creates the Lambda function that will execute the code.
        self._scan_lambda(ddb_table)
