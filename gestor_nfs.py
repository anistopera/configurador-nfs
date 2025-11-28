
import os
import subprocess
import re


class GestorNFS:
    """
    Clase que maneja la lógica del servidor NFS (Master).
    Instala, configura y gestiona las exportaciones NFS.
    """

    def __init__(self):
        self.exports_file = "/etc/exports"
        self.es_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False

    def _run_command(self, command):
        """
        Ejecuta un comando en el sistema y devuelve el resultado.
        Si está en root, ejecuta directamente sin sudo.
        Si no está en root, agrega sudo antes del comando.
        """
        try:
            # Si no es root y el comando no tiene sudo, agregarlo
            if not self.es_root and not command.startswith("sudo"):
                command = f"sudo {command}"
            
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"success": False, "stdout": e.stdout, "stderr": e.stderr}

    def preparar_sistema(self):
        """Instala nfs-kernel-server y habilita el servicio."""
        print("Paso 1: Instalando nfs-kernel-server...")
        install_result = self._run_command("zypper install -y nfs-kernel-server")
        if not install_result["success"]:
            return {"success": False, "message": f"✗ Error al instalar nfs-kernel-server: {install_result['stderr']}"}

        print("Paso 2: Habilitando y iniciando el servicio nfs-server...")
        service_result = self._run_command("systemctl enable --now nfs-server")
        if not service_result["success"]:
            if "already enabled" not in service_result["stderr"]:
                 return {"success": False, "message": f"✗ Error al habilitar el servicio: {service_result['stderr']}"}

        return {"success": True, "message": "✓ El sistema está listo para operar como servidor NFS."}

    def crear_y_preparar_directorio(self, path="/opt/data"):
        """Crea el directorio a compartir y le asigna permisos 777."""
        print(f"Creando y configurando directorio: {path}")
        if not os.path.exists(path):
            create_result = self._run_command(f"mkdir -p {path}")
            if not create_result["success"]:
                return {"success": False, "message": f"✗ No se pudo crear el directorio: {create_result['stderr']}"}

        # Establecer permisos ugo+rw (equivalente a 666 para archivos, pero respetando umask)
        perm_result = self._run_command(f"chmod ugo+rw {path}")
        if not perm_result["success"]:
            return {"success": False, "message": f"✗ No se pudieron establecer los permisos: {perm_result['stderr']}"}

        return {"success": True, "message": f"✓ Directorio {path} listo con permisos de lectura/escritura."}

    def leer_configuraciones(self):
        """Lee las configuraciones actuales del archivo /etc/exports."""
        if not os.path.exists(self.exports_file):
            return []
        try:
            with open(self.exports_file, "r") as f:
                return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        except IOError:
            return []

    def agregar_configuracion(self, carpeta, host, opciones):
        """Agrega una nueva configuración al archivo /etc/exports."""
        if not all([carpeta, host, opciones]):
            return {"success": False, "message": "✗ Todos los campos son obligatorios."}

        linea_config = f"{carpeta} {host}({','.join(opciones)})"
        
        configs_actuales = self.leer_configuraciones()
        if linea_config in configs_actuales:
            return {"success": False, "message": "✗ Esta configuración ya existe."}

        try:
            command = f"echo \"{linea_config}\" | tee -a {self.exports_file}"
            result = self._run_command(command)
            if result["success"]:
                 return self.recargar_exportaciones()
            else:
                return {"success": False, "message": f"✗ Error al escribir en /etc/exports: {result['stderr']}"}
        except Exception as e:
            return {"success": False, "message": f"✗ Error inesperado: {e}"}

    def eliminar_configuracion(self, linea_a_eliminar):
        """Elimina una configuración del archivo /etc/exports."""
        try:
            # Escapamos la línea completa para que sed la interprete literalmente.
            linea_escapada = re.escape(linea_a_eliminar)

            # Usamos '#' como delimitador en sed para evitar conflictos con las rutas '/'.
            command = f"sed -i '\#^{linea_escapada}$#d' {self.exports_file}"
            result = self._run_command(command)
            
            if result["success"]:
                return self.recargar_exportaciones()
            else:
                return {"success": False, "message": f"✗ Error al eliminar la línea: {result['stderr']}"}
        except Exception as e:
            return {"success": False, "message": f"✗ Error inesperado al eliminar: {e}"}

    def recargar_exportaciones(self):
        """Aplica los cambios ejecutando exportfs -ra."""
        print("Recargando todas las exportaciones NFS...")
        result = self._run_command("exportfs -ra")
        if result["success"]:
            return {"success": True, "message": "✓ Configuración NFS recargada y aplicada con éxito."}
        else:
            return {"success": False, "message": f"✗ Error al recargar las exportaciones: {result['stderr']}"}

    def verificar_exportaciones(self):
        """
        Ejecuta 'exportfs -v' para mostrar las exportaciones activas.
        Devuelve la salida para verificación.
        """
        result = self._run_command("exportfs -v")
        if result["success"]:
            return {"success": True, "message": "📋 Exportaciones NFS activas:", "data": result["stdout"]}
        else:
            return {"success": False, "message": f"✗ Error al obtener exportaciones: {result['stderr']}"}

    def verificar_espacio_disco(self):
        """
        Ejecuta 'df -h' para mostrar el espacio en disco disponible.
        Devuelve la salida para verificación.
        """
        result = self._run_command("df -h")
        if result["success"]:
            return {"success": True, "message": "💾 Espacio en disco disponible:", "data": result["stdout"]}
        else:
            return {"success": False, "message": f"✗ Error al obtener espacio en disco: {result['stderr']}"}
