import boto3

def create_ecs_cluster(client, cluster_name):
    response = client.create_cluster(
        clusterName=cluster_name
    )
    return response
def create_ecs_service(client, cluster_name, service_name, task_definition, subnet_ids, security_group_ids):
    response = client.create_service(
        cluster=cluster_name,
        serviceName=service_name,
        taskDefinition=task_definition,
        desiredCount=1,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': subnet_ids,
                'securityGroups': security_group_ids,
                'assignPublicIp': 'ENABLED'
            }
        },
        deploymentConfiguration={
            'maximumPercent': 200,
            'minimumHealthyPercent': 100
        }
    )
    return response
#This function is to check when the service becomes stable
def wait_for_service_stability(client, cluster_name, service_name):
    waiter = client.get_waiter('services_stable')
    waiter.wait(cluster=cluster_name, services=[service_name])

ecs_client = boto3.client('ecs')

student_id = "24181422"
ECR_image_uri = '489389878001.dkr.ecr.ap-south-1.amazonaws.com/24181422_ecr_repo'

cluster_name = student_id + '-cluster'
create_ecs_cluster(ecs_client, cluster_name)

service_name = student_id + '-service'
task_definition = 'arn:aws:ecs:ap-south-1:489389878001:task-definition/24181422-task-family:1'
subnet_id_1= 'subnet-02b66cd3edeaad811'
subnet_id_2= 'subnet-037f3093c4bcd84d5'
subnet_id_3= 'subnet-0350ec28e25be6ff9'

subnet_ids = [subnet_id_1, subnet_id_2, subnet_id_3]
security_group_ids = ['sg-05fa4619d288aaaf2']

ecs_client = boto3.client('ecs')

service_response = create_ecs_service(ecs_client, cluster_name, service_name, task_definition, subnet_ids, security_group_ids)
print(f'ECS Service created: {service_response["service"]["serviceArn"]}')

print(f'Waiting for service {service_name} to become stable...')
wait_for_service_stability(ecs_client, cluster_name, service_name)
print(f'Service {service_name} is now stable.')


