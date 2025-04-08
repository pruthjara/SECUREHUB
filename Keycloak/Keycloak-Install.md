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
- Root URL: http://backend-service:9000 (usar IP externa, no nombre del servicio)

Guarda los cambios y en la pestaña Credenciales, copia el client-secret.
### 2.2. Crear un Cliente para el Frontend

Accede a Clientes → Crear Cliente.

Configura los siguientes valores:
- ID del Cliente: securehub-frontend
- Tipo de Acceso: Public
- Root URL: http://frontend-service:3030 (usar IP externa, no nombre del servicio)
- Valid Redirect URIs: http://frontend-service:3030/* (usar IP externa, no nombre del servicio)
- Web Origins: http://frontend-service:3030 (usar IP externa, no nombre del servicio)
  
Guarda los cambios.

## 3. Configuración de Keycloak con LDAP de FreeIPA

### 3.1. Añadir FreeIPA como Proveedor de Usuarios
Ve a Keycloak → User federation.

Haz clic en Agregar Proveedor y elige LDAP.

#### Configuración de la conexión LDAP con FreeIPA
- Nombre: freeipa-ldap
- Proveedor: Active Directory
- Endpoint LDAP: ldap://freeipa.andion.eu
- Habilitar StartTLS: No
- Tipo de autenticación: Simple
- Bind DN: uid=admin,cn=users,cn=accounts,dc=andion,dc=eu
- Contraseña: (la de FreeIPA)

#### Configuración de búsqueda y actualización en LDAP
- Modo de edición: READ_ONLY
- Users DN: cn=users,cn=accounts,dc=andion,dc=eu
- Atributo LDAP del nombre de usuario: uid
- Atributo LDAP del RDN: uid
- Atributo UUID LDAP: ipaUniqueID
- Clases de objeto del usuario: person, organizationalperson, top, inetorgperson
- Filtro de búsqueda de usuario: (opcional)
- Ámbito de búsqueda: One Level
- Habilitar paginación: Sí
- Referencias LDAP: Ignorar

#### Configuración de sincronización
- Importación de usuarios: Activada
- Sincronización de registros: Activada
- Tamaño de lote: (valor predeterminado o ajustado según necesidades)
- Sincronización periódica completa: Activada
- Frecuencia de sincronización completa: (definir el tiempo)
- Sincronización periódica de cambios: Activada
- Frecuencia de sincronización de cambios: (definir el tiempo)
- Integración con Kerberos
- Permitir autenticación Kerberos: No
- Usar Kerberos para autenticación de contraseña: No

#### Configuración de caché
- Política de caché: DEFAULT
- Configuración avanzada
- Habilitar operación extendida de modificación de contraseña LDAPv3: No
- Validar políticas de contraseña: No
- Confiar en el correo electrónico: No
- Rastreo de conexión: No
- Consultar extensiones soportadas: (según necesidades)

### 3.3. Habilitar Inicio de Sesión con LDAP

Ve a User federation  → freeipa-ldap  → Actions (Desplegable arriba a la derecha) → Sync All Users

Prueba iniciar sesión con un usuario de FreeIPA.


