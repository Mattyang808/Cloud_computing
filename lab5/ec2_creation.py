# filename: ec2_creation.py
import boto3, os, stat


REGION = "ap-south-1"
AMI_ID = "ami-0f918f7e67a3323f0"
INSTANCE_TYPE = "t3.micro"
STUDENT_NUMBER = "24181422"              
KEY_NAME = f"{STUDENT_NUMBER}-key"
SG_NAME = f"{STUDENT_NUMBER}-sg-lab5"
NAME1 = f"{STUDENT_NUMBER}-vm1"
NAME2 = f"{STUDENT_NUMBER}-vm2"


ec2 = boto3.resource("ec2", region_name=REGION)
ec2c = boto3.client("ec2", region_name=REGION)

# 0) Default VPC + 2 subnets in different AZs
vpc = list(ec2.vpcs.filter(Filters=[{"Name": "isDefault", "Values": ["true"]}]))[0]
subs = ec2c.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc.id]}])["Subnets"]
seen = set(); chosen = []
for s in subs:
    az = s["AvailabilityZone"]
    if az not in seen:
        chosen.append(s["SubnetId"]); seen.add(az)
    if len(chosen) == 2: break
assert len(chosen) == 2, "Need two subnets in different AZs"

# 1) Security group (HTTP/80 + SSH/22)
sg = ec2.create_security_group(GroupName=SG_NAME, Description="Allow SSH and HTTP", VpcId=vpc.id)
sg.authorize_ingress(IpPermissions=[
    {"IpProtocol":"tcp","FromPort":22,"ToPort":22,"IpRanges":[{"CidrIp":"0.0.0.0/0"}]},
    {"IpProtocol":"tcp","FromPort":80,"ToPort":80,"IpRanges":[{"CidrIp":"0.0.0.0/0"}]},
])
print(f"Created security group: {sg.id}")

# 2) Key pair (or reuse)
try:
    kp = ec2c.create_key_pair(KeyName=KEY_NAME)
    pem = f"./{KEY_NAME}.pem"
    with open(pem, "w") as f: f.write(kp["KeyMaterial"])
    os.chmod(pem, stat.S_IRUSR | stat.S_IWUSR)
    print(f"Created key pair and saved: {pem}")
except ec2c.exceptions.ClientError as e:
    if "InvalidKeyPair.Duplicate" in str(e):
        print(f"Key pair {KEY_NAME} already exists. Using it.")
    else:
        raise

# 3) Launch instance 1 (subnet A) with Name=vm1
i1 = ec2.create_instances(
    ImageId=AMI_ID, InstanceType=INSTANCE_TYPE, KeyName=KEY_NAME,
    MinCount=1, MaxCount=1,
    NetworkInterfaces=[{
        "AssociatePublicIpAddress": True, "DeviceIndex": 0,
        "SubnetId": chosen[0], "Groups": [sg.id]
    }],
    TagSpecifications=[{
        "ResourceType": "instance",
        "Tags": [{"Key":"Name","Value":NAME1},{"Key":"Owner","Value":STUDENT_NUMBER}]
    }]
)[0]

# 4) Launch instance 2 (subnet B) with Name=vm2
i2 = ec2.create_instances(
    ImageId=AMI_ID, InstanceType=INSTANCE_TYPE, KeyName=KEY_NAME,
    MinCount=1, MaxCount=1,
    NetworkInterfaces=[{
        "AssociatePublicIpAddress": True, "DeviceIndex": 0,
        "SubnetId": chosen[1], "Groups": [sg.id]
    }],
    TagSpecifications=[{
        "ResourceType": "instance",
        "Tags": [{"Key":"Name","Value":NAME2},{"Key":"Owner","Value":STUDENT_NUMBER}]
    }]
)[0]

# 5) Wait and print basics
i1.wait_until_running(); i2.wait_until_running()
ec2c.get_waiter("instance_status_ok").wait(InstanceIds=[i1.id, i2.id])
i1.reload(); i2.reload()

print(f"VPC_ID: {vpc.id}")
print(f"SUBNET_IDS: {chosen}")
print(f"SECURITY_GROUP_ID: {sg.id}")
print(f"INSTANCE_1: {i1.id}  IP: {i1.public_ip_address}  Name: {NAME1}")
print(f"INSTANCE_2: {i2.id}  IP: {i2.public_ip_address}  Name: {NAME2}")
