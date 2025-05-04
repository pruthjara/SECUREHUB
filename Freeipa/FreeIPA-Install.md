## Despliegue de FreeIPA en Kubernetes

Para desplegar correctamente FreeIPA en un entorno Kubernetes, es necesario aplicar los siguientes archivos de configuración:

### Archivos necesarios

- `FreeIPA-Install-MVFedora.md`: Guía para crear una imagen personalizada basada en Fedora.
- `FreeIPA-Install.md`: Instrucciones detalladas de despliegue.
- `freeipa-data.yaml`: Define el volumen persistente para los datos de FreeIPA.
- `freeipa-ingress.yaml`: Configuración del Ingress para exponer el servicio de FreeIPA.
- `freeipa-install-options.yaml`: Opciones de instalación como entorno, dominio, contraseña, etc.
- `freeipa-secret.yaml`: Secretos necesarios para el despliegue (credenciales, etc.).
- `freeipa-service.yaml`: Define el servicio de red para acceder al pod.
- `freeipa-statefulset.yaml`: Define el StatefulSet que despliega y mantiene el pod de FreeIPA.

> ⚠️ **IMPORTANTE:**  
> Si deseas desplegar de nuevo FreeIPA después de haberlo eliminado, asegúrate de:
>
> - Eliminar el **PersistentVolume** y el **Logical Volume Claim** creados en `freeipa-data.yaml`.
> - Cambiar los **nombres** del PV y PVC, y modificar también la **ruta del volumen** para evitar conflictos con datos persistentes antiguos.

---

## Regenerar el keytab del administrador

Si cambias la contraseña del usuario `admin` de FreeIPA, es necesario regenerar el archivo `keytab` y actualizar el secreto `keytab-secret.yaml` que utiliza el backend para obtener un ticket de Kerberos.

### Pasos para regenerar el keytab:

1. Accede al pod de FreeIPA:

   ```bash
   kubectl exec -it freeipa-0 -- bash
   ```

2. Ejecuta el siguiente comando dentro del pod para obtener un nuevo keytab:
   ```bash
   ipa-getkeytab -s freeipa.andion.eu -p admin@ANDION.EU -k /tmp/admin.keytab
   ```
   Deberías ver: Keytab successfully retrieved and stored in: /tmp/admin.keytab

3. Codifica el keytab en base64:
   ```bash
   base64 /tmp/admin.keytab
   ```
4. Copia el contenido codificado y reemplázalo en el campo correspondiente del archivo keytab-secret.yaml, por ejemplo:
   ```bash
   apiVersion: v1
   kind: Secret
   metadata:
     name: keytab-secret
   type: Opaque
   data:
     admin.keytab: <contenido base64 aquí>
   ```
5. Aplica el secreto actualizado:
   ```bash
   kubectl apply -f keytab-secret.yaml
   ```

## Instalación del cliente de FreeIPA en nodos

Para que los nodos (por ejemplo, donde corre el backend) puedan autenticarse con FreeIPA, se debe instalar el cliente de FreeIPA. A continuación se indican los pasos para instalar correctamente el cliente y, al final, cómo eliminarlo en caso necesario.

### Instalación del cliente FreeIPA

1. **Instala los paquetes necesarios:**

   ```bash
   sudo apt update
   sudo apt install freeipa-client -y
   ```
2. **Ejecuta la configuración interactiva del cliente:**
   ```bash
   sudo ipa-client-install --mkhomedir
   ```
Durante el proceso se te pedirá el dominio (ANDION.EU) y la IP o FQDN del servidor FreeIPA (freeipa.andion.eu). También deberás autenticarte con un usuario administrador.

3. **Verifica que el cliente se unió correctamente al dominio:**
   ```bash
   ipa user-find
   ```
Ahora el nodo podrá autenticarse usando Kerberos y acceder a recursos gestionados por FreeIPA.

### Eliminación de un cliente anterior (si es necesario)
Si el cliente ya estaba instalado y deseas hacer una reinstalación limpia, puedes eliminarlo con los siguientes comandos:
  ```bash
  sudo apt remove --purge freeipa-client -y
  sudo rm -rf /etc/ipa /var/lib/ipa /var/log/ipa*
  sudo apt remove --purge sssd* -y
  sudo rm -rf /etc/sssd /var/lib/sss /var/log/sssd
  sudo rm -f /etc/krb5.conf /var/lib/krb5kdc
  ```
## Restablecer contraseña de un usuario en FreeIPA

En caso de que necesites restablecer la contraseña de un usuario directamente desde el servidor FreeIPA, puedes hacerlo utilizando la herramienta `kadmin.local`, que permite gestionar la base de datos de Kerberos localmente sin necesidad de autenticarse.

### Pasos para restablecer la contraseña:

1. Accede al pod de FreeIPA:
   ```bash
   kubectl exec -it freeipa-0 -- bash
   ```
2. Inicia la consola administrativa de Kerberos:
   ```bash
   sudo kadmin.local
   ```
3. Una vez dentro, ejecuta el siguiente comando para cambiar la contraseña del usuario deseado:
   ```bash
   kadmin.local: cpw <nombre-de-usuario>
   ```
   Se te pedirá que introduzcas la nueva contraseña.

**Este método es útil para realizar cambios urgentes sin depender de la interfaz web de FreeIPA.**

