
import os
import subprocess
import re

class GestorNFS:
    """
    Clase que maneja la lógica del servidor NFS (Master).
    """

    def __init__(self):
        self.exports_file = "/etc/exports"
        self.es_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False

    def _run_command(self, command):
        try:
            if not self.es_root and not command.startswith("sudo"):
                command = f"sudo {command}"
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"success": False, "stdout": e.stdout, "stderr": e.stderr}

    def crear_y_exportar_recurso(self, carpeta, host, opciones):
        if not all([carpeta, host, opciones]):
            return {"success": False, "message": "[ERROR] Todos los campos son obligatorios."}

        # Preparación del sistema
        install_result = self._run_command("zypper install -y nfs-kernel-server")
        if not install_result["success"]:
            return {"success": False, "message": f"[ERROR] Al instalar nfs-kernel-server: {install_result['stderr']}"}
        service_result = self._run_command("systemctl enable --now nfs-server")
        if not service_result["success"] and "already enabled" not in service_result["stderr"]:
            return {"success": False, "message": f"[ERROR] Al habilitar el servicio NFS: {service_result['stderr']}"}

        # Creación del directorio
        if not os.path.exists(carpeta):
            create_result = self._run_command(f"mkdir -p {carpeta}")
            if not create_result["success"]:
                return {"success": False, "message": f"[ERROR] No se pudo crear el directorio '{carpeta}': {create_result['stderr']}"}
        perm_result = self._run_command(f"chmod ugo+rwx {carpeta}")
        if not perm_result["success"]:
            return {"success": False, "message": f"[ERROR] No se pudieron establecer los permisos para '{carpeta}': {perm_result['stderr']}"}

        # Agregar a /etc/exports
        linea_config = f"{carpeta} {host}({','.join(opciones)})"
        configs_actuales = self.leer_configuraciones()
        if linea_config in configs_actuales:
            return self.recargar_exportaciones("[INFO] La configuración ya existía. Se ha recargado.")

        try:
            command = f"echo '{linea_config}' | sudo tee -a {self.exports_file}"
            result = self._run_command(command)
            if not result["success"]:
                return {"success": False, "message": f"[ERROR] Al escribir en /etc/exports: {result['stderr']}"}
        except Exception as e:
            return {"success": False, "message": f"[ERROR] Inesperado al escribir en archivo: {e}"}

        return self.recargar_exportaciones("[OK] Configuración NFS creada y aplicada con éxito.")

    def leer_configuraciones(self):
        if not os.path.exists(self.exports_file):
            return []
        read_command = f"cat {self.exports_file}"
        result = self._run_command(read_command)
        if result["success"]:
            return [line.strip() for line in result["stdout"].splitlines() if line.strip() and not line.strip().startswith("#")]
        return []

    def eliminar_configuracion(self, linea_a_eliminar):
        try:
            # Usar sed para eliminar la línea de forma segura
            linea_escapada = re.escape(linea_a_eliminar)
            command = f"sed -i '/^{linea_escapada}$/d' {self.exports_file}"
            result = self._run_command(command)
            if result["success"]:
                return self.recargar_exportaciones("[OK] Configuración eliminada y recargada con éxito.")
            else:
                return {"success": False, "message": f"[ERROR] Al eliminar la línea: {result['stderr']}"}
        except Exception as e:
            return {"success": False, "message": f"[ERROR] Inesperado al eliminar: {e}"}

    def recargar_exportaciones(self, custom_message):
        result = self._run_command("exportfs -ra")
        if result["success"]:
            return {"success": True, "message": custom_message}
        else:
            # Si el mensaje de éxito ya se dio, pero el recargar falla, es un problema
            return {"success": False, "message": f"[ERROR] Al recargar las exportaciones: {result['stderr']}"}

    def verificar_montajes_y_disco(self):
        result = self._run_command("df -h")
        if result["success"]:
            return {"success": True, "message": "[INFO] Espacio en disco y montajes:", "data": result["stdout"]}
        else:
            return {"success": False, "message": f"[ERROR] Al obtener espacio en disco: {result['stderr']}"}

