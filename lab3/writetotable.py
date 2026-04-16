import boto3
from datetime import datetime

def populate_table_with_s3_files():
    try:
        # Initialize clients
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        s3 = boto3.client('s3', region_name='ap-south-1')
        
        # Get the table
        table = dynamodb.Table('CloudFiles')
        
        ROOT_S3_DIR = '24181422-cloudstorage'
        USER_ID = '24181422'  
        
        # List all objects in S3 bucket
        response = s3.list_objects_v2(Bucket=ROOT_S3_DIR)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                s3_key = obj['Key']
                print(f"Processing file: {s3_key}")
                
                try:
                    # Get object metadata
                    obj_response = s3.head_object(Bucket=ROOT_S3_DIR, Key=s3_key)
                    
                    # Get object ACL for owner and permissions
                    acl_response = s3.get_object_acl(Bucket=ROOT_S3_DIR, Key=s3_key)
                    
                    # Extract owner ID
                    owner_id = acl_response['Owner']['ID']
                    
                    # Extract permissions
                    permissions = []
                    for grant in acl_response['Grants']:
                        grantee = grant['Grantee']
                        permission = grant['Permission']
                        if grantee['Type'] == 'CanonicalUser':
                            permissions.append(f"{grantee['ID']}: {permission}")
                        else:
                            permissions.append(f"{grantee['Type']}: {permission}")
                    
                    # Determine file path
                    if '/' in s3_key:
                        file_path = '/'.join(s3_key.split('/')[:-1]) + '/'
                    else:
                        file_path = '/'  # Root directory
                    
                    # Extract just the filename
                    file_name = s3_key.split('/')[-1]
                    
                    # Prepare item for DynamoDB
                    item = {
                        'userId': USER_ID,
                        'fileName': file_name,
                        'path': file_path,
                        'lastUpdated': obj_response['LastModified'].isoformat(),
                        'owner': owner_id,  # Using owner ID as requested
                        'permissions': ', '.join(permissions)
                    }
                    
                    # Insert item into DynamoDB
                    table.put_item(Item=item)
                    print(f"Added {file_name} to DynamoDB table")
                    
                except Exception as file_error:
                    print(f"Error processing file {s3_key}: {file_error}")
        else:
            print("No objects found in S3 bucket")
        
        # Display table contents
        print("\nDynamoDB table contents:")
        print("-" * 80)
        scan_response = table.scan()
        for item in scan_response['Items']:
            print(f"UserId: {item['userId']}")
            print(f"FileName: {item['fileName']}")
            print(f"Path: {item['path']}")
            print(f"LastUpdated: {item['lastUpdated']}")
            print(f"Owner: {item['owner']}")
            print(f"Permissions: {item['permissions']}")
            print("-" * 40)
            
    except Exception as e:
        print(f"Error populating table: {e}")

if __name__ == '__main__':
    populate_table_with_s3_files()