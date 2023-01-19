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


chaliceapp.py
This files is the infrastructure as a code in CDK, it generates the required integrations
required for this project.

"""
from chalice.cdk import Chalice
import os
import json

from aws_cdk import (
    Duration,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_stepfunctions as steps,
    aws_stepfunctions_tasks as tasks)

try:
    from aws_cdk import core as cdk
except ImportError:
    import aws_cdk as cdk


RUNTIME_SOURCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), os.pardir, "runtime"
)


class ChaliceApp(cdk.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.dynamodb_table = self._create_ddb_table()
        self.chalice = Chalice(
            self,
            "ChaliceApp",
            source_dir=RUNTIME_SOURCE_DIR,
            stage_config={
                "environment_variables": {
                    "APP_TABLE_NAME": self.dynamodb_table.table_name
                }
            },
        )
        self.dynamodb_table.grant_read_write_data(
            self.chalice.get_role("DefaultRole"))

        self.step_functions = self._custom_workflow(self.dynamodb_table)

        self.async_lambda = self._set_ddb_trigger_function(
            self.dynamodb_table, self.step_functions)

    def _create_ddb_table(self):
        dynamodb_table = dynamodb.Table(
            self,
            "AppTable",
            partition_key=dynamodb.Attribute(
                name="PK", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        cdk.CfnOutput(self, "AppTableName", value=dynamodb_table.table_name)
        return dynamodb_table

    def _set_ddb_trigger_function(self, ddb_table, step_function):

        async_lambda = _lambda.Function(
            self,
            "AsyncHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("streams_lambda"),
            handler="app.handler",
            environment={
                "STEP_FUNCTION_ARN": step_function.state_machine_arn
            },
        )

        async_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "states:StartExecution",
                ],
                resources=[step_function.state_machine_arn],
            )
        )
        ddb_table.grant_stream_read(async_lambda)

        company_inserts = _lambda.CfnEventSourceMapping(
            scope=self,
            id="InsertsOnlyEventSourceMapping",
            function_name=async_lambda.function_name,
            event_source_arn=ddb_table.table_stream_arn,
            maximum_batching_window_in_seconds=1,
            starting_position="LATEST",
            batch_size=1,
        )

        company_inserts.add_property_override(
            property_path="FilterCriteria",
            value={
                "Filters": [
                    {
                        "Pattern": json.dumps(
                            {
                                "eventName": ["INSERT", "MODIFY"],
                            }
                        )
                    }
                ]
            },
        )
        return async_lambda

    def _update_function(self, ddb_table):
        update_lambda = _lambda.Function(
            self,
            "update_lambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("update_lambda"),
            handler="app.handler",
            environment={
                "APP_TABLE_NAME": ddb_table.table_name,
            },
        )

        ddb_table.grant_read_write_data(update_lambda)

        return update_lambda

    def _random_function(self):
        random_lambda = _lambda.Function(
            self,
            "random_lambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("random_lambda"),
            handler="app.handler",
        )
        return random_lambda

    def _custom_workflow(self, ddb_table):

        # It requires two lambdas one for update DDB and antoher for the random counter
        self.random_lambda = self._random_function()
        self.update_lambda = self._update_function(ddb_table)

        start_step = steps.Pass(self, "Start Workflow")
        wait_step = steps.Wait(self,
                               "Wait 10 Seconds",
                               time=steps.WaitTime.duration(Duration.seconds(15)))

        definition = start_step.next(
            steps.Choice(self, "Item Status")
            .when(steps.Condition.string_equals("$.workflow_step", "NEW"),
                  tasks.LambdaInvoke(self,
                                     "UpdateNewLambda",
                                     result_path="$.status",
                                     lambda_function=self.update_lambda,
                                     payload=steps.TaskInput.from_object({
                                         "Keys": steps.JsonPath.object_at("$.Keys"),
                                         "Update": {"workflow_status": "ACTIVE"},
                                     })
                                     )
                  .next(wait_step)
                  .next(tasks.LambdaInvoke(
                      self,
                      "Get Random Number",
                      result_path="$.random_number",
                      result_selector={
                          "number_selected.$": "$.Payload.return_number"
                      },
                      lambda_function=self.random_lambda)
                .next(steps.Choice(self, "Check Number Value")
                      .when(steps.Condition.number_less_than_equals("$.random_number.number_selected", 7),
                      tasks.LambdaInvoke(self,
                                         "UpdateWithSuccess",
                                         result_path="$.status",
                                         lambda_function=self.update_lambda,
                                         payload=steps.TaskInput.from_object({
                                             "Keys": steps.JsonPath.object_at("$.Keys"),
                                             "Update": {"workflow_status": "SUCCESS"},
                                         })
                                         ).
                      next(steps.Pass(self, "Success!")))
                      .when(steps.Condition.number_greater_than_equals("$.random_number.number_selected", 8),
                      tasks.LambdaInvoke(self,
                                         "UpdateWithFail",
                                         result_path="$.status",
                                         lambda_function=self.update_lambda,
                                         payload=steps.TaskInput.from_object({
                                             "Keys": steps.JsonPath.object_at("$.Keys"),
                                             "Update": {"workflow_status": "FAILED"},
                                         })
                                         ).
                      next(steps.Pass(self, "Failed")))
                      )))
            .when(steps.Condition.string_equals("$.workflow_step", "FAILED"),
                  tasks.LambdaInvoke(self,
                                     "UpdateRetryLambda",
                                     result_path="$.status",
                                     lambda_function=self.update_lambda,
                                     payload=steps.TaskInput.from_object({
                                         "Keys": steps.JsonPath.object_at("$.Keys"),
                                         "Update": {"workflow_status": "ACTIVE"},
                                         "increment": 1
                                     })
                                     )
                  .next(wait_step))
        )

        return steps.StateMachine(
            self,
            "EpisodeThreeStateMachine",
            definition=definition,
            timeout=Duration.minutes(10),
        )
