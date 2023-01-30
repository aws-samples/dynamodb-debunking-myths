<!-- /*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this
 * software and associated documentation files (the "Software"), to deal in the Software
 * without restriction, including without limitation the rights to use, copy, modify,
 * merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 * PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */ -->

# Debunking Amazon DynamoDB Myths.

Welcome to this repository, this is the official github repository that will be used to share the examples shared in the twitch series "Debunking Amazon DynamoDB Myths".

This is the branch that covers the episode three.

# Episode Three - Thinking NoSQL - A real world example

As a follow up from episode two, we learned that there is a functionality called Amazon DynamoDB Streams that enables event driven architectures very similar to triggers in traditional SQL databases. With Amazon DynamoDB streams, you can build event driven architectures.

During this episode, we discussed a very interesting use case from Amazon FinTech. It is a pattern that uses Triggers and Lambda functions to orchestrate a post processing logic using as base information the items stored in a DynamoDB table. This patter introduces asynchronous communication and lets other services such as Amazon Step Functions and AWS Lambda to do what they do best. Amazon DynamoDB is working in this scenario as a single source of truth.

When a new task is created, it has no attribute other than the `task_id`, this value will be enriched by the step function as the workflow progress by each step that is completed. In our scenario, we will use simulated API calls, and their responses will update the task stored in DynamoDB, allowing users to track in real time the status of any task.

![Step_function](./documentation/stepfunctions_graph.svg)

The workflow check first if the attribute `workflow_step` is set to either `NEW` or `FAILED`. In case of a `NEW` task a lambda function will update the task in DynamoDB with the status `ACTIVE` and it will then go to a Wait state for 10 seconds. When the task status is `FAILED` this workflow will update the status to `ACTIVE` as well but it will also include an incremental attribute called `attempts` to keep track of how many times this workflow has retried the operation, this branch will also end in the Wait state.

This is where we Mock an API with just a simple lambda function that will return a random number from 0 to 9. If the result is lower or equal than 7, the execution result will be `SUCCESS`, if the result is 8 or 9 the execution result will be `FAILED` and this workflow will need to be executed one more time.

## Template

This template provides a REST API that's backed by an Amazon DynamoDB table, and is deployed using the AWS CDK and Chalice.

For more information, see the [Deploying with the AWS CDK](https://aws.github.io/chalice/tutorials/cdk.html) tutorial.

## Quickstart

First, you'll need to install the AWS CDK if you haven't already.

The CDK requires Node.js and npm to run. See the [Getting started with the AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) for more details.

```
$ npm install -g aws-cdk
```

Next you'll need to install the requirements for the project.

```
$ pip install -r requirements.txt
```

There's also separate requirements files in the `infrastructure` and `runtime` directories if you'd prefer to have separate virtual environments for your CDK and Chalice app.

To deploy the application, `cd` to the `infrastructure` directory. If this is you're first time using the CDK you'll need to bootstrap your environment.

```shell
$ cd infrastructure
$ cdk bootstrap
Creating deployment package.
Reusing existing deployment package.
 ⏳  Bootstrapping environment aws://111122223333/us-east-2...
Trusted accounts for deployment: (none)
Trusted accounts for lookup: (none)
Using default execution policy of 'arn:aws:iam::aws:policy/YourPolicyAccess'. Pass '--cloudformation-execution-policies' to customize.
CDKToolkit: creating CloudFormation changeset...
 ✅  Environment aws://111122223333/us-east-2 bootstrapped.

```

Then you can deploy your application using the CDK.

```shell
$ cdk deploy
...

Creating deployment package.

✨  Synthesis time: 11.87s

ddb-twitch-episode-three: building assets...

[0%] start: Building bd2a120eea420303a3fa0a18757034d553b91bf8453784ef2a72a62fdaeb431e:current_account-current_region
...
[100%] success: Built 2d8d7430355f7ecffefd6a7c7b0a984920ad86172e74af0da472fecdcffc0020:current_account-current_region


Do you wish to deploy these changes (y/n)? y
ddb-twitch-episode-three: deploying...
[0%] start: Publishing bd2a120eea420303a3fa0a18757034d553b91bf8453784ef2a72a62fdaeb431e:current_account-current_region
...
[100%] success: Published bd2a120eea420303a3fa0a18757034d553b91bf8453784ef2a72a62fdaeb431e:current_account-current_region
ddb-twitch-episode-three: creating CloudFormation changeset...

 ✅  ddb-twitch-episode-three

✨  Deployment time: 141.73s

Outputs:
ddb-twitch-episode-three.APIHandlerArn = arn:aws:lambda:us-east-2:111122223333:function:ddb-twitch-episode-three-APIHandler-RMzjeGoJ7YO4
ddb-twitch-episode-three.APIHandlerName = ddb-twitch-episode-three-APIHandler-RMzjeGoJ7YO4
ddb-twitch-episode-three.AppTableName = ddb-twitch-episode-three-AppTable815C50BC-1XEMMP1MS1AYE
ddb-twitch-episode-three.EndpointURL = https://0b91z1i6r3.execute-api.us-east-2.amazonaws.com/api/
ddb-twitch-episode-three.RestAPIId = 0b91z1i6r3
Stack ARN:
arn:aws:cloudformation:us-east-2:111122223333:stack/ddb-twitch-episode-three/4283c0d0-a0e1-11ed-9abb-02ceaa102162

✨  Total time: 153.59s

```

## Project layout

This project template combines a CDK application and a Chalice application. These correspond to the `infrastructure` and `runtime` directory respectively. To run any CDK CLI commands, ensure you're in the `infrastructure` directory, and to run any Chalice CLI commands ensure you're in the `runtime` directory.

## Sample Queries

For the sample queries below you will need to install [httpie](https://httpie.io/) or use any other tool of your choice. Your URL can be found as Output in the CDK project `ddb-twitch-episode-three.EndpointURL`

### Example

1. Your objective is to create task using the HTTP REST API endpoint just created, to do this, execute a POST to

```
http POST <ddb-twitch-episode-three.EndpointURL>task task_id=100
```

2. To retrieve the task information, run the command:

```
http GET <ddb-twitch-episode-three.EndpointURL>task/100
```

```json
{
  "task_id": "100",
  "updated_datetime": "2023-01-30T21:05:01.576480",
  "workflow_status": "SUCCESS"
}
```

Now go and have a look to your step functions workflow where the magic is happening!

# Clean-up

Q - How do I delete the infrastructure that I just created?
A - It is very simple! run the command `cdk destroy` while you are in the `/infrastructure` folder.
Q - uh?
A -

```
$ .../dynamodb-debunking-myths/infrastructure/cdk destroy


Creating deployment package.
Reusing existing deployment package.
Are you sure you want to delete: ddb-twitch-episode-three (y/n)? y
ddb-twitch-episode-three: destroying...

 ✅  ddb-twitch-episode-three: destroyed
```

# Contributing

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional documentation, we greatly value feedback and contributions from our community. Please revisit the [CONTRIBUTING](./CONTRIBUTING.md) file.

## License

This library is licensed under the MIT-0 License. See the [LICENSE](./LICENSE) file.
