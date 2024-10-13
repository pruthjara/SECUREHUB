import subprocess
import os
import sys

REPO_BACKEND = "strast-upm/syscontrol_back"
REPO_FRONTEND = "strast-upm/syscontrol_front"
TAG = "latest"
USERNAME = "pruthjara" 
TOKEN = "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"   


def run_command(command, error_message):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_message}\nDetalles del error: {e}")
        sys.exit(1)

def remove_old_local_images():
    # Posibles imágenes antiguas
    images_to_remove = [
        "syscontrol-backend:latest",
        "syscontrol-frontend:latest",
        "ghcr.io/strast-upm/syscontrol_back:latest",
        "ghcr.io/strast-upm/syscontrol_front:latest"
    ]
    
    for image in images_to_remove:
        print(f"Eliminando imagen local {image}...")
        remove_command = f"docker rmi -f {image}"
        run_command(remove_command, f"Error al eliminar la imagen local {image}")

def get_image_id(image_name):
    result = subprocess.run(
        f"docker images -q {image_name}",
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )
    return result.stdout.strip()

def main(compose_file_path):
    # Verificar que USERNAME y TOKEN estén definidos
    if not USERNAME or not TOKEN:
        print("Error: Las variables de entorno 'GITHUB_USERNAME' y 'GITHUB_TOKEN' deben estar definidas.")
        sys.exit(1)

    # Eliminar las imágenes locales antes de reconstruir
    remove_old_local_images()

    # Construir las imágenes con Docker Compose sin caché
    print(f"Construyendo las imágenes Docker con Docker Compose desde {compose_file_path}...")
    build_command = f"docker-compose -f {compose_file_path} build --no-cache"
    run_command(build_command, "Error al construir las imágenes con Docker Compose")

    # Obtener los IDs de las imágenes recién construidas
    backend_image_name = "syscontrol-backend"
    frontend_image_name = "syscontrol-frontend"

    backend_image_id = get_image_id(backend_image_name)
    frontend_image_id = get_image_id(frontend_image_name)

    if not backend_image_id:
        print("Error: No se pudo encontrar la imagen del backend después de la construcción.")
        sys.exit(1)

    if not frontend_image_id:
        print("Error: No se pudo encontrar la imagen del frontend después de la construcción.")
        sys.exit(1)

    # Etiquetar las imágenes para GitHub Container Registry
    print("Etiquetando la imagen del backend...")
    tag_backend_command = f"docker tag {backend_image_id} ghcr.io/{REPO_BACKEND}:{TAG}"
    run_command(tag_backend_command, "Error al etiquetar la imagen del backend")

    print("Etiquetando la imagen del frontend...")
    tag_frontend_command = f"docker tag {frontend_image_id} ghcr.io/{REPO_FRONTEND}:{TAG}"
    run_command(tag_frontend_command, "Error al etiquetar la imagen del frontend")

    # Autenticarse en GitHub Container Registry
    print("Autenticándose en GitHub Container Registry...")
    login_command = f"echo {TOKEN} | docker login ghcr.io -u {USERNAME} --password-stdin"
    run_command(login_command, "Error al autenticar en GitHub Container Registry")

    # Subir las imágenes al registro
    print("Subiendo la imagen del backend al registro de GitHub...")
    push_backend_command = f"docker push ghcr.io/{REPO_BACKEND}:{TAG}"
    run_command(push_backend_command, "Error al subir la imagen del backend al registro de GitHub")

    print("Subiendo la imagen del frontend al registro de GitHub...")
    push_frontend_command = f"docker push ghcr.io/{REPO_FRONTEND}:{TAG}"
    run_command(push_frontend_command, "Error al subir la imagen del frontend al registro de GitHub")

    print("¡Imágenes Docker subidas exitosamente!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python DockerImagePush.py <ruta_del_docker_compose>")
        sys.exit(1)

    compose_file_path = sys.argv[1]
    main(compose_file_path)