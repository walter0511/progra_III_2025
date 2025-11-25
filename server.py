from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse
from urllib.parse import urlparse, parse_qs
import json
import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model('grados.h5')
port = 3000

class miServidor(SimpleHTTPRequestHandler):
    def do_GET(self):
        url_parseada = urlparse(self.path)
        path = url_parseada.path
        parametros = parse_qs(url_parseada.query)

        if self.path=="/":
            self.path="index.html"
            return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        longitud = int(self.headers.get('Content-Length', 0))
        datos = self.rfile.read(longitud)
        datos = datos.decode("utf-8")
        datos = parse.unquote(datos)
        datos = json.loads(datos)
        c = float(datos['celsius'])
        
        # Usar el modelo para predecir Kelvin y Fahrenheit (entrando como array 2D)
        preds = model.predict(np.array([[c]]))
        kelvin = float(preds[0][0])
        fahrenheit = float(preds[0][1])
        
        resp = {
            "kelvin": round(kelvin, 2),
            "fahrenheit": round(fahrenheit, 2)
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode("utf-8"))

print("Servidor ejecutandose en el puerto", port)
server = HTTPServer(("localhost", port), miServidor)
server.serve_forever()