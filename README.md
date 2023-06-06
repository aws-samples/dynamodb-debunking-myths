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

This is the branch that covers the episode seven.

# Episode Seven - Myth #3: You can’t implement atomic counters with Amazon DynamoDB.

In this episode we will be interviewing Chris Gillespie and Jason Hunter, since they have recently wrote a blog about how to [implement resource counters with Amazon DynamoDB](https://aws.amazon.com/blogs/database/implement-resource-counters-with-amazon-dynamodb/). At this point in the Series we are discussing how to implement certain functionalities that are often over-simplified, however when we need to think about scale and massive paralell computing there are some elements you need to consider.

Chris will walk us through seven approaches for managing counters.

1. [Atomic counters](./resource_counters/1_atomic_counter.py)
2. [Optimistic concurrency control](./resource_counters/2_occ.py)
3. [Optimistic concurrency control with history](./resource_counters/3_occ_with_history.py)
4. [Transaction with a client request token](./resource_counters/4_transaction.py)
5. [Transaction with a marker item](./resource_counters/5_transaction_with_marker.py)
6. [Counting with an item collection](./resource_counters/6_item_collection.py)
7. [Counting with a set](./resource_counters/7_with_a_set.py)
