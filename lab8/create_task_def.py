import boto3

def create_ecs_task_definition(
    client, image_uri, account_id, task_role_name, execution_role_name, student_id,
    environment_dict=None,port=8888, cpu='256', memory='512'
):
    task_role_arn = f'arn:aws:iam::{account_id}:role/{task_role_name}'
    execution_role_arn = f'arn:aws:iam::{account_id}:role/{execution_role_name}'

    env_list = [{'name': k, 'value': v} for k, v in (environment_dict or {}).items()]
    
    response = client.register_task_definition(
        runtimePlatform={           
            'cpuArchitecture': 'ARM64',
            'operatingSystemFamily': 'LINUX'
        },
        family=f'{student_id}-task-family',
        networkMode='awsvpc',
        requiresCompatibilities=['FARGATE'],
        cpu=cpu,
        memory=memory,
        taskRoleArn=task_role_arn,
        executionRoleArn=execution_role_arn,
        containerDefinitions=[
            {
                'name': f'{student_id}-container',
                'image': image_uri,
                'essential': True,
                'portMappings': [
                    {
                        'containerPort': port,
                        'hostPort': port,
                        'protocol': 'tcp'
                    },
                ]
            },
        ],
    )
    return response

account_id = '489389878001'
student_id = "24181422"
task_role_name = 'SageMakerRole'
execution_role_name = 'ecsTaskExecutionRole'
image_uri = '489389878001.dkr.ecr.ap-south-1.amazonaws.com/24181422_ecr_repo'


ecs_client = boto3.client('ecs')

task_definition = create_ecs_task_definition(
    ecs_client,
    image_uri,
    account_id,
    task_role_name,
    execution_role_name,
    student_id,
    port=8888                      
)
print("Task Definition ARN:", task_definition['taskDefinition']['taskDefinitionArn'])


