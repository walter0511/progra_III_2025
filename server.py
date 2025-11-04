from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib import parse
from urllib.parse import urlparse, parse_qs
import json 
import crud_alumno
import os
import hashlib

port = 8000

crudAlumno = crud_alumno.crud_alumno()

# Simulación de base de datos de usuarios (en producción usa una base de datos real)
usuarios = {
    "admin": {
        "clave": hashlib.md5("1234".encode()).hexdigest(),  # En producción usa bcrypt
        "nombre": "Administrador",
        "rol": "admin"
    },
    "docente": {
        "clave": hashlib.md5("1234".encode()).hexdigest(),
        "nombre": "Docente Ejemplo", 
        "rol": "docente"
    }
}

# Diccionario para simular sesiones (en producción usa sessions reales)
sesiones = {}

class miServidor(SimpleHTTPRequestHandler):
    
    def do_GET(self):
        url_parseada = urlparse(self.path)
        path = url_parseada.path
        parametros = parse_qs(url_parseada.query)

        # Servir archivos estáticos
        if path.startswith('/static/') or '.' in path:
            return SimpleHTTPRequestHandler.do_GET(self)
            
        # Ruta principal - redirige al login
        if path == "/":
            self.path = "login.html"
            return SimpleHTTPRequestHandler.do_GET(self)
            
        # Ruta del sistema principal
        elif path == "/sistema":
            # Verificar si el usuario está autenticado
            token = self.headers.get('Cookie', '').replace('token=', '')
            if token in sesiones:
                self.path = "index.html"
                return SimpleHTTPRequestHandler.do_GET(self)
            else:
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
                return
                
        # Ruta de login
        elif path == "/login":
            self.path = "login.html"
            return SimpleHTTPRequestHandler.do_GET(self)
            
        # API para obtener alumnos
        elif path == "/alumnos":
            alumnos = crudAlumno.consultar("")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(alumnos).encode('utf-8'))
            
        # Servir vistas/modulos
        elif path == "/vistas":
            self.path = '/modulos/' + parametros['form'][0] + '.html'
            return SimpleHTTPRequestHandler.do_GET(self)
            
        # Ruta por defecto - servir archivo directamente
        else:
            if os.path.exists(self.path[1:]):
                return SimpleHTTPRequestHandler.do_GET(self)
            else:
                self.send_error(404, "File not found")
    
    def do_POST(self):
        url_parseada = urlparse(self.path)
        path = url_parseada.path
        
        # Procesar login
        if path == "/login":
            self.procesar_login()
            
        # Procesar otras peticiones POST (alumnos, docentes, etc.)
        elif path in ["/alumnos", "/docentes", "/materias", "/notas"]:
            self.procesar_datos(path)
        else:
            self.send_error(404, "Endpoint not found")
    
    def procesar_login(self):
        longitud = int(self.headers['Content-Length'])
        datos = self.rfile.read(longitud)
        datos = datos.decode("utf-8")
        datos = json.loads(datos)
        
        usuario = datos.get('usuario', '')
        clave = datos.get('clave', '')
        
        # Validar credenciales
        if usuario in usuarios and usuarios[usuario]['clave'] == hashlib.md5(clave.encode()).hexdigest():
            # Crear sesión
            import uuid
            token = str(uuid.uuid4())
            sesiones[token] = {
                'usuario': usuario,
                'nombre': usuarios[usuario]['nombre'],
                'rol': usuarios[usuario]['rol']
            }
            
            respuesta = {
                "msg": "ok", 
                "usuario": {
                    "nombre": usuarios[usuario]['nombre'],
                    "rol": usuarios[usuario]['rol']
                }
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Set-Cookie', f'token={token}; Path=/')
            self.end_headers()
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))
        else:
            respuesta = {
                "msg": "error", 
                "error": "Usuario o contraseña incorrectos"
            }
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))
    
    def procesar_datos(self, endpoint):
        longitud = int(self.headers['Content-Length'])
        datos = self.rfile.read(longitud)
        datos = datos.decode("utf-8")
        datos = parse.unquote(datos)
        datos = json.loads(datos)
        
        # Aquí puedes agregar validación de sesión si lo necesitas
        # token = self.headers.get('Cookie', '').replace('token=', '')
        # if token not in sesiones:
        #     self.send_response(401)
        #     self.end_headers()
        #     return
        
        # Procesar según el endpoint
        if endpoint == "/alumnos":
            resp = {"msg": crudAlumno.administrar(datos)}
        elif endpoint == "/docentes":
            # Aquí llamarías a tu CRUD de docentes
            resp = {"msg": "ok"}  # Placeholder
        elif endpoint == "/materias":
            # Aquí llamarías a tu CRUD de materias  
            resp = {"msg": "ok"}  # Placeholder
        elif endpoint == "/notas":
            # Aquí llamarías a tu CRUD de notas
            resp = {"msg": "ok"}  # Placeholder
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(datos).encode("utf-8"))

    def list_directory(self, path):
        # Prevenir listado de directorios
        self.send_error(404, "No permission to list directory")

print("=" * 50)
print("Servidor académico iniciando...")
print("Puerto:", port)
print("URL: http://localhost:8000")
print(f"Directorio de trabajo: {os.getcwd()}")
print("=" * 50)

# VERIFICAR ARCHIVOS NECESARIOS AL INICIO
archivos_requeridos = ['login.html', 'index.html']
print("\nVerificando archivos necesarios:")
for archivo in archivos_requeridos:
    if os.path.exists(archivo):
        print(f"  ✓ {archivo} encontrado")
    else:
        print(f"  ✗ {archivo} NO ENCONTRADO - CREAR ESTE ARCHIVO")

print("\n" + "=" * 50)

try:
    
    server = HTTPServer(("0.0.0.0", port), miServidor)
    print("Servidor iniciado correctamente!")
    print("CRUDs activos: Usuarios, Alumnos y Docentes")
    print("=" * 50)
    server.serve_forever()
except Exception as e:
    print(f"Error al iniciar el servidor: {e}")