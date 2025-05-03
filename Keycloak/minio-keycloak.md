# Configuración de MinIO con Keycloak y FreeIPA (vía OpenID Connect)

Este documento describe cómo integrar MinIO con Keycloak usando OpenID Connect (OIDC), configurando Keycloak para que extraiga atributos desde FreeIPA y genere el claim `policy` necesario para que MinIO autorice correctamente a los usuarios autenticados.

---

## Requisitos previos

- Keycloak desplegado y conectado a FreeIPA como proveedor LDAP (User Federation)
- MinIO configurado para autenticarse con Keycloak (OIDC)
- Un usuario de FreeIPA existente, por ejemplo: `pruth`
- El usuario tiene un atributo `employeeType=consoleAdmin` en FreeIPA

---

## 1. Añadir el atributo `employeeType` al usuario en FreeIPA

Desde el pod de FreeIPA, ejecutar:

```bash
ipa user-mod pruth --employeetype=consoleAdmin
```
Verificar que el atributo esté presente:

```bash
ipa user-show pruth --all --raw | grep employeeType
```

## 2. Crear un LDAP Mapper en Keycloak

Ir a:  
`User Federation > [tu proveedor LDAP] > Mappers > Create`

Completar con los siguientes valores:

| Campo                        | Valor                      |
|-----------------------------|-----------------------------|
| **Name**                    | `employeeType-mapper`       |
| **Mapper Type**             | `user-attribute-ldap-mapper`|
| **User Model Attribute**    | `policy`                    |
| **LDAP Attribute**          | `employeeType`              |
| **Read Only**               | ON                          |
| **Always Read Value From LDAP** |   ON                  |
| **Is Mandatory In LDAP**    |   OFF                       |

Esto hace que el atributo `employeeType` en FreeIPA se guarde como `policy` en los usuarios federados en Keycloak.

## 3. Crear un Client Scope para MinIO

Ir a:  
`Client Scopes > Create`

- **Name**: `minio-authorization`
- **Include in token scope**: Activado

Guardar.

---

## 4. Añadir un mapper en el Client Scope

Ir a:  
`Client Scopes > minio-authorization > Mappers > Create`

Completar con los siguientes valores:

| Campo                   | Valor                 |
|-------------------------|-----------------------|
| **Mapper Type**         | `User Attribute`      |
| **Name**                | `minio-policy-mapper` |
| **User Attribute**      | `policy`              |
| **Token Claim Name**    | `policy`              |
| **Add to ID Token**     | ON                    |
| **Add to Access Token** | ON                    |
| **Claim JSON Type**     | `String`              |
| **Multivalued**         | ON                    |

---

## 5. Asignar el Client Scope al cliente `minio`

Ir a:  
`Clients > minio > Client Scopes`

- Asegurar que `minio-authorization` esté en la lista **Assigned Default Client Scopes**
- Si no está, hacer clic en **Assign** y añadirlo como **default**
## 6. Verificar que el token contiene el claim `policy`

Obtener un token usando `curl`:

```bash
curl -X POST https://keycloak.andion.eu/realms/minio/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=minio" \
  -d "client_secret=TU_CLIENT_SECRET" \
  -d "username=pruth" \
  -d "password=TU_PASSWORD"
```
Copiar el `access_token`, ir a [https://jwt.io](https://jwt.io) y verificar que contiene:

```json
"policy": "consoleAdmin"
```

## Resultado esperado

Una vez el claim `policy` está presente en el token, MinIO lo utilizará para autorizar al usuario usando sus políticas definidas (como `consoleAdmin`), y el login funcionará sin errores como: "Policy claim missing from the JWT token"








