# SecureHub Deployment Repository

Este repositorio contiene los archivos necesarios para desplegar la aplicación SecureHub en un entorno Kubernetes. La aplicación se compone de varios componentes clave: backend, frontend, FreeIPA y Keycloak, cada uno con su propia configuración de despliegue y servicio.

## Estructura de Archivos

- **Backend/**  
  Contiene los archivos de configuración y despliegue del backend de SecureHub.

- **Frontend/**  
  Contiene los archivos de configuración y despliegue del frontend de SecureHub.

- **FreeIPA/**  
  Contiene los archivos de configuración para la integración de SecureHub con FreeIPA para la gestión de usuarios y autenticación.

- **Keycloak/**  
  Contiene los archivos de configuración de Keycloak, el servicio de autenticación centralizado que gestiona el inicio de sesión en SecureHub.

- **LICENSE**  
  Archivo con la licencia del proyecto.

- **README.md**  
  Este documento con información sobre el despliegue de SecureHub.

---

## Instrucciones para el Despliegue

### 1. Configuración del Entorno Kubernetes

Asegúrate de tener un clúster de Kubernetes configurado y accesible desde tu sistema.

---

### 2. Despliegue de los Componentes

Ejecuta los siguientes pasos para desplegar cada componente de SecureHub:

- **Backend**  
  Aplica los archivos de despliegue y servicio del backend usando:  
  ```bash
  kubectl apply -f Backend/
  ```
- **Frontend**
  Aplica los archivos de despliegue y servicio del frontend usando:
  ```bash
  kubectl apply -f Frontend/
  ```
- **FreeIPA**
  Despliega FreeIPA para la gestión de usuarios y autenticación usando los archivos en:
  ```bash
  kubectl apply -f FreeIPA/
  ```
- **Keycloak**
  Despliega Keycloak, configurado para autenticarse con FreeIPA mediante LDAP, usando los archivos en:
  ```bash
  kubectl apply -f Keycloak/
  ```
  
### 3. Monitoreo y Gestión

Utiliza los comandos de kubectl para monitorear, actualizar y gestionar los despliegues según sea necesario, por ejemplo:
```bash
kubectl get pods
kubectl get services
kubectl logs <nombre-del-pod>
```
## Links
- Securehub Frontend: http://138.4.11.249:3030
- FreeIPA API: https://freeipa.andion.eu/ipa/ui/
