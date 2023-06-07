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

# Debunking Amazon DynamoDB Myths - Episode Five

We discussed all the information about DynamoDB shell with Amrit during this episode, here is the link to the official documentation [dynamodb-shell](https://github.com/awslabs/dynamodb-shell) give it a try it will change the way you think about implementing SQL queries into Amazon DynamoDB.

You can very easily install dynamodb-shell by installing the aws [homebrew-tap](https://github.com/aws/homebrew-tap). Once you have the application installed you can start exploring with the following command:

Remember before trying to open the tool you need to have configured your AWS environment variables in your machine/laptop/session, if don't you will get a connection refused error, and even if you have the cli open you will not be really connected anywhere. If you don’t modify your environment variables ddbsh will connect to the default region as specified in your aws config file.

```shell
~ ❯ ddbsh
ddbsh - version 0.3
```

You can notice something very interesting right in front of the screen, the tool is telling you to which region you are connected, you don’t really need to guess where you are, it is literally in front of you!

The first command that I personally always execute is `show tables;` make sure you add the `;` at the end, I am so used to not add `;` at this point that for me is a challenge!

```shell
us-east-2> show tables;
twitch-table-us-east-2 | ACTIVE | PAY_PER_REQUEST | STANDARD | 9f0a23cf-9e06-4732-9e00-e9847105a572 | arn:aws:dynamodb:us-east-2:111122223333:table/twitch-table-us-east-2 | TTL DISABLED | GSI: 1 | LSI : 0 |
```

For me personally this means hello world!!

Now let’s walk through one really nice feature, I want to show you how easy is to change from region to region. This is done via the [connect](https://github.com/awslabs/dynamodb-shell#connect) command: `connect ` + region.

I know what you are thinking right now... Oh but it is very easy for you since you have already run so many scripts with the tool!, and well let me tell you that I really don’t remember the commands by hearth, I always use the help; syntax.

```shell
us-east-2> help;
HELP - provide help in ddbsh

HELP <keyword> [keyword [keyword ...]]

      Provides help about the specified keyword, or statement.

      HELP ALTER TABLE
      HELP BACKUP
      HELP BEGIN
      ...
```

Now since I don’t remember exactly how to connect to the destination region I will just follow the insstructions:

```shell
us-east-2> help connect;
CONNECT - Connects to a DynamoDB region.

CONNECT <region>
CONNECT <region> WITH ENDPOINT <endpoint>

Here, <endpoint> is the URI for an internal (zeta) endpoint.
CONNECT us-east-1;
CONNECT us-east-1 with endpoint "https://..."
```

Let’s change region:

```shell
us-east-2> connect us-east-1;
CONNECT
us-east-1> show tables;
us-east-1>
```

Ok in this region I really don’t have anything to play around with, so let’s go back where we were before.

Let’s describe a table to understand the configuration and confirm the other operations works.

```shell
us-east-2> describe twitch-table-us-east-2;
Name: twitch-table-us-east-2 (ACTIVE)
Key: HASH PK, RANGE SK
Attributes: GSI1PK, S, GSI1SK, S, PK, S, SK, S
Created at: 2023-03-28T16:55:48Z
Table ARN: arn:aws:dynamodb:us-east-2:111122223333:table/twitch-table-us-east-2
Table ID: 9f0a23cf-9e06-4732-9e00-e9847105a572
Table size (bytes): 0
Item Count: 0
Billing Mode: On Demand
PITR is Enabled: [2023-03-28T17:09:59Z to 2023-03-28T17:11:51Z]
GSI query-index: ( HASH GSI1PK, RANGE GSI1SK ), Billing Mode: On Demand (mirrors table), Projecting (ALL), Status: ACTIVE, Backfilling: NO
LSI: None
Stream: NEW_AND_OLD_IMAGES
Table Class: STANDARD
SSE: Not set
```

Once here we can apply a lot of control plane operations, for example we describe one of our tables, modify the table structure and then validate that the changes actually ocurred. If you don’t remember the structure of the command, help is your friend here.

```shell
us-east-2> alter table twitch-table-us-east-2 set stream (both images);
ALTER
us-east-2> alter table twitch-table-us-east-2 set pitr enabled;
```

## Second Part - Table Operations

For the second part of this demo we need to start creating a table, since we want to see its full potential.

Here let me show you one of my favorite featues, It might be silly for many of you, but for me personally since I mainly code in python, I have forgotten how useful the semicolon is!

```shell
create table if not exists nowait twitch-games( pk string, sk string )
primary key ( pk hash, sk range )
billing mode on demand;
```

Let’s explore a couple of commands, first lets re-validate all the information we have in the reports table, but in the old table:

This command will retrieve all the data from the table, if your table has 100M items you will be returning 100M elements.

```shell
select * from twitch-table-us-east-2;
```

Now Choose one of the PK from your result and put the partition key in the space marked as `<Change Me!>` below, this will retrieve only a subset of data, only the elements that have that `PK`.

```shell
select * from twitch-table-us-east-2 where PK = "<Change Me!>";
```

Usng the same `PK` select now a characteresting from the `SK` and use the begins_with condition.

```shell
select * from twitch-table-us-east-2 where PK = "" and begins_with(SK, org);
```

What happens when you execute this command?

```shell
select * from twitch-table-us-east-2 where organization = "epsilon";
```

For all the queries that you just executed you still got the results, but what really happened behind scenes? can someone in the chat let me know what happened?

While I give one or two minutes for people to respond let’s try some update operations:

```shell
update twitch-table-us-east-2 set user_id = "tebanieo" where PK = "cca04788-157b-4207-b8f8-be58aa9fd8dd" and SK = "user_id";
UPDATE (0 read, 1 modified, 0 ccf)
```

Now back to the question, maybe by adding this flag will help you visualize what is happening:

```shell
select * from twitch-table-us-east-2 return total;
```

```shell
select * from twitch-table-us-east-2 where PK = "" return total;
```

```shell
select * from twitch-table-us-east-2 where PK = "" and begins_with(SK, org) return total;
```

```shell
select * from twitch-table-us-east-2 where organization = "epsilon" return total;
```

For this last one notice how we added the table index to retrieve the organization epsilon

```shell
select * from twitch-table-us-east-2.query-index where GSI1PK = "ORG#epsilon" return total;
```

If you can’t see the problem right away this is where Amrith come to the rescue, he has included an incredible useful functionality called `EXPLAIN`. Since showing is actuallly better than explaining and talking about it, let me show you what it does.

```shell
us-east-2> explain select \* from twitch-table-us-east-2 return total;
Scan({
"TableName": "twitch-table-us-east-2",
"ReturnConsumedCapacity": "TOTAL",
"ConsistentRead": false
})
Scan({
"TableName": "twitch-table-us-east-2",
"ExclusiveStartKey": {
"PK": {
"S": "a6cc2093-3251-417f-a222-a9b215c0e82b"
},
"SK": {
"S": "requested_by"
}
},
"ReturnConsumedCapacity": "TOTAL",
"ConsistentRead": false
})
```

```shell
us-east-2> explain select * from twitch-table-us-east-2 where PK="770bfcd7-d916-4bfd-b81b-ff70ee3036f9" return total;
Query({
"TableName": "twitch-table-us-east-2",
"ConsistentRead": false,
"ReturnConsumedCapacity": "TOTAL",
"KeyConditionExpression": "#abaa1 = :vbaa1",
"ExpressionAttributeNames": {
"#abaa1": "PK"
},
"ExpressionAttributeValues": {
":vbaa1": {
"S": "770bfcd7-d916-4bfd-b81b-ff70ee3036f9"
}
}
})
```

Finally the query that was behaving different, notice the difference in operations, even if we specified a were clause, the operation behind scenes executed an scan.

```shell
us-east-2> explain select * from twitch-table-us-east-2 where organization = "epsilon" return total;
Scan({
"TableName": "twitch-table-us-east-2",
"ReturnConsumedCapacity": "TOTAL",
"FilterExpression": "#acaa1 = :vcaa1",
"ExpressionAttributeNames": {
"#acaa1": "organization"
},
"ExpressionAttributeValues": {
":vcaa1": {
"S": "epsilon"
}
},
"ConsistentRead": false
})
Scan({
"TableName": "twitch-table-us-east-2",
"ExclusiveStartKey": {
"PK": {
"S": "a6cc2093-3251-417f-a222-a9b215c0e82b"
},
"SK": {
"S": "requested_by"
}
},
"ReturnConsumedCapacity": "TOTAL",
"FilterExpression": "#acaa1 = :vcaa1",
"ExpressionAttributeNames": {
"#acaa1": "organization"
},
"ExpressionAttributeValues": {
":vcaa1": {
"S": "epsilon"
}
},
"ConsistentRead": false
})
```

Now let’s dive deep into the explain command by using this example, we are building a RPG type of game, you can help us with the name of the game with your comments in the chat. During this game you will collect gold and diamonds to buy different goodies during the game, you can buy weapons, potions, clothes, armors, etc, etc, pretty standard on this kind of games.

We will use the table twitch-game table that was created earlier, where the datamodel looks like this.

[Twitch Games](twitch_games.png)

```shell
insert into twitch-games (pk,sk,user_id,gold,diamonds)
values ("UID#tebanieo", "ASSETS", "tebanieo", 1000, 20),
("UID#oza", "ASSETS", "oza", 1200, 20);

insert into twitch-games (pk, sk, user_id, health, stamina, strenght, type)
values ("UID#oza", "STATUS", "oza", 94, 40, 40, "mage"),
("UID#tebanieo", "STATUS", "tebanieo", 80, 40, 46, "paladin");

insert into twitch-games (pk, sk, user_id, item, status, usability, reach, damage, type)
values ("UID#oza", "INVENTORY#ACTIVE#WEAPON", "oza", "Legendary Fire Wand", "ACTIVE", 100, 500, "99-150", "wand"),
("UID#tebanieo", "INVENTORY#ACTIVE#WEAPON", "tebanieo", "Spear of Light", "ACTIVE", 100, 100, "50-70", "Spear");
```

Modify the values in the twitch games table

```shell
select * from twitch-games where pk = "UID#tebanieo" and sk = "ASSETS";
{diamonds: 20, gold: 1000, pk: UID#tebanieo, sk: ASSETS, user_id: tebanieo}

update twitch-games set gold = 1100 where pk = "UID#tebanieo" and sk = "ASSETS";
select * from twitch-games where pk = "UID#tebanieo" and sk = "ASSETS";
```

You can also specify conditions on the update increment the values.

```shell
update twitch-games set gold = gold + 100 where pk = "UID#tebanieo" and sk = "ASSETS";
```

Let’s imagine we are at this point during the game where we need to buy potions because we are going to fight one of those big bosses, this game will be a little bit realistic since it will have a limited amount of potions that you can buy, so if one of the online players want to grab all the potions for himself, he can do it!

First we would need to create the Store entity, because so far we have been working only with player data.

```shell
insert into twitch-games (pk,sk,gold,health, diamonds, item, quantity)
values ("SID#blue-montain", "ITEMS#POTIONS#HEALING_NORMAL", 50,100,1,"Normal Potion",200)
, ("SID#blue-montain","ITEMS#POTIONS#HEALING_MEGA",100,1000,1, "Mega Potion", 20);

insert into twitch-games (pk,sk, gold, stamina, diamonds, item, quantity)
values ("SID#blue-montain","ITEMS#POTIONS#STAMINA_NORMAL",100,1000,1, "Normal Stamina Recovery", 20);

insert into twitch-games (pk,sk, gold, item, quantity)
values ("SID#blue-montain", "ITEMS#STONES#RUBY", 1000,"Ruby", 2);
```

Let’s identify how to work with the sort key conditions, by using the where clause.

```shell
insert into twitch-games (pk, sk, user_id, item, status, usability, damage, type, reach)
values ("UID#tebanieo", "INVENTORY#BAG#WEAPON#SWORD#BRONZE SWORD", "tebanieo", "Bronze Sword", "BROKEN", 0, "10", "Sword", 30),
("UID#tebanieo", "INVENTORY#BAG#WEAPON#SWORD#SILVER SWORD", "tebanieo", "Silver Sword", "BAG", 80, "30-40", "Sword", 60),
("UID#tebanieo", "INVENTORY#BAG#WEAPON#SPEAR#WINTER TRIDENT", "tebanieo", "Winter Trident", "BAG", 60, "40-50", "Spear", 80),
("UID#tebanieo", "INVENTORY#BAG#WEAPON#MAZE#NAIL BAT", "tebanieo", "Nail Bat", "BAG", 30, "25-35", "Maze", 40),
("UID#tebanieo", "INVENTORY#ACTIVE#HELMET#LIGHT BOX", "tebanieo", "Light Box", "BAG", 40, "0", "Helmet", 1);

insert into twitch-games (pk, sk, user_id, item, status, usability, power, bonus)
values ("UID#tebanieo", "INVENTORY#ACTIVE#RINGS#R1", "tebanieo", "Emerald Forest Ring", "BAG", 100, 100, "Strenght +5"),
("UID#tebanieo", "INVENTORY#ACTIVE#RINGS#R2", "tebanieo", "Amber Fire Ring", "BAG", 100, 100, "Strenght +10"),
("UID#tebanieo", "INVENTORY#ACTIVE#RINGS#R3", "tebanieo", "Opal Agelical Ring", "BAG", 100, 100, "Health +5"),
("UID#tebanieo", "INVENTORY#ACTIVE#RINGS#R4", "tebanieo", "Golden Ring", "BAG", 100, 100, "Stamina +4"),
("UID#tebanieo", "INVENTORY#ACTIVE#RINGS#R5", "tebanieo", "Silver Ring Ring", "BAG", 100, 100, "Stamina +1"),
("UID#tebanieo", "INVENTORY#ACTIVE#RINGS#R6", "tebanieo", "Ruby Blood Ring", "BAG", 100, 100, "Damage +25");
```

We can now run a query

```shell
explain select * from twitch-games where pk = "UID#tebanieo" and begins_with(sk, "INVENTORY#ACTIVE#") and CONTAINS(item, "Golden");
```

```shell
select * from twitch-games where pk = "UID#tebanieo" and sk BETWEEN "INVENTORY#ACTIVE#RINGS#R3" and "INVENTORY#ACTIVE#RINGS#R5";
```

Now let’s think about it, what happens when a player needs to heal himself? they would need to buy the potion, heal and then reduce the amount of coins from their inventory, if any of the previous elements above fail, then the operation should be cancelled.

```shell
begin;
update twitch-games set gold = gold - 100 where pk = "UID#tebanieo" and sk = "ASSETS";
update twitch-games set quantity = quantity - 1 where pk = "SID#blue-montain" and sk = "ITEMS#POTIONS#HEALING_NORMAL";
commit;
```

Try to run the explain command on those, explore what happens behind scenes and become an expert on DynamoDB API calls.

I hope this session was useful for all of you, start thinking in terms of the DynamoDB API and build your datamodels to use efficiently all these calls we have seen in this episode, feel free to leave us some feedback and report any issue if you find one.

Thanks!
