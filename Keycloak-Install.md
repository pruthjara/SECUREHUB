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
spec:
  selector:
    app: keycloak
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: LoadBalancer
```

