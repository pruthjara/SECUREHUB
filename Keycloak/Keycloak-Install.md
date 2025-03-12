# Instalación y Configuración de Keycloak en Kubernetes

Este documento describe cómo instalar y configurar **Keycloak** en un clúster de Kubernetes, junto con la configuración de clientes para frontend y backend, y la integración con **LDAP de FreeIPA**.

## 1. Desplegar Keycloak en Kubernetes

### 1.1. Aplicar el Deployment y Service

Ejecuta el siguiente archivo YAML en tu clúster:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
  namespace: securehub
spec:
  replicas: 1
  selector:
    matchLabels:
      app: keycloak
  template:
    metadata:
      labels:
        app: keycloak
    spec:
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:latest
        args: ["start-dev"]
        ports:
          - containerPort: 8080
        env:
          - name: KEYCLOAK_ADMIN
            value: "admin"
          - name: KEYCLOAK_ADMIN_PASSWORD
            value: "admin123"

---
apiVersion: v1
kind: Service
metadata:
  name: keycloak-service
  namespace: securehub
  annotations:
    metallb.universe.tf/address-pool: "primary"
    metallb.universe.tf/allow-shared-ip: "true"
spec:
  selector:
    app: keycloak
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: LoadBalancer
```
### 1.2. Aplicar la configuración en el clúster
Ejecuta el siguiente comando para desplegar Keycloak:
```
kubectl apply -f keycloak-deployment.yaml
```

Verifica que el servicio esté corriendo:
```
kubectl get pods -n securehub
kubectl get svc -n securehub
```
Si todo está bien, deberías ver un LoadBalancer con un EXTERNAL-IP en el servicio keycloak-service.

### 1.3. Acceder a la Interfaz Web de Keycloak
Una vez desplegado, accede a la interfaz de administración en:
```
http://<EXTERNAL-IP>:8080
```
Inicia sesión con las credenciales configuradas en el deployment:
```
Usuario: admin
Contraseña: admin123
```
## 2. Configuración de Clientes en Keycloak

### 2.1. Crear un Cliente para el Backend
Accede a Keycloak y entra en el Realm "master" (o crea un nuevo realm si prefieres).

Ve a Clientes → Crear Cliente.

Configura los siguientes valores:
- ID del Cliente: securehub-backend
- Tipo de Acceso: Confidential
- Root URL: http://backend-service:9000

Guarda los cambios y en la pestaña Credenciales, copia el client-secret.
### 2.2. Crear un Cliente para el Frontend

Accede a Clientes → Crear Cliente.

Configura los siguientes valores:
- ID del Cliente: securehub-frontend
- Tipo de Acceso: Public
- Root URL: http://frontend-service:3030
- Valid Redirect URIs: http://frontend-service:3030/*
- Web Origins: http://frontend-service:3030
  
Guarda los cambios.

## 3. Configuración de Keycloak con LDAP de FreeIPA

### 3.1. Añadir FreeIPA como Proveedor de Usuarios
Ve a Keycloak → Proveedores de Usuarios.

Haz clic en Agregar Proveedor y elige LDAP.

Configura:
- Nombre: freeipa-ldap
- Ednpoint LDAP: ldap://freeipa-service:389
- DN Base: dc=securehub,dc=com
- DN de Administración: uid=admin,cn=users,cn=accounts,dc=securehub,dc=com
- Contraseña: (la de FreeIPA)
- Modo de sincronización: PERIODIC
  
Guarda y haz clic en Sincronizar Usuarios.
### 3.2. Configurar Atributos de Usuario
En el proveedor LDAP, ve a Mappers.

Agrega:
- uid → username
- mail → email
- cn → full name
  
Guarda los cambios.
### 3.3. Habilitar Inicio de Sesión con LDAP
Ve a Autenticación → Flows.

Edita el flujo de autenticación e inserta LDAP Login.

Prueba iniciar sesión con un usuario de FreeIPA.


