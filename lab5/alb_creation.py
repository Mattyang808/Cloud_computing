import boto3

REGION = "ap-south-1"
STUDENT_NUMBER = "24181422"         
VPC_ID = "vpc-08959750bf9a18836"                 
SUBNET_IDS = ["subnet-0d14a9142af92073e", "subnet-08f367a3bb7eb8497"]  
SECURITY_GROUP_ID = "sg-0b3c70b30e2fa8717"        
INSTANCE_IDS = ["i-0ab08fd096891fc79", "i-088465e88cdb29d20"]    

elb = boto3.client("elbv2", region_name=REGION)

# Target Group
tg_name = f"{STUDENT_NUMBER}-tg"
tg = elb.create_target_group(
    Name=tg_name,
    Protocol="HTTP",
    Port=80,
    VpcId=VPC_ID,
    TargetType="instance",
    HealthCheckProtocol="HTTP",
    HealthCheckPort="80",
    HealthCheckPath="/"
)["TargetGroups"][0]
tg_arn = tg["TargetGroupArn"]
print(f"Created target group: {tg_arn}")

# Register targets
elb.register_targets(
    TargetGroupArn=tg_arn,
    Targets=[{"Id": i} for i in INSTANCE_IDS]
)
print("Registered instances in target group.")

# ALB
lb_name = f"{STUDENT_NUMBER}-alb"
lb = elb.create_load_balancer(
    Name=lb_name,
    Subnets=SUBNET_IDS,
    SecurityGroups=[SECURITY_GROUP_ID],
    Scheme="internet-facing",
    Type="application",
    IpAddressType="ipv4",
)["LoadBalancers"][0]
lb_arn = lb["LoadBalancerArn"]
lb_dns = lb["DNSName"]
print(f"Created ALB: {lb_arn}")
print(f"ALB DNS: http://{lb_dns}")

# Wait until ALB active
elb.get_waiter("load_balancer_available").wait(LoadBalancerArns=[lb_arn])

# Listener 80 -> TG
listener = elb.create_listener(
    LoadBalancerArn=lb_arn,
    Protocol="HTTP",
    Port=80,
    DefaultActions=[{"Type": "forward", "TargetGroupArn": tg_arn}]
)["Listeners"][0]
print(f"Created listener: {listener['ListenerArn']}")

print("\n=== PART 2 OUTPUT ===")
print(f"TARGET_GROUP_ARN: {tg_arn}")
print(f"ALB_ARN: {lb_arn}")
print(f"ALB_DNS: http://{lb_dns}")
