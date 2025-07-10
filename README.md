# mlops_scikit_learn_project_houses_function_cron_training

Este repositorio contiene la configuración y el código necesario para ejecutar tareas de entrenamiento programadas (cron) para un modelo de machine learning de predicción de precios de casas utilizando scikit-learn, como parte de un flujo MLOps.

## Estructura del repositorio

- `README.md`: Este archivo.
- Código fuente y scripts para la ejecución de tareas programadas de entrenamiento.

## Descripción

El objetivo de este proyecto es automatizar el entrenamiento periódico de un modelo de machine learning utilizando servicios de cron (por ejemplo, Cloud Functions, Cloud Scheduler o soluciones similares). Esto permite mantener el modelo actualizado con nuevos datos y facilitar la integración continua y el despliegue continuo (CI/CD) en un entorno MLOps.

## Características principales

- Entrenamiento automático y programado del modelo.
- Integración con pipelines de MLOps.
- Preparado para su despliegue en la nube (GCP, AWS, etc.).

## ¿Cómo usar este repositorio?

1. Clona el repositorio:
   ```bash
   git clone <url-del-repo>
   ```
2. Configura las variables de entorno y credenciales necesarias para tu entorno de nube.
3. Despliega la función o script según la plataforma que utilices (por ejemplo, Google Cloud Functions, AWS Lambda, etc.).
4. Configura el servicio de cron/scheduler para ejecutar el entrenamiento con la periodicidad deseada.

## Requisitos

- Python 3.8+
- scikit-learn
- (Otros requisitos según el archivo `requirements.txt`)


   ```bash
   export GCP_PROJECT_ID="xxx"
   export GCP_REGION="us-central1"
   export GCP_ARTIFACT_REGISTRY_REPO="docker-repository" 
   export GCP_VERTEX_BUCKET="mlops-training-models-for-training-46281" 
   export TRAINING_IMAGE_URI="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_ARTIFACT_REGISTRY_REPO}/house-price-trainer:latest"
   export GCS_DATA_PATH="gs://${GCP_VERTEX_BUCKET}/data/housing.csv"
   export GCS_MODEL_OUTPUT_DIR="gs://${GCP_VERTEX_BUCKET}/models/house-price-model"
   export TRAINING_SERVICE_ACCOUNT="xxxx-compute@developer.gserviceaccount.com" 
   export GCP_SERVICE_ACCOUNT="github-runner-service-account@mlops-training-462812.iam.gserviceaccount.com"
   ```

## Licencia


MIT License.
