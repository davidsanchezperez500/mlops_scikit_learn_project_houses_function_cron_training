# main.py (para Cloud Function)

import base64
import json
import os
import time
from google.cloud import aiplatform

# ==============================================================================
# Variables de entorno para la Cloud Function
# Se inyectarán durante el despliegue de la Cloud Function
# ==============================================================================
PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
REGION = os.environ.get('GCP_REGION')
TRAINING_IMAGE_URI = os.environ.get('TRAINING_IMAGE_URI')
GCS_DATA_PATH = os.environ.get('GCS_DATA_PATH')
GCS_MODEL_OUTPUT_DIR = os.environ.get('GCS_MODEL_OUTPUT_DIR')
TRAINING_SERVICE_ACCOUNT = os.environ.get('TRAINING_SERVICE_ACCOUNT')

def trigger_vertex_ai_retraining(event, context):
    """
    Cloud Function que se activa por un mensaje de Pub/Sub
    y lanza un trabajo de entrenamiento personalizado en Vertex AI.
    """
    print(f"Cloud Function activada por evento: {context.event_id}")
    print(f"Tipo de evento: {context.event_type}")

    if event.get('data'):
        message_data = base64.b64decode(event['data']).decode('utf-8')
        print(f"Mensaje de Pub/Sub recibido: {message_data}")
    else:
        print("Mensaje de Pub/Sub sin datos específicos (trigger manual o de Scheduler).")

    # Validar que todas las variables de entorno necesarias estén presentes
    if not all([PROJECT_ID, REGION, TRAINING_IMAGE_URI, GCS_DATA_PATH, GCS_MODEL_OUTPUT_DIR, TRAINING_SERVICE_ACCOUNT]):
        print("ERROR: Faltan variables de entorno para la configuración de Vertex AI.")
        missing_vars = [
            name for name, value in {
                "PROJECT_ID": PROJECT_ID,
                "REGION": REGION,
                "TRAINING_IMAGE_URI": TRAINING_IMAGE_URI,
                "GCS_DATA_PATH": GCS_DATA_PATH,
                "GCS_MODEL_OUTPUT_DIR": GCS_MODEL_OUTPUT_DIR,
                "TRAINING_SERVICE_ACCOUNT": TRAINING_SERVICE_ACCOUNT
            }.items() if value is None
        ]
        raise ValueError(f"Variables de entorno incompletas: {', '.join(missing_vars)}")

    try:
        # Inicializar el cliente de Vertex AI
        aiplatform.init(project=PROJECT_ID, location=REGION)

        # Nombre del trabajo de entrenamiento (único para cada ejecución)
        job_display_name = f"house-price-retrain-job-{time.strftime('%Y%m%d-%H%M%S')}"

        # Extraer el nombre del bucket de staging del GCS_MODEL_OUTPUT_DIR
        # Ejemplo: gs://my-bucket/models/ -> my-bucket
        staging_bucket_name = GCS_MODEL_OUTPUT_DIR.split('/')[2]
        staging_bucket_uri = f"gs://{staging_bucket_name}"

        # ======================================================================
        # CAMBIO CLAVE AQUÍ: Usar worker_pool_specs en lugar de container_uri directo
        # ======================================================================
        job = aiplatform.CustomJob(
            display_name=job_display_name,
            # La especificación del contenedor va dentro de worker_pool_specs
            worker_pool_specs=[
                {
                    "machine_spec": {
                        "machine_type": "n1-standard-4", # Tipo de máquina para el job de entrenamiento
                        "accelerator_type": None, # Puedes especificar "NVIDIA_TESLA_T4" si usas GPU
                        "accelerator_count": 0, # Número de GPUs
                    },
                    "replica_count": 1, # Número de réplicas de workers
                    "container_spec": {
                        "image_uri": TRAINING_IMAGE_URI, # Aquí va la URI de la imagen de entrenamiento
                        "command": [], # No es necesario si el ENTRYPOINT del Dockerfile ya ejecuta el script
                        "args": [
                            f"--data-path={GCS_DATA_PATH}",
                            f"--model-dir={GCS_MODEL_OUTPUT_DIR}"
                        ],
                    },
                }
            ],
            project=PROJECT_ID,
            location=REGION,
            staging_bucket=staging_bucket_uri
        )

        # Iniciar el trabajo
        print(f"Lanzando trabajo de entrenamiento personalizado: {job_display_name}")
        job.run(
            service_account=TRAINING_SERVICE_ACCOUNT,
            sync=False # No esperar a que el trabajo termine, solo lanzarlo
        )
        print(f"Trabajo de entrenamiento {job_display_name} lanzado exitosamente.")

    except Exception as e:
        print(f"Error al lanzar el trabajo de entrenamiento en Vertex AI: {e}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Fallo al lanzar el trabajo de entrenamiento: {e}")

