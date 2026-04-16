
import boto3 as bt
import os

#configuration
STUDENT_ID   = "24181422"       
AMI_ID       = "ami-0f918f7e67a3323f0"            
INSTANCE_TYPE = "t3.micro"

# Names distinct from awscli run
GroupName    = f"{STUDENT_ID}-sg-lab2"
KeyName      = f"{STUDENT_ID}-key-lab2"
InstanceName = f"{STUDENT_ID}-vm2"

ec2 = bt.client("ec2")

# 1. Create security group
step1_response = ec2.create_security_group(
    Description="security group for development environment",
    GroupName=GroupName
)
sg_id = step1_response["GroupId"]
print("[1] Security Group:", GroupName, sg_id)

# 2. Authorise inbound traffic for ssh
try:
    step2_response = ec2.authorize_security_group_ingress(
        GroupName=GroupName,
        IpPermissions=[{
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
        }]
    )
    print("[2] Ingress added for tcp/22 from 0.0.0.0/0")
except Exception as e:
    print("[2] Note:", e)

# 3. Create a key pair
kp = ec2.create_key_pair(KeyName=KeyName)
key_material = kp["KeyMaterial"]
ssh_dir = os.path.expanduser("~/.ssh")
os.makedirs(ssh_dir, exist_ok=True)
pem_path = os.path.join(ssh_dir, f"{KeyName}.pem")
with open(pem_path, "w") as f:
    f.write(key_material)
os.chmod(pem_path, 0o400)
print("[3] Key Pair:", KeyName, "saved to", pem_path, "(chmod 400)")

# 4. Create the instance
step4_response = ec2.run_instances(
    ImageId=AMI_ID,
    InstanceType=INSTANCE_TYPE,
    MinCount=1,
    MaxCount=1,
    KeyName=KeyName,
    SecurityGroupIds=[GroupName],
)
instance_id = step4_response["Instances"][0]["InstanceId"]
print("[4] Instance launched:", instance_id)

# Wait until running (helps ensure Public IP is assigned)
ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])
print("ec2 instance is 'running'.")

# 5. Add a tag to your Instance
ec2.create_tags(
    Resources=[instance_id],
    Tags=[{"Key": "Name", "Value": InstanceName}]
)
print("[5] Tag applied: Name =", InstanceName)

# 6. Get the public IP address
desc = ec2.describe_instances(InstanceIds=[instance_id])
inst = desc["Reservations"][0]["Instances"][0]
public_ip = inst.get("PublicIpAddress")
print("[6] Public IP:", public_ip)



