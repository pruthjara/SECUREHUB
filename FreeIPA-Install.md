# Instalación de FreeIPA en una máquina virtual con Fedora

## 1. Documentación para el Despliegue de una Máquina Virtual Fedora en KVM

### 1.1 Preparativos

Antes de descargar la imagen de Fedora y configurar la máquina virtual,
asegúrate de tener instaladas las dependencias necesarias.

#### 1.1.2 Actualiza el sistema

```bash
sudo apt update
```

#### 1.1.3 Instala los paquetes necesarios de libvirt y virtinst para gestionar máquinas virtuales con KVM

```bash
sudo apt install libvirt-daemon-system libvirt-clients virtinst -y
```

### 1.2 Descargar la Imagen de Fedora Server

Descarga la imagen de Fedora Server para KVM usando wget, luego renómbrala para facilitar su identificación.

```bash
wget https://download.fedoraproject.org/pub/fedora/linux/releases/41/Server/x86_64/images/Fedora-Server-KVM-41-1.4.x86_64.qcow2 -P ~/
mv Fedora-Server-KVM-41-1.4.x86_64.qcow2 freeipa-fedora-server-kvm-41.qcow2
```

### 1.3 Mover la Imagen al Directorio de Imágenes de libvirt

Para que `libvirt` acceda a la imagen correctamente, cópiala al directorio predeterminado de imágenes de `libvirt`.

```bash
sudo cp freeipa-fedora-server-kvm-41.qcow2 /var/lib/libvirt/images/
```

### 1.4 Configuración Inicial de la Máquina Virtual con `qemu`

Para configurar inicialmente la máquina virtual y asegurarnos de que la imagen funciona correctamente, usaremos `qemu`. Esto nos permitirá verificar y realizar ajustes iniciales antes de pasar al despliegue completo con `virt-install`.

```bash
sudo qemu-system-x86_64 \
  -m 4096 \
  -smp 2 \
  -drive file=/var/lib/libvirt/images/freeipa-fedora-server-kvm-41.qcow2,format=qcow2 \
  -nographic \
  -serial mon:stdio
```

Este comando especifica la cantidad de memoria (4096 MB) y núcleos de CPU (2)
para la máquina virtual. Para FreeIPA son necesarios al menos 4GB de RAM.
Recuerda configurar un hostname para la máquina antes de terminar para
trabajar con ella.

```bash
sudo hostnamectl set-hostname freeipa
```

Por si fuera necesario puedes crear una backup de esta imagen.

```bash
sudo cp /var/lib/libvirt/images/freeipa-fedora-server-kvm-41.qcow2 freeipa-fedora-server-kvm-41-backup.qcow2
```

Para restaurar el backup puede utilizar

```bash
sudo cp freeipa-fedora-server-kvm-41-backup.qcow2 /var/lib/libvirt/images/freeipa-fedora-server-kvm-41.qcow2 
```

### 1.5 Configuración de la Red Bridge

Para permitir que la máquina virtual tenga conectividad de red, configura una interfaz de red bridge mediante `netplan`.

#### 1.5.1 Abre el archivo de configuración de `netplan` con el siguiente comando (reemplaza `<archivo>` por el nombre del archivo en `/etc/netplan`)

```bash
sudo nano /etc/netplan/<archivo>
```

#### 1.5.2 Añade la configuración de la red bridge

```bash
network:
    version: 2
    ethernets:
        eno1:
            dhcp4: false
    vlans:
        eno1.559:
            id: 559
            link: eno1
            dhcp4: true  # Mantener DHCP en eno1.559 para evitar pérdida de conexión
    bridges:
        br0:
            interfaces:
                - eno1.559
            addresses:
                - 138.4.11.152/25
            routes:
                - to: default
                  via: 138.4.11.131
            nameservers:
                addresses:
                    - 8.8.8.8
                    - 8.8.4.4
            dhcp4: false  # No usar DHCP en br0 porque ya estamos asignando IP manualmente
```

#### 1.5.3 Aplica los cambios de netplan para que la configuración tome efecto

```bash
sudo netplan apply
```

### 1.6 Despliegue Definitivo con virt-install

Una vez verificada y configurada la imagen de la máquina virtual, usaremos `virt-install` para desplegarla de manera definitiva. Este paso es recomendable porque `virt-install` proporciona más opciones avanzadas y facilita el manejo de la máquina virtual con `libvirt`.

Ejecuta el siguiente comando para crear la máquina virtual con `virt-install`, especificando la configuración de red bridge, CPU, memoria y otros parámetros:

```bash
sudo virt-install \
  --name fedora-freeipa \
  --ram 4096 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/freeipa-fedora-server-kvm-41.qcow2,format=qcow2,bus=virtio \
  --os-variant fedora-unknown \
  --network bridge=br0,model=virtio \
  --graphics none \
  --console pty,target_type=serial \
  --import
```

Para configurar el arranque automático de la máquina virtual al arrancar el
servidor utilice:

```bash
sudo virsh autostart fedora-freeipa
```

### 1.7 Apagar y Eliminar la Máquina Virtual

Para apagar y eliminar la máquina virtual cuando ya no la necesites, sigue estos pasos:

#### 1.7.1 Apaga la máquina virtual

```bash
sudo virsh shutdown fedora-freeipa
```

#### 1.7.2 Borra la definición de la máquina virtual

```bash
sudo virsh undefine fedora-freeipa
```

#### 1.7.3 (Opcional) Elimina el archivo de imagen de la máquina virtual si ya no es necesario

```bash
sudo rm /var/lib/libvirt/images/freeipa-fedora-server-kvm-41.qcow2
```

### 1.8 Comprobar el Estado de la Máquina Virtual

Puedes verificar el estado de las máquinas virtuales utilizando el siguiente comando:

```bash
sudo virsh list --all
```

Este comando te mostrará una lista de todas las máquinas virtuales en el sistema, incluyendo las que están detenidas.

## 2. Configuración del servidor FreeIPA

Una vez creada la VM, accede a ella e instala FreeIPA con los siguientes pasos.

### 2.1 Accede a la consola de la VM

```bash
sudo virsh console <nombre_VM>
```

### 2.2 Actualiza el sistema Fedora

```bash
sudo dnf update -y
```

### 2.3 Instala FreeIPA Server

```bash
sudo dnf install freeipa-server -y
```

### 2.4 Configura FreeIPA Server

Previamente a la instalación de FreeIPA configure en su DNS o ficheros `hosts`
el dominio apropiado como puede ser `freeipa.scrap.strast.es`

```text
# Ejemplo de añadido en /etc/hosts
127.0.1.1 freeipa.scrap.strast.es freeipa
192.168.2.1 freeipa.scrap.strast.es freeipa
```

Ejecuta el siguiente comando para iniciar la configuración interactiva de FreeIPA:

```bash
sudo ipa-server-install
```

Durante la configuración se pedirá lo siguiente:

- Do you want to configure integrated DNS (BIND)? [no]: no
- Server host name [freeipa]: freeipa.scrap.strast.es
- Please confirm the domain name [scrap.strast.es]: (press enter)
- Please provide a realm name [SCRAP.STRAST.ES]: (press enter)
- Directory Manager password
- IPA admin password
- NetBIOS domain name [SCRAP]: (press enter)
- Do you want to configure chrony with NTP server or pool address? [no]: no
- Continue to configure the system with these values? [no]: yes

### 2.5 Habilita y arranca los servicios de FreeIPA

```bash
sudo systemctl enable ipa
sudo systemctl start ipa
```

### 2.6 Verifica que FreeIPA esté en funcionamiento

```bash
sudo ipactl status
```
#### 2.6.1 Si algun servicio de FreeIPA no funciona:
```bash
sudo ipactl restart
```
### 2.7 Configuración adicional

Una vez completada la instalación, puedes acceder a la interfaz de administración de FreeIPA y gestionar los usuarios, permisos y otros recursos necesarios. Asegúrate de configurar las políticas de firewall adecuadas para permitir el tráfico hacia los servicios de FreeIPA.

### 2.8 Uninstall

```bash
sudo ipa-server-install --uninstall
```

### 2.9 Trazas tras la instalación

```text
Configuring client side components
This program will set up IPA client.
Version 4.12.2

Using existing certificate '/etc/ipa/ca.crt'.
Client hostname: freeipa.scrap.strast.es
Realm: SCRAP.STRAST.ES
DNS Domain: scrap.strast.es
IPA Server: freeipa.scrap.strast.es
BaseDN: dc=scrap,dc=strast,dc=es

Configured /etc/sssd/sssd.conf
Systemwide CA database updated.
Adding SSH public key from /etc/ssh/ssh_host_ecdsa_key.pub
Adding SSH public key from /etc/ssh/ssh_host_ed25519_key.pub
Adding SSH public key from /etc/ssh/ssh_host_rsa_key.pub
Could not update DNS SSHFP records.
SSSD enabled
Configured /etc/openldap/ldap.conf
Configured /etc/ssh/ssh_config
Configured /etc/ssh/sshd_config.d/04-ipa.conf
Configuring scrap.strast.es as NIS domain.
Client configuration complete.
The ipa-client-install command was successful


Invalid IP address 127.0.1.1 for freeipa.scrap.strast.es.: cannot use loopback IP address 127.0.1.1
Invalid IP address 127.0.1.1 for freeipa.scrap.strast.es.: cannot use loopback IP address 127.0.1.1
Please add records in this file to your DNS system: /tmp/ipa.system.records.0b9nx2e6.db
==============================================================================
Setup complete

Next steps:
	1. You must make sure these network ports are open:
		TCP Ports:
		  * 80, 443: HTTP/HTTPS
		  * 389, 636: LDAP/LDAPS
		  * 88, 464: kerberos
		UDP Ports:
		  * 88, 464: kerberos
		  * 123: ntp

	2. You can now obtain a kerberos ticket using the command: 'kinit admin'
	   This ticket will allow you to use the IPA tools (e.g., ipa user-add)
	   and the web user interface.

Be sure to back up the CA certificates stored in /root/cacert.p12
These files are required to create replicas. The password for these
files is the Directory Manager password
```

## 3. Configuración del cliente FreeIPA

Para configurar el cliente FreeIPA en un sistema, sigue los pasos a continuación:

### 3.1 Instalar el cliente FreeIPA

Ejecuta el siguiente comando para instalar el cliente FreeIPA en tu máquina:
```bash
sudo apt install freeipa-client -y
```
### 3.2 Configurar el nombre del host

Abre el archivo de configuración del hostname y define el nombre de tu máquina:
```bash
sudo nano /etc/hostname
```
Por ejemplo, cambia el contenido del archivo a:
```bash
scrap01.cluster.local
```
Guarda y cierra el archivo, luego reinicia la máquina para aplicar los cambios:
```bash
sudo reboot
```
### 3.3 Configuración en el servidor FreeIPA
En la máquina virtual que ejecuta el servidor FreeIPA, asegúrate de que los puertos necesarios estén abiertos en el firewall:

```bash
sudo firewall-cmd --permanent --add-service=freeipa-ldap
sudo firewall-cmd --permanent --add-service=freeipa-kerberos
sudo firewall-cmd --permanent --add-service=ntp
sudo firewall-cmd --reload
```
### 3.4 Ejecutar el instalador del cliente FreeIPA

Después del reinicio, ejecuta el siguiente comando para iniciar la configuración del cliente:
```bash
sudo ipa-client-install --mkhomedir
```
Durante el proceso, responde a las preguntas de la siguiente manera:
```bash
Dominio del servidor IPA: scrap.strast.es
Nombre del servidor IPA: freeipa.scrap.strast.es
```
### 3.5 Trazas tras ejecutar la instalación
```bash
This program will set up IPA client.
Version 4.11.1

WARNING: conflicting time&date synchronization service 'ntp' will be disabled in favor of chronyd

DNS discovery failed to determine your DNS domain
Provide the domain name of your IPA server (ex: example.com): scrap.strast.es
Provide your IPA server name (ex: ipa.example.com): freeipa.scrap.strast.es
The failure to use DNS to find your IPA server indicates that your resolv.conf file is not properly configured.
Autodiscovery of servers for failover cannot work with this configuration.
If you proceed with the installation, services will be configured to always access the discovered server for all operations and will not fail over to other servers in case of failure.
Proceed with fixed values and no DNS discovery? [no]: yes
Do you want to configure chrony with NTP server or pool address? [no]: no
Client hostname: scrap02.cluster.local
Realm: SCRAP.STRAST.ES
DNS Domain: scrap.strast.es
IPA Server: freeipa.scrap.strast.es
BaseDN: dc=scrap,dc=strast,dc=es

Continue to configure the system with these values? [no]: yes
Synchronizing time
No SRV records of NTP servers found and no NTP server or pool address was provided.
Using default chrony configuration.
Attempting to sync time with chronyc.
Process chronyc waitsync failed to sync time!
Unable to sync time with chrony server, assuming the time is in sync. Please check that 123 UDP port is opened, and any time server is on network.
User authorized to enroll computers: admin
Password for admin@SCRAP.STRAST.ES: 
Successfully retrieved CA cert
    Subject:     CN=Certificate Authority,O=SCRAP.STRAST.ES
    Issuer:      CN=Certificate Authority,O=SCRAP.STRAST.ES
    Valid From:  2024-11-19 22:23:02+00:00
    Valid Until: 2044-11-19 22:23:02+00:00

Enrolled in IPA realm SCRAP.STRAST.ES
Created /etc/ipa/default.conf
Configured /etc/sssd/sssd.conf
Systemwide CA database updated.
DNS query for scrap02.cluster.local. A failed: cannot open /etc/resolv.conf
DNS resolution for hostname scrap02.cluster.local failed: cannot open /etc/resolv.conf
Failed to update DNS records.
Missing A/AAAA record(s) for host scrap02.cluster.local: 192.168.1.2.
Missing reverse record(s) for address(es): 192.168.1.2.
Adding SSH public key from /etc/ssh/ssh_host_rsa_key.pub
Adding SSH public key from /etc/ssh/ssh_host_ed25519_key.pub
Adding SSH public key from /etc/ssh/ssh_host_ecdsa_key.pub
Could not update DNS SSHFP records.
SSSD enabled
Configured /etc/openldap/ldap.conf
Configured /etc/ssh/ssh_config
Configured /etc/ssh/sshd_config.d/04-ipa.conf
Configuring scrap.strast.es as NIS domain.
Configured /etc/krb5.conf for IPA realm SCRAP.STRAST.ES
Client configuration complete.
The ipa-client-install command was successful
```
