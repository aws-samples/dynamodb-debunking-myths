import boto3

client = boto3.client('dynamodb')

response = client.create_table(
    TableName='pk-only',
    AttributeDefinitions=[
        {
            'AttributeName': 'pk',
            'AttributeType': 'S'
        },
    ],    
    KeySchema=[
        {
            'AttributeName': 'pk',
            'KeyType': 'HASH'
        },
    ],
    BillingMode='PAY_PER_REQUEST'
)

print(response)

response = client.create_table(
    TableName='pk-and-sk',
    AttributeDefinitions=[
        {
            'AttributeName': 'pk',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'sk',
            'AttributeType': 'S'
        }
    ],    
    KeySchema=[
        {
            'AttributeName': 'pk',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'sk',
            'KeyType': 'RANGE'
        },        
    ],
    BillingMode='PAY_PER_REQUEST'
)

print(response)
