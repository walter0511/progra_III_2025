import crud_academico

db = crud_academico.crud()

class crud_docente:
    
    def __init__(self):
        print("CRUD Docentes inicializado")
    
    def consultar(self, buscar):
        return db.consultar("SELECT * FROM docentes WHERE nombre like '%"+ buscar +"%'")
   
    def administrar(self, datos):
        if datos['accion']=="nuevo":
            sql = """
                INSERT INTO docentes (codigo, nombre, direccion, telefono, email, especialidad)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            valores = (datos['codigo'], datos['nombre'], datos['direccion'], datos['telefono'], datos['email'], datos['especialidad'])
        
        if datos['accion']=="modificar":
            sql = """
                UPDATE docentes SET codigo=%s, nombre=%s, direccion=%s, telefono=%s, email=%s, especialidad=%s
                WHERE idDocente=%s
            """
            valores = (datos['codigo'], datos['nombre'], datos['direccion'], datos['telefono'], datos['email'], datos['especialidad'], datos['idDocente'])
        
        if datos['accion']=="eliminar":
            sql = "DELETE FROM docentes WHERE idDocente=%s"
            valores = (datos['idDocente'],)
        
        return db.ejecutar(sql, valores)