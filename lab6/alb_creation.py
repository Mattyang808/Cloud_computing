import boto3
from botocore.exceptions import ClientError

REGION = "ap-south-1"
INSTANCE_ID = "i-02ba8f0f30eec2969"

TG_NAME  = "24181422-tg-lab6"
ALB_NAME = "24181422-alb-lab6"           

ec2   = boto3.client("ec2",   region_name=REGION)
elbv2 = boto3.client("elbv2", region_name=REGION)

# 1) Instance details
inst    = ec2.describe_instances(InstanceIds=[INSTANCE_ID])["Reservations"][0]["Instances"][0]
vpc_id  = inst["VpcId"]
inst_az = inst["Placement"]["AvailabilityZone"]
inst_sg_ids = [sg["GroupId"] for sg in inst["SecurityGroups"]]

# 2) Pick subnets: one in instance AZ + one in a different AZ (both PUBLIC)
subs = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]
public = [s for s in subs if s.get("MapPublicIpOnLaunch")]
subnet_in_inst_az = next((s["SubnetId"] for s in public if s["AvailabilityZone"] == inst_az), None)
subnet_in_other_az = next((s["SubnetId"] for s in public if s["AvailabilityZone"] != inst_az), None)
if not subnet_in_inst_az or not subnet_in_other_az:
    raise RuntimeError("Need two PUBLIC subnets: one in the instance AZ and one in another AZ.")
subnet_ids = [subnet_in_inst_az, subnet_in_other_az]

# 3) Get-or-create ALB SG
alb_sg_name = f"{ALB_NAME}-sg"
resp = ec2.describe_security_groups(
    Filters=[{"Name": "group-name", "Values": [alb_sg_name]},
             {"Name": "vpc-id", "Values": [vpc_id]}]
)
if resp["SecurityGroups"]:
    alb_sg_id = resp["SecurityGroups"][0]["GroupId"]
else:
    alb_sg_id = ec2.create_security_group(
        GroupName=alb_sg_name, Description="ALB SG allowing HTTP 80", VpcId=vpc_id
    )["GroupId"]

# Ensure inbound 80 on ALB SG (ignore duplicates)
try:
    ec2.authorize_security_group_ingress(
        GroupId=alb_sg_id,
        IpPermissions=[{
            "IpProtocol": "tcp", "FromPort": 80, "ToPort": 80,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }]
    )
except ClientError as e:
    if "InvalidPermission.Duplicate" not in str(e):
        raise

#allow ALB -> instance on 80 (ignore duplicates)
for sg_id in inst_sg_ids:
    try:
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[{
                "IpProtocol": "tcp", "FromPort": 80, "ToPort": 80,
                "UserIdGroupPairs": [{"GroupId": alb_sg_id}],
            }]
        )
    except ClientError as e:
        if "InvalidPermission.Duplicate" not in str(e):
            raise

# 4) Target Group (HTTP:80, /polls/, 30s)
tg_arn = elbv2.create_target_group(
    Name=TG_NAME, Protocol="HTTP", Port=80, VpcId=vpc_id, TargetType="instance",
    HealthCheckProtocol="HTTP", HealthCheckPort="80",
    HealthCheckPath="/polls/", HealthCheckIntervalSeconds=30,
)["TargetGroups"][0]["TargetGroupArn"]

elbv2.register_targets(TargetGroupArn=tg_arn, Targets=[{"Id": INSTANCE_ID}])

# 5) ALB (internet-facing) in the two chosen subnets
lb = elbv2.create_load_balancer(
    Name=ALB_NAME, Type="application", Scheme="internet-facing", IpAddressType="ipv4",
    Subnets=subnet_ids, SecurityGroups=[alb_sg_id],
)["LoadBalancers"][0]
lb_arn = lb["LoadBalancerArn"]; lb_dns = lb["DNSName"]

# 6) Listener HTTP:80 → TG
elbv2.create_listener(
    LoadBalancerArn=lb_arn, Protocol="HTTP", Port=80,
    DefaultActions=[{"Type": "forward", "TargetGroupArn": tg_arn}],
)

print("ALB_SG_ID:", alb_sg_id)
print("TG_ARN   :", tg_arn)
print("ALB_ARN  :", lb_arn)
print("ALB_DNS  :", lb_dns)
print(f"Test: http://{lb_dns}/polls/")

