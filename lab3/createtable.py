import boto3

def create_db_table():
    try:
        # Initialize DynamoDB service instance
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        
        table = dynamodb.create_table(
            TableName='CloudFiles',
            KeySchema=[
                {
                    'AttributeName': 'userId',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'fileName',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'  # String type
                },
                {
                    'AttributeName': 'fileName',
                    'AttributeType': 'S'  # String type
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        print("Table status:", table.table_status)
        print("Table created successfully!")
        return table
        
    except Exception as e:
        print(f"Error creating table: {e}")
        return None

if __name__ == '__main__':
    create_db_table()