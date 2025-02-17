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
