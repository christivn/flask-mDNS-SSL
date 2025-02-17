# Flask Application with mDNS and SSL (Using mkcert)

Este proyecto permite ejecutar una aplicación Flask en HTTPS sobre un dominio local (por ejemplo, `example.local`) en una red local. Utiliza mDNS (Multicast DNS) para resolver el nombre de dominio localmente y `mkcert` para generar un certificado SSL válido para el dominio `.local` sin advertencias de seguridad.

## Requisitos

1. Python 3.x
2. `pip` para instalar dependencias.
3. `mkcert` para generar certificados SSL válidos para dominios locales.

## Pasos de configuración

### 1. Instalar `mkcert`

`mkcert` es una herramienta que genera certificados SSL válidos para dominios locales.

#### **Instalación en macOS**:

```bash
brew install mkcert
```

#### **Instalación en Linux (Debian/Ubuntu)**:

```bash
sudo apt install mkcert
```

#### **Instalación en Windows**:

Si usas **Windows**, puedes instalar `mkcert` con [Chocolatey](https://chocolatey.org):

```bash
choco install mkcert
```

### 2. Crear una Autoridad Certificadora (CA) local

Una vez instalado `mkcert`, crea la CA local ejecutando el siguiente comando:

```bash
mkcert -install
```

Esto instalará una autoridad certificadora (CA) que será confiable para los certificados generados en tu máquina.

### 3. Generar el certificado SSL para `example.local`

Ahora, genera un certificado SSL para el dominio `example.local` (o cualquier dominio `.local` que desees):

```bash
mkcert example.local
```

Este comando generará dos archivos en tu directorio actual:

- `example.local.pem` (certificado SSL)
- `example.local-key.pem` (clave privada)

### 4. Configurar Flask para usar SSL y mDNS

Ahora que tienes el certificado SSL, configura tu aplicación Flask para usar HTTPS y anunciarla en la red local usando mDNS (con `zeroconf`).

#### **Instalar dependencias necesarias**:

Instala las dependencias del proyecto utilizando `pip`:

```bash
pip install Flask zeroconf
```

#### **Código del servidor Flask (app.py)**:

```python
from flask import Flask
from zeroconf import Zeroconf, ServiceInfo
import socket
import ssl

# Crea la aplicación Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    # Configuración de Zeroconf para mDNS
    zeroconf = Zeroconf()

    # Información del servicio (puerto y tipo de servicio)
    desc = {'path': '/'}
    info = ServiceInfo(
        "_http._tcp.local.",
        "example.local._http._tcp.local.",
        addresses=[socket.inet_aton("127.0.0.1")],  # Dirección IP local
        port=80,  # Usando el puerto 80
        properties=desc,
    )

    # Registra el servicio mDNS
    zeroconf.register_service(info)

    try:
        # Cargar el certificado SSL y la clave privada generada por mkcert
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile='example.local.pem', keyfile='example.local-key.pem')

        # Inicia el servidor Flask en HTTPS con SSL en el puerto 80
        app.run(host='0.0.0.0', port=80, ssl_context=context)
    finally:
        # Desregistra el servicio mDNS cuando se detenga
        zeroconf.unregister_service(info)
        zeroconf.close()
```

Este código hace lo siguiente:
- Registra el servicio en la red local usando mDNS con `zeroconf`.
- Configura Flask para servir la aplicación en HTTPS, usando los certificados generados por `mkcert`.

### 5. Ejecutar la aplicación

Una vez que todo esté configurado, ejecuta el script de Flask:

```bash
python app.py
```

### 6. Acceder a la aplicación

Puedes acceder a tu aplicación en la siguiente URL en tu navegador:

```
https://example.local
```

El certificado SSL será válido porque fue generado por `mkcert`, por lo que no aparecerán advertencias de "sitio no confiable" en tu navegador (solo en máquinas que tengan instalada la misma CA).

### Notas adicionales

- Si otros dispositivos en la misma red local también necesitan confiar en este certificado, puedes exportar la CA local desde tu máquina y agregarla como "confiable" en esos dispositivos.
  
  - En **macOS** y **iOS**, puedes agregar la CA local al llavero (Keychain) como "confiable".
  - En **Windows**, puedes agregarla a través de las opciones de certificados en el panel de control.

- Si deseas usar otro dominio local (por ejemplo, `dev.local`), simplemente reemplaza `example.local` en los comandos y en el código de Flask.
