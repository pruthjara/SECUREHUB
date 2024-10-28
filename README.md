# SecureHub Deployment Repository

Este repositorio contiene los archivos necesarios para desplegar la aplicación **SecureHub** en un entorno Kubernetes, utilizando Helm para gestionar el despliegue. La aplicación se compone de un **frontend** y un **backend**, cada uno con su propia configuración de despliegue y servicio.

## Estructura de Archivos

- **Helm chart for deployment**  
  Carpeta que contiene el chart de Helm para gestionar el despliegue de la aplicación en Kubernetes, facilitando la instalación, actualización y configuración de los recursos de manera controlada.
  
- **securehubback-deployment.yaml**  
  Archivo de configuración para el despliegue del **backend** de SecureHub. Define las especificaciones de recursos, réplicas, imagen Docker y variables de entorno del backend en Kubernetes.

- **securehubback-service.yaml**  
  Archivo de configuración del **servicio** asociado al backend de SecureHub, que expone el backend dentro del clúster de Kubernetes y le permite comunicarse con otros servicios (como el frontend).

- **securehubfront-deployment.yaml**  
  Archivo de configuración para el despliegue del **frontend** de SecureHub. Similar al backend, define las especificaciones de recursos, imagen Docker y variables de entorno, y se asegura de que el frontend esté configurado correctamente para conectarse al backend.

- **securehubfront-service.yaml**  
  Archivo de configuración del **servicio** asociado al frontend de SecureHub, que expone el frontend en Kubernetes y permite su acceso dentro del clúster o, si está configurado, hacia el exterior.

## Instrucciones para el Despliegue

1. **Instalación de Helm**: Asegúrate de tener Helm instalado en tu sistema.
2. **Configurar el Chart de Helm**: Revisa y ajusta los valores en el archivo `values.yaml` dentro del chart para personalizar los recursos y configuraciones.
3. **Aplicar los Recursos en Kubernetes**:
   - Aplica los archivos `securehubback-deployment.yaml` y `securehubback-service.yaml` para desplegar y exponer el backend.
   - Aplica los archivos `securehubfront-deployment.yaml` y `securehubfront-service.yaml` para desplegar y exponer el frontend.
4. **Monitoreo y Gestión**: Utiliza los comandos de Helm para monitorear y actualizar el despliegue según sea necesario.

Este repositorio está diseñado para facilitar el despliegue modular de los componentes de SecureHub en Kubernetes, proporcionando una estructura clara para la administración de ambos servicios (frontend y backend) con Helm.


