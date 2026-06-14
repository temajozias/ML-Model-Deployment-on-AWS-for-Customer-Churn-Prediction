### MLOPS AWS

This project demonstrates the end-to-end deployment of a Customer Churn Prediction model on AWS. It automates the lifecycle from model packaging and containerization to deployment and monitoring using CI/CD pipelines.

* Key Objectives

1. Automate the ML model deployment lifecycle with AWS CI/CD services.
2. Containerize the model using Docker and store images in Amazon ECR.
3. Deploy ML services on Amazon ECS (Fargate) with scalable task definitions.
4. Use Application Load Balancer (ALB) to route traffic and enable Blue/Green deployments.
5. Automate builds and tests with AWS CodePipeline & CodeBuild.
6. Integrate Amazon RDS as the database backend for storing and managing data.
7. Apply Terraform to provision AWS resources as code.
8. Ensure best practices for monitoring, scalability, and reproducibility in MLOps.

* Tech Stack


* Language: Python
* Libraries: Flask, gunicorn, lightgbm, scikit-learn, scikit-learn, gunicorn, xgboost
* Tool: Terraform
* Services: Flask, Docker, AWS ECR, AWS CodePipeline, AWS CodeBuild, AWS ECS, AWS RDS, Task Definition, Application Load Balancer



* Getting Started

## Prerequisites

Install Git and Visual Studio Code (or your preferred IDE).

1. Have an AWS account and an IAM user with permissions to create resources (or use an admin account for testing).

2. Recommended: install and configure the AWS CLI (aws configure) so Terraform can access your AWS account.


1) Install Terraform

Official install instructions: https://developer.hashicorp.com/terraform/install

macOS (Homebrew)

# add HashiCorp tap (one-time)
brew tap hashicorp/tap

# install Terraform
brew install hashicorp/tap/terraform

# verify
terraform --version


Windows - https://developer.hashicorp.com/terraform/install (Download exe and setup in Windows)

# OR install via Chocolatey
choco install terraform -y

# verify (Command Prompt)
terraform --version


Note: Make sure terraform --version prints successfully. Terraform will be used to provision every AWS service in this project, so having Terraform installed and on your PATH is mandatory.


2) Get the project code and open in your IDE

Download the project code ZIP from the project Download / Codes section.

Extract the ZIP to a folder on your local system.


# Open the extrcated code folder in VS Code

cd C:\Downloads\Code
code .

3) Ready to provision

Open the Terraform Resources/ folder in your repo.

Edit any required variables (AWS region, credentials - locals.tf) in the Terraform .tf files or terraform.tfvars.

Initialize and apply:

terraform init
terraform plan    # review changes


Important: All AWS resources for this project (ECR, ECS, RDS, ALB, CodePipeline, CodeBuild, networking, etc.) are provisioned and managed via Terraform — avoid manual changes in the AWS Console unless you intend to manage drift.


4) Set Up Python Virtual Environment and Install Dependencies

Open the project code folder in your terminal or IDE.

Create a Python 3.8 virtual environment (Flask application is configured to work with Python 3.8 runtime):

Windows

# Creating Virual environment
py -3.8 -m venv env_3.8

# Activating Virual environment
env_3.8\Scripts\activate


macOS / Linux

# Creating Virual environment
python3.8 -m venv env_3.8

# Activating Virual environment
source env_3.8/bin/activate


#Navigate to the FlaskApplication folder where the requirements.txt is avaialable

cd FlaskApplication
# Install required Python packages:

pip install -r requirements.txt

After this, your environment will be ready to run the Flask application and interact with the ML backend.

Step 1 - provision VPC, subnets, route tables, internet gateway, and security group
terraform apply -target=aws_vpc.main -target=aws_internet_gateway.main -target=aws_subnet.public_1 -target=aws_subnet.public_2 -target=aws_subnet.private_1 -target=aws_subnet.private_2 -target=aws_route_table.public -target=aws_route_table_association.public_1 -target=aws_route_table_association.public_2 -target=aws_security_group.main -auto-approve


4) Create the RDS Database Instance

The RDS database will store raw customer data used by the ML application. All AWS resources are provisioned using Terraform.

Steps:

Open the secrets.tfvars file and specify the username and password you want for your RDS instance:

db_username = "your_db_username"
db_password = "your_secure_password"


Apply the Terraform configuration only for the RDS instance (so you don’t affect other services) by running:

terraform apply -target=aws_db_instance.postgres_instance -var-file="secrets.tfvars" -auto-approve


Note: This command targets only the RDS database. Terraform will not create or modify other AWS resources in the folder.

After successful creation, your RDS instance is ready and can be connected to the Flask application running in ECS.


5) Load Data into the RDS Database Instance

The RDS database needs to have customer raw data loaded before the ML application can process it.

Steps:

Activate your Python 3.8 virtual environment if it’s not already active:

* Windows:

env_3.8\Scripts\activate


* macOS / Linux:

source env_3.8/bin/activate


Navigate to the Flask application source folder:

cd flaskapplication/src


Set up environment variables for connecting to the RDS instance. Use the credentials you specified in secrets.tfvars and put it in the .env:

DB_HOST=<your-rds-endpoint>
DB_NAME=postgres
DB_USER=<username-from-secrets.tfvars>
DB_PASSWORD=<password-from-secrets.tfvars>
DB_PORT=5432


* Save the environment variables (or ensure they are active in your current terminal/session).

* Run the data loading script to populate the RDS instance with customer data:

python RDS_Data_load.py


This script will read the input file input/Churn_Modelling.csv and load the records into the RDS database. Once complete, your RDS instance will have the raw customer data required for churn predictions.


* Make sure the virtual environment env_3.8 is activated before running the script.


6) Execute the Application directly on Local sysytem

Before deploying to AWS, you can test the Flask application locally to ensure it is working correctly with the RDS database.

Steps:

Activate your Python 3.8 virtual environment if it is not already active:

* Windows:

env_3.8\Scripts\activate


* macOS / Linux:

source env_3.8/bin/activate


Navigate to the Flask application source folder:

cd flaskapplication/src


Run the Flask application:

python app.py


This will start the Flask server locally, typically at:

http://127.0.0.1:5000

3a) Test GET Request (Health Check)

Open your browser or use curl to check the health of the API:

curl http://127.0.0.1:5000/health-status


A successful response (status: alive) indicates the Flask API is running correctly.

3b) Test POST Request (Churn Prediction)

Send a POST request to test the churn prediction endpoint:

curl -X POST http://127.0.0.1:5000/churn-prediction


* Explanation:

1. The Flask application will forward the request to the ML backend.
2. The backend will fetch raw customer data from the RDS database.
3. The churn prediction results for the requested customers will be returned in the response, showing which customers are likely to churn.



7) Test the Containerized Application Locally

After verifying the Flask application runs correctly locally, you can test it as a Docker container.

7a) Install Docker Desktop

Make sure Docker Desktop is installed on your system:

Windows: https://docs.docker.com/desktop/setup/install/windows-install/

macOS: https://docs.docker.com/desktop/setup/install/mac-install/


After installation, ensure Docker Desktop is running before proceeding. Always open the Docker Desktop application in the local system when working with Docker in the local system.

7b) Build the Docker Image

Open a terminal and navigate to the project code folder (not the Flask application folder).

Build the Docker image using the Dockerfile located in the project root:

docker build -t churn_image .


-t churn_image tags the image as churn_image.

The . ensures Docker uses the Dockerfile in the current directory.

7c) Run the Container

Run the container locally and map port 5000:

docker run -it -p 5000:5000 churn_image


The Flask API will now be accessible at http://localhost:5000.

7d) Test the Churn Prediction Endpoint

Use curl (or Postman) to send a POST request:

curl -X POST http://localhost:5000/churn-prediction


The containerized application will fetch raw customer data from the RDS database, process it with the ML backend, and return churn predictions.



8) Push Code to GitHub and Prepare for Deployment

Once the application has been tested locally (both directly and as a container), push the project code to your GitHub repository for version control and integration with AWS CodePipeline.

8a) Remove Local Virtual Environment folder from the code folder

Before pushing, delete the local Python virtual environment to avoid committing it:


8b) Modify app.py for Deployment

Open app.py inside flaskapplication/src.

Comment out the line that loads .env files:


# Commented out for ECS deployment

#from dotenv import load_dotenv
from flask import Flask, jsonify, request
#load_dotenv(Path(".env"))  

#if os.environ.get("ENV", "dev") == "prod":
    #load_dotenv(Path(".env.prod"))
#if os.environ.get("ENV", "dev") == "dev":
    #load_dotenv(Path(".env.dev"))


The Flask application will now use environment variables provided via ECS task definitions for database credentials instead of relying on a local .env file.

8c) Push Project to GitHub

Initialize a Git repository (if not already done):

# 1. Initialize a local Git repository
git init

# 2. Add GitHub remote repository
git remote add origin <repository-url>

# 3. switch to a new branch called 'master'
git checkout -b master

# 4. Stage all files for commit
git add .

# 5. Commit the staged files with a message
git commit -m "initial commit"

# 6. Push the branch 'master' to GitHub and set upstream
git push -u origin master


The project is now version-controlled on GitHub and ready to be linked to AWS CodePipeline for automated CI/CD.


9) Configure GitHub Access for AWS CodePipeline

To enable AWS CodePipeline to pull the project code from GitHub, you need to create a GitHub Personal Access Token (PAT) and provide it to Terraform.

9a) Generate a GitHub Personal Access Token

Go to GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
.

* Click Generate new token and select the following scopes:

repo (full control of private repositories if your repo is private)

Copy the generated token — you will use it in the Terraform secrets file.

9b) Add the GitHub PAT to Terraform Secrets

Open secrets.tfvars and add the token:

github_pat = "<your-github-personal-access-token>"



10) Provision AWS Resources Using Terraform

After configuring your environment and GitHub connection, start the provisioning of AWS resources one by one using Terraform. This ensures controlled creation and easier debugging.

* Run all commands from the Terraform resources folder (not the Flask application folder).

cd ..

cd Terraform Resources

10a) Create the ECR Repository
terraform apply -target=aws_ecr_repository.churn_repo -var-file="secrets.tfvars" -auto-approve


10b) Create the CodeBuild Project
terraform apply -target=aws_codebuild_project.topic_codebuild -var-file="secrets.tfvars" -auto-approve

This command will attach the policies to the role
terraform apply -target=aws_iam_role_policy_attachment.ecr_access -target=aws_iam_role_policy_attachment.secrets_manager_access -target=aws_iam_role_policy_attachment.cloudwatch_logs_full_access -target=aws_iam_role_policy_attachment.codebuild_basic_policy -target=aws_iam_role_policy.codebuild_s3_full_access -var-file="secrets.tfvars" -auto-approve

* Note: After Terraform creates the CodeBuild project, verify the service role in the AWS console.

Attach any missing policies manually if needed to ensure CodeBuild can fully build, test, and push Docker images and artifacts.

* Attach the policies for the CodeBuild service role include:

1. AmazonS3FullAccess – to access S3 buckets for source and artifacts
2. AmazonEC2ContainerRegistryPowerUser – to push/pull Docker images from ECR
3. SecretsManagerReadWrite – to access secrets from AWS Secrets Manager
4. CloudWatchLogsFullAccess – to create and write logs for monitoring
5. CloudWatchLogsAccess – for reading CloudWatch logs

If the CodeBuild service role does not have these policies, the build may fail or have limited access.



10c) Create Load Balancer Resources
terraform apply \
  -target=aws_lb_target_group.churn_target_group \
  -target=aws_lb.churn_load_balancer \
  -target=aws_lb_listener.churn_connection \
  -auto-approve

or

terraform apply -target=aws_lb_target_group.churn_target_group -target=aws_lb.churn_load_balancer -target=aws_lb_listener.churn_connection -auto-approve

10d) Create the ECS Cluster
terraform apply -target=aws_ecs_cluster.churn_cluster -auto-approve


10e) Create CloudWatch Log Group
terraform apply -target=aws_cloudwatch_log_group.churn_app -auto-approve


10f) Create ECS Task Definition
terraform apply -target=aws_ecs_task_definition.churn_definition -auto-approve


10g) Create ECS Service
terraform apply -target=aws_ecs_service.churn_service -auto-approve



Authorize Codestar connection
terraform apply -target=aws_codestarconnections_connection.github -auto-approve

    Authorize the codestart connection manually using aws console
    Go to:

    1. AWS Console → search for CodePipeline in the search bar

    2. On the left sidebar → Settings → Connections

    3. You should see github-connection with status Pending

    Or go directly to:

    AWS Console → search Developer Tools → Settings → Connections



10h) Final Step: Create CodePipeline


terraform apply -target=aws_codepipeline.churn_pipeline -target=aws_cloudwatch_event_rule.codepipeline_trigger -target=aws_cloudwatch_event_target.codepipeline_target -var-file="secrets.tfvars" -auto-approve




Once all these steps are complete, CI/CD pipeline will be fully set up. Whenever code is pushed to GitHub, CodePipeline will automatically build, test, and deploy the updated version ML application to ECS 



11) Test the Containerized Application on AWS ECS

Once ECS service is running and the load balancer is set up, test the Flask application directly through the Application Load Balancer (ALB).


11a) Get the Load Balancer DNS Name

Open the AWS Management Console → EC2 → Load Balancers.
Locate the ALB you created (e.g., churn-load-balancer).
Copy the DNS name of the load balancer.


11b) Test GET Request (Health Check)

Use curl or your browser to verify the application is running:

curl -X GET http://[load-balancer-dns]/health-status


A successful response (e.g., status: alive) confirms that the ECS containers are healthy and accessible.


11c) Test POST Request (Churn Prediction)

Send a POST request to the churn prediction endpoint:

curl -X POST http://[load-balancer-dns]/churn-prediction


* What happens:

1. he request is routed by the ALB to one of the ECS containers.

2. The container fetches raw customer data from the RDS instance.

3. The ML backend processes the data and returns churn predictions for the specified customers.
curl -X POST http://churn-load-balancer-1504372420.us-east-1.elb.amazonaws.com/churn-prediction 




