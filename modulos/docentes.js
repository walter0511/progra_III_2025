var accion = "nuevo",
    idDocente = 0;
document.addEventListener("DOMContentLoaded", event=>{ 
    frmDocentes.addEventListener("submit",e=>{
        e.preventDefault();

        guardarDocentes();
    });
    obtenerDocentes();
});
async function guardarDocentes(){
    let datos = {
        accion,
        idDocente,
        codigo: txtCodigoDocente.value,
        nombre: txtNombreDocente.value,
        direccion: txtDireccionDocente.value,
        telefono: txtTelefonoDocente.value,
        email: txtEmailDocente.value,
        especialidad: txtEspecialidadDocente.value
    };
    let response = await fetch("/docentes",{
        method: "POST",
        body: JSON.stringify(datos),
    }), 
        respuesta = await response.json();
    if(respuesta.msg!="ok"){
        alertify.error(`Error al procesar docente: ${respuesta}`);
        return;
    }
    limpiarFormulario();
    obtenerDocentes();
}
function limpiarFormulario(){
    accion = "nuevo";
    idDocente = 0;
    txtCodigoDocente.value = "";
    txtNombreDocente.value = "";
    txtDireccionDocente.value = "";
    txtTelefonoDocente.value = "";
    txtEmailDocente.value = "";
    txtEspecialidadDocente.value = "";
}
async function obtenerDocentes(){
    let response = await fetch("/docentes"), 
        respuesta = await response.json();
    mostrarDatosDocentes(respuesta);
}
function mostrarDatosDocentes(docentes){
    let filas = "";
    docentes.forEach(docente=>{
        filas += `
            <tr onClick='mostrarDocente(${ JSON.stringify(docente) })'>
                <td>${docente.codigo}</td>
                <td>${docente.nombre}</td>
                <td>${docente.direccion}</td>
                <td>${docente.telefono}</td>
                <td>${docente.email}</td>
                <td>${docente.especialidad}</td>
                <td><button onClick='eliminarDocente(${ JSON.stringify(docente) }, event)' class="btn btn-danger btn-sm">ELIMINAR</button></td>
            </tr>
        `;
    });
    tblDocentes.innerHTML = filas;
}
function mostrarDocente(docente){
    accion = "modificar";
    idDocente = docente.idDocente;
    txtCodigoDocente.value = docente.codigo;
    txtNombreDocente.value = docente.nombre;
    txtDireccionDocente.value = docente.direccion;
    txtTelefonoDocente.value = docente.telefono;
    txtEmailDocente.value = docente.email;
    txtEspecialidadDocente.value = docente.especialidad;
}
function eliminarDocente(docente, event){
    event.preventDefault();

    if(confirm(`Esta seguro de eliminar a ${docente.nombre}`)){
        idDocente = docente.idDocente;
        accion = "eliminar";
        guardarDocentes();
    }
}