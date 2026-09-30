1. Go to: https://dagshub.com/dashboard
2. Create > New Repo > Connect a repo > (Github) Connect > Select your repo > Connect
3. Copy experiment tracking url and code snippet. (Also try: Go To MLFlow UI)
4. pip install dagshub & mlflow
5. Run the exp notebooks
6. dvc init
7. create a local folder as "local_s3" (temporary work)
8. on terminal - "dvc remote add -d mylocal local_s3"
9. add file - dvc.yaml, params.yaml
10. DVC pipeline is ready to run - dvc repro
11. Set aws credentials - aws configure in terminal
12. Need to add S3 as remote storage - Create IAM User(keep cred) and S3 bucket
13. pip install - dvc[s3] & awscli
14. Add s3 as dvc remote storage - dvc remote add -d myremote s3://<bucket-name>
15. dvc commit, dvc push
16. pip install flask and run the app (dvc push - to push data to S3)
17. Add .github/workflows/ci.yaml file
18. Failed for authorization through dagshub
18. Create key token on Dagshub for auth: Go to dagshub profile > Your settings > Tokens > Generate new token. 
Add this auth token to github secret&var and update on ci file
    >> Save token capstone_test: ______________________________________________
19. Add dockerfile and start docker-desktop in background
20. "docker build -t capstone-app:latest ."
21. docker run -p 8888:5000 -e CAPSTONE_TEST=e8685db6a0244e698c28141e41b23a18dcac879c capstone-app:latest
22. docker push youruser/capstone-app:latest . 

---
> Kubernetes on aws

1. Setup aws services for below secrets and variables: **aws configure**
	AWS_ACCESS_KEY_ID
	AWS_SECRET_ACCESS_KEY
	AWS_REGION
	ECR_REPOSITORY (capstone-proj)
    AWS_ACCOUNT_ID
   (IAM user: AmazonEC2ContainerRegistryFullAccess, Administratoraccess)
2. pip uninstall awscli
3. aws --version
4. Download kubectl: **Invoke-WebRequest -Uri "https://dl.k8s.io/release/v1.28.2/bin/windows/amd64/kubectl.exe" -OutFile "kubectl.exe"**
> Test if kubectl is properly installed: kubectl version --client

5. Download eksctl: **Invoke-WebRequest -Uri "https://github.com/weaveworks/eksctl/releases/download/v0.158.0/eksctl_Windows_amd64.zip" -OutFile "eksctl.zip"**
6. Extract eksctl: **Expand-Archive -Path .\eksctl.zip -DestinationPath .**
* Move the extracted eksctl.exe file to C:\Windows\System32 or any folder in your system PATH: Move-Item -Path .\eksctl.exe -Destination 
> Verify eksctl: eksctl version
7. Create an EKS cluster:
    **eksctl create cluster --name flask-app-cluster --region us-east-1 --nodegroup-name flask-app-nodes --node-type t3.small --nodes 1 --nodes-min 1 --nodes-max 1 --managed**
8. **aws eks --region us-east-1 update-kubeconfig --name flask-app-cluster** (This ensures your kubectl is pointing to the correct cluster.)
9. Check EKS Cluster Configuration Ensure you can access your EKS cluster by running
    **aws eks list-clusters**
10. Delete cluster(optional):
    **eksctl delete cluster --name flask-app-cluster --region us-east-1**

    Also, verify cluster deletion:
    **eksctl get cluster --region us-east-1**
11. Verify the cluster status:
    **aws eks --region us-east-1 describe-cluster --name flask-app-cluster --query "cluster.status"**
12. Check cluster connectivity:
	**kubectl get nodes**
13. Deploy the app on EKS via CICD pipeline
  > edit the security group for nodes and edit inbound rule for 5000 port
14. . Verify the deployment:
	**kubectl get pods**
	**kubectl get svc**
15. Once the LoadBalancer service is up, get the external IP:
	**kubectl get svc flask-app-service**

use this for testing
curl -X POST http://a197c873571754cc997354e4f9d7ef69-1339969836.us-east-1.elb.amazonaws.com:5000/predict -d "text=this is absolutely terrible and awful"

curl -X POST http://a197c873571754cc997354e4f9d7ef69-1339969836.us-east-1.elb.amazonaws.com:5000/predict -d "text=this is amazing and wonderful I love it"

---
Prometheus Server Setup
1. Launch an Ubuntu EC2 Instance for Prometheus: t3.medium,  20GB of disk space (general-purpose SSD), Security Group: Allow inbound access on ports: 9090 for Prometheus Web UI, 22 for SSH access

Connect and paste these on the terminal
2. Update packages: sudo apt update && sudo apt upgrade -y
3. wget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz 
4. tar -xvzf prometheus-2.46.0.linux-amd64.tar.gz
5. mv prometheus-2.46.0.linux-amd64 prometheus
6. sudo mv prometheus /etc/prometheus
7. sudo mv /etc/prometheus/prometheus /usr/local/bin/
8. Open the file for editing: sudo nano /etc/prometheus/prometheus.yml
> edit the File:

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "flask-app"
    static_configs:
      - targets: ["a197c873571754cc997354e4f9d7ef69-1339969836.us-east-1.elb.amazonaws.com:5000"]  # Replace with your app's External IP

9. Save the File: ctrl+o -> enter -> ctrl+x
10. Verify the Changes: **cat /etc/prometheus/prometheus.yml**
11. **which prometheus**
12. **/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml**

---
Grafana Server Setup

1. Launch an Ubuntu EC2 Instance for Grafana: t3.medium,  20GB of disk space (general-purpose SSD), Security Group: Allow inbound access on ports: 3000 for Grafana Web UI, 22 for SSH access

2. sudo apt update && sudo apt upgrade -y
3. Download Grafana: **wget https://dl.grafana.com/oss/release/grafana_10.1.5_amd64.deb**
4. Install Grafana: **sudo apt install ./grafana_10.1.5_amd64.deb -y**
5. Start the Grafana service: **sudo systemctl start grafana-server**
6. Enable Grafana to start on boot: **sudo systemctl enable grafana-server**
7. Verify the service is running: **sudo systemctl status grafana-server**
8. Open Grafana web UI: **http://<ec2-public-ip>:3000 (username/pass - admin)**
9. Add Prometheus as a Data Source: **http://54.81.71.206/:9090**
    click - Save and Test | Get started with building dashboards.


---
**How Is CloudFormation Related to EKS?**

AWS CloudFormation is a service that helps define and provision AWS infrastructure as code using templates. It automates the process of creating and managing AWS resources.

When you run eksctl, it generates CloudFormation templates behind the scenes to create:
1. The EKS control plane.
2. Node groups.
CloudFormation ensures that these resources are created and managed as a stack (a logical grouping of resources).

A CloudFormation Stack is a collection of AWS resources (like VPCs, subnets, EC2 instances, etc.) managed as a single unit. For EKS:
1. eksctl-flask-app-cluster-cluster stack: Creates the EKS control plane.
2. eksctl-flask-app-cluster-nodegroup-flask-app-nodes stack: Creates the worker nodes.

Each stack contains:
1. A template defining the resources (YAML or JSON).
2. Resource dependencies and configurations.

---
**Fleet Requests**
A Fleet Request is an AWS internal process for provisioning EC2 instances. When creating a NodeGroup, EKS uses an Auto Scaling Group (ASG) to request EC2 instances, which count as Fleet Requests.

WAWS imposes a limit on the number of Fleet Requests per account. If your account exceeds this limit (e.g., due to other active ASGs or EKS clusters), NodeGroup creation fails with the error "You’ve reached your quota for maximum Fleet Requests".

---
**What is a PVC?**
1. PVC (PersistentVolumeClaim) is a request for storage by a Kubernetes application. It is bound to a PV (PersistentVolume), which is the actual storage resource.
2. PVCs use StorageClasses to define how the volume should be provisioned (e.g., EBS volumes on AWS, NFS, etc.).
3. When a pod is deployed and needs storage, it will request the storage defined in the PVC.
