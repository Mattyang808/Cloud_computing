import boto3
import os

REGION = "ap-south-1"         
AMI_ID = "ami-0f918f7e67a3323f0"  
KEY_NAME = "24181422-key-lab7"
SG_NAME = "24181422-sg-lab7"

ec2 = boto3.client("ec2", region_name=REGION)

# 1) Key pair
kp = ec2.create_key_pair(KeyName=KEY_NAME)
with open(f"{KEY_NAME}.pem", "w") as f:
    f.write(kp["KeyMaterial"])
os.chmod(f"{KEY_NAME}.pem", 0o400)

# 2) Security group (allows SSH 22 and HTTP 80 from anywhere for the lab)
sg_id = ec2.create_security_group(GroupName=SG_NAME, Description="Lab7 SG")["GroupId"]
ec2.authorize_security_group_ingress(
    GroupId=sg_id,
    IpPermissions=[
        {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22,
         "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
        {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80,
         "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
    ],
)

# 3) Launch instance
run = ec2.run_instances(
    ImageId=AMI_ID,
    InstanceType="t3.micro",
    KeyName=KEY_NAME,
    SecurityGroupIds=[sg_id],
    MinCount=1, MaxCount=1,
    TagSpecifications=[{
        "ResourceType": "instance",
        "Tags": [{"Key": "Name", "Value": "24181422-vm"}]
    }],
)
instance_id = run["Instances"][0]["InstanceId"]

# 4) Wait for running & print public IP
ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])
desc = ec2.describe_instances(InstanceIds=[instance_id])
ip = desc["Reservations"][0]["Instances"][0]["PublicIpAddress"]

print("INSTANCE_ID:", instance_id)
print("PUBLIC_IP:", ip)