# Cloud_computing Labs

## Cloud Infrastructure & Orchestration

- AWS Infrastructure as Code (IaC): Provisioned and managed scalable cloud environments—including EC2 instances, Security Groups, Key Pairs, and Subnets across multiple Availability Zones—using the AWS CLI and Python Boto3 SDK.
- High Availability & Load Balancing: Configured Application Load Balancers (ALB), listeners, and Target Groups to securely distribute HTTP traffic across multiple EC2 instances.
- Containerization & Serverless Computing: Built custom Docker images using Dockerfiles and managed registries via Amazon Elastic Container Registry (ECR). Deployed and orchestrated serverless container workloads on Amazon ECS using AWS Fargate.

## Web Development & CI/CD Automation

- Web Server Deployment: Developed and deployed Django web applications within isolated Python virtual environments, configuring Nginx as a reverse proxy to route traffic to the application server.
- Deployment Automation: Automated EC2 server provisioning, package installation, system configurations, and Django deployments using Python Fabric tasks (fabfile.py) and SSH protocols.
- Linux Administration: Administered Ubuntu Linux environments via WSL, utilizing Bash scripting, permission management (chmod), and package managers (apt).

## Database & Cloud Storage Management

- NoSQL Database Administration: Designed Amazon DynamoDB schemas utilizing Partition and Sort keys. Executed data ingestion, table scans, and automated batch-write operations to migrate data from local instances to AWS DynamoDB.
- S3 Storage Automation: Wrote Python scripts to recursively traverse local directories, automate file uploads/downloads to Amazon S3, mirror local folder structures in the cloud, and retrieve Access Control Lists (ACLs).

## Security & Cryptography

- Access Control Policies: Enforced robust security standards by authoring and attaching JSON-based IAM and Resource policies to restrict unauthorized access to S3 buckets and AWS resources.
- Data Encryption: Secured data-at-rest using AES-256 encryption. Managed symmetric cryptographic keys via AWS Key Management Service (KMS) and implemented local EAX-mode AES encryption/decryption workflows using the pycryptodome library.

## Machine Learning & Artificial Intelligence

- End-to-End MLOps Pipeline: Built machine learning workflows in Amazon SageMaker (via a Dockerized JupyterLab environment), automating S3 data ingestion and model artifact storage.
- Data Engineering: Preprocessed tabular datasets using Pandas and NumPy, performing feature selection, one-hot encoding for categorical variables, and train/validation/test splitting.
- Model Optimization: Programmed and launched automated Bayesian Hyperparameter Tuning Jobs for XGBoost classification models to maximize validation metrics.
- Natural Language Processing (NLP): Integrated Amazon Comprehend via Boto3 to execute dominant language detection, sentiment analysis, named entity recognition, key phrase extraction, and part-of-speech syntax tokenization.

