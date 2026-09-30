## IMDB Sentiment Analysis MLOps Project

This project builds and deploys a sentiment-analysis system for IMDB movie reviews. It demonstrates how a classic machine learning workflow can be turned into a production-ready MLOps pipeline using DVC, MLflow, Docker, Flask, and Kubernetes.

## Key Features

- Text classification pipeline for IMDB movie reviews using a bag-of-words representation and Logistic Regression.
- End-to-end data workflow with ingestion, preprocessing, feature extraction, model training, and evaluation.
- Experiment tracking and model versioning through DagsHub and MLflow so each run is logged with metrics and artifacts.
- Reproducible model lifecycle using DVC to manage pipeline stages and data dependencies.
- Automated model promotion workflow that moves a validated registered model into production.
- Flask-based serving app that loads the production model and vectorizer and exposes prediction endpoints.
- Containerized deployment with Docker and AWS ECR for shipping the serving application.
- Kubernetes deployment on Amazon EKS with a standardized service manifest.
- Monitoring-ready architecture with Prometheus-style metrics exposed from the Flask app.
- CI/CD-ready project setup with GitHub Actions for testing, model promotion, build, and deployment automation.

## What This Project Demonstrates

- Data and model reproducibility
- Experiment lineage and artifact tracking
- Production model registration and promotion
- Model serving through a web application
- Automated container build and deployment
- Cloud-native infrastructure for running the app in production

## Project Architecture

- `src/`: all machine learning logic, including data ingestion, preprocessing, feature engineering, training, evaluation, and model registration.
- `flask_app/`: the production prediction service, HTML frontend, and serving dependencies.
- `tests/`: validation tests for Flask endpoints and model behavior.
- `scripts/promote_model.py`: logic for promoting a tested model to the production stage.
- `dvc.yaml` and `params.yaml`: pipeline definition and model-training parameters.
- `.github/workflows/ci.yaml`: CI/CD automation for validation, promotion, and deployment tasks.
- `deployment.yaml`: Kubernetes deployment configuration for running the app on EKS.

---

## Problems Encountered

- **DagsHub authorization between development and production:** token configuration and access differed across local runs, GitHub Actions, and the deployed container. Use a rotated token in local `.env` and GitHub/Kubernetes secrets; never embed it in an image or commit.
- **`eksctl` downloads and Kubernetes version incompatibility:** an `eksctl` binary for the wrong operating system or a `kubectl` version too far from the EKS control-plane version caused setup issues. Download the correct OS/architecture build and check version compatibility before creating or operating the cluster.
- **EC2 Fleet Request quota:** AWS may reject EKS node-group creation when account capacity or fleet-request quotas are exhausted. Check Service Quotas and existing Auto Scaling groups, and request a quota increase if needed.
- **Missing model/vectorizer files in Docker:** the serving image should not depend on locally tracked pickle files. The pipeline logs the vectorizer with the MLflow run, and the serving app downloads it using the registered model version.
- **Image URI mismatch:** the ECR repository and account/region in `deployment.yaml` must match the image built and pushed by CI.
