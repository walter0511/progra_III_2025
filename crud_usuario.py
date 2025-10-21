import mysql.connector
from mysql.connector import Error

class CrudUsuario:
    def __init__(self):
        print("Conectando a la base de datos para usuarios...")
        try:
            self.conexion = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='db_academica'
            )
            if self.conexion.is_connected():
                print("✅ Conexión exitosa a la base de datos para usuarios")
                # Verificar si la tabla usuarios existe
                self.verificar_tabla()
            else:
                print("❌ Error al conectar a la base de datos")
        except Error as e:
            print(f"❌ Error de conexión: {e}")

    def verificar_tabla(self):
        try:
            cursor = self.conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    idUsuario INT(10) AUTO_INCREMENT PRIMARY KEY,
                    usuario CHAR(35) NOT NULL UNIQUE,
                    clave CHAR(35) NOT NULL,
                    nombre CHAR(85) NOT NULL,
                    direccion CHAR(100),
                    telefono CHAR(9)
                )
            """)
            
            # Verificar si existe al menos un usuario
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insertar usuario por defecto
                cursor.execute("""
                    INSERT INTO usuarios (usuario, clave, nombre, direccion, telefono) 
                    VALUES ('admin', '1234', 'Administrador', 'Usulután', '7777-8888')
                """)
                self.conexion.commit()
                print("✅ Usuario por defecto creado: admin/1234")
            else:
                # Mostrar los usuarios existentes para debugging
                cursor.execute("SELECT usuario, clave FROM usuarios")
                usuarios = cursor.fetchall()
                print("📋 Usuarios en la base de datos:")
                for usuario in usuarios:
                    print(f"   Usuario: {usuario[0]}, Clave: {usuario[1]}")
            
            print("✅ Tabla 'usuarios' verificada correctamente")
            
        except Error as e:
            print(f"❌ Error verificando tabla: {e}")

    def consultar(self, sql, parametros=None):
        try:
            cursor = self.conexion.cursor(dictionary=True)
            if parametros:
                print(f"🔍 Ejecutando consulta: {sql} con parámetros: {parametros}")
                cursor.execute(sql, parametros)
            else:
                print(f"🔍 Ejecutando consulta: {sql}")
                cursor.execute(sql)
            resultado = cursor.fetchall()
            print(f"📊 Resultado de consulta: {resultado}")
            return resultado
        except Error as e:
            print(f"❌ Error en consulta: {e}")
            return []

    def ejecutar(self, sql, datos):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(sql, datos)
            self.conexion.commit()
            return "ok"
        except Error as e:
            return str(e)

    def login(self, usuario, clave):
        print(f"🔐 Intentando login - Usuario: '{usuario}', Clave: '{clave}'")
        
 
        sql_check_user = "SELECT * FROM usuarios WHERE usuario = %s"
        usuario_existente = self.consultar(sql_check_user, (usuario,))
        
        if usuario_existente:
            print(f"Usuario '{usuario}' encontrado en la base de datos")
            print(f"Datos del usuario: {usuario_existente[0]}")
        else:
            print(f" Usuario '{usuario}' NO encontrado en la base de datos")
            return None
        
        # Ahora verificamos usuario y clave
        sql = "SELECT * FROM usuarios WHERE usuario = %s AND clave = %s"
        resultado = self.consultar(sql, (usuario, clave))
        
        if resultado:
            print(f"🎉 Login exitoso para usuario: {usuario}")
            return resultado[0]
        else:
            print(f"❌ Login fallido - Clave incorrecta para usuario: {usuario}")
            return None

    def obtener_usuario_por_id(self, id_usuario):
        sql = "SELECT * FROM usuarios WHERE idUsuario = %s"
        resultado = self.consultar(sql, (id_usuario,))
        return resultado[0] if resultado else None

    def crear_usuario(self, datos):
        sql = """
            INSERT INTO usuarios (usuario, clave, nombre, direccion, telefono)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (datos['usuario'], datos['clave'], datos['nombre'], 
                   datos['direccion'], datos['telefono'])
        return self.ejecutar(sql, valores)

    def actualizar_usuario(self, datos):
        if datos['clave']:
            sql = """
                UPDATE usuarios SET usuario=%s, clave=%s, nombre=%s, 
                direccion=%s, telefono=%s WHERE idUsuario=%s
            """
            valores = (datos['usuario'], datos['clave'], datos['nombre'], 
                       datos['direccion'], datos['telefono'], datos['idUsuario'])
        else:
            sql = """
                UPDATE usuarios SET usuario=%s, nombre=%s, 
                direccion=%s, telefono=%s WHERE idUsuario=%s
            """
            valores = (datos['usuario'], datos['nombre'], 
                       datos['direccion'], datos['telefono'], datos['idUsuario'])
        return self.ejecutar(sql, valores)

    def eliminar_usuario(self, id_usuario):
        sql = "DELETE FROM usuarios WHERE idUsuario = %s"
        return self.ejecutar(sql, (id_usuario,))

    def obtener_todos_usuarios(self):
        sql = "SELECT * FROM usuarios"
        return self.consultar(sql)

# Crear instancia global
crud_usuario = CrudUsuario()