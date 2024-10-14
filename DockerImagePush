#!/bin/bash

# Nuevos nombres de las imágenes
REPO_BACKEND="strast-upm/securehub_backend"
REPO_FRONTEND="strast-upm/securehub_frontend"
TAG="latest"
USERNAME="pruthjara"
TOKEN="-"

# Función para ejecutar un comando y verificar errores
run_command() {
  command=$1
  error_message=$2

  if ! eval "$command"; then
    echo "Error: $error_message"
    exit 1
  fi
}

# Función para eliminar las imágenes locales antiguas
remove_old_local_images() {
  images_to_remove=(
    "securehub-backend:latest"
    "securehub-frontend:latest"
    "ghcr.io/strast-upm/securehub_backend:latest"
    "ghcr.io/strast-upm/securehub_frontend:latest"
  )

  for image in "${images_to_remove[@]}"; do
    echo "Eliminando imagen local $image..."
    remove_command="docker rmi -f $image"
    run_command "$remove_command" "Error al eliminar la imagen local $image"
  done
}

# Función para obtener el ID de la imagen
get_image_id() {
  image_name=$1
  docker images -q "$image_name"
}

# Función principal
main() {
  compose_file_path=$1

  # Verificar que USERNAME y TOKEN estén definidos
  if [[ -z "$USERNAME" || -z "$TOKEN" ]]; then
    echo "Error: Las variables de entorno 'USERNAME' y 'TOKEN' deben estar definidas."
    exit 1
  fi

  # Eliminar las imágenes locales antes de reconstruir
  remove_old_local_images

  # Construir las imágenes con Docker Compose sin caché
  echo "Construyendo las imágenes Docker con Docker Compose desde $compose_file_path..."
  build_command="docker-compose -f $compose_file_path build --no-cache"
  run_command "$build_command" "Error al construir las imágenes con Docker Compose"

  # Obtener los IDs de las imágenes recién construidas
  backend_image_name="securehub-backend"
  frontend_image_name="securehub-frontend"

  backend_image_id=$(get_image_id "$backend_image_name")
  frontend_image_id=$(get_image_id "$frontend_image_name")

  if [[ -z "$backend_image_id" ]]; then
    echo "Error: No se pudo encontrar la imagen del backend después de la construcción."
    exit 1
  fi

  if [[ -z "$frontend_image_id" ]]; then
    echo "Error: No se pudo encontrar la imagen del frontend después de la construcción."
    exit 1
  fi

  # Etiquetar las imágenes para GitHub Container Registry
  echo "Etiquetando la imagen del backend..."
  tag_backend_command="docker tag $backend_image_id ghcr.io/$REPO_BACKEND:$TAG"
  run_command "$tag_backend_command" "Error al etiquetar la imagen del backend"

  echo "Etiquetando la imagen del frontend..."
  tag_frontend_command="docker tag $frontend_image_id ghcr.io/$REPO_FRONTEND:$TAG"
  run_command "$tag_frontend_command" "Error al etiquetar la imagen del frontend"

  # Autenticarse en GitHub Container Registry
  echo "Autenticándose en GitHub Container Registry..."
  login_command="echo $TOKEN | docker login ghcr.io -u $USERNAME --password-stdin"
  run_command "$login_command" "Error al autenticar en GitHub Container Registry"

  # Subir las imágenes al registro
  echo "Subiendo la imagen del backend al registro de GitHub..."
  push_backend_command="docker push ghcr.io/$REPO_BACKEND:$TAG"
  run_command "$push_backend_command" "Error al subir la imagen del backend al registro de GitHub"

  echo "Subiendo la imagen del frontend al registro de GitHub..."
  push_frontend_command="docker push ghcr.io/$REPO_FRONTEND:$TAG"
  run_command "$push_frontend_command" "Error al subir la imagen del frontend al registro de GitHub"

  echo "¡Imágenes Docker subidas exitosamente!"
}

# Verificar que se haya pasado el archivo de Docker Compose como argumento
if [[ $# -ne 1 ]]; then
  echo "Uso: $0 <ruta_del_docker_compose>"
  exit 1
fi

compose_file_path=$1
main "$compose_file_path"
