
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
        """
        try:
            if not self.es_root and not command.startswith("sudo"):
                command = f"sudo {command}"
            
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            return {"success": True, "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.CalledProcessError as e:
            return {"success": False, "stdout": e.stdout, "stderr": e.stderr}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e)}

    def crear_y_exportar_recurso(self, carpeta, host, opciones):
        """
        Método consolidado que prepara el sistema, crea el directorio,
        lo agrega a /etc/exports y recarga la configuración.
        """
        if not all([carpeta, host, opciones]):
            return {"success": False, "message": "✗ Todos los campos son obligatorios."}

        # Paso 1: Preparar el sistema (Instalar y habilitar NFS)
        print("Paso 1: Instalando y habilitando NFS si es necesario...")
        install_result = self._run_command("zypper install -y nfs-kernel-server")
        if not install_result["success"]:
            return {"success": False, "message": f"✗ Error al instalar nfs-kernel-server: {install_result['stderr']}"}
        
        service_result = self._run_command("systemctl enable --now nfs-server")
        if not service_result["success"] and "already enabled" not in service_result["stderr"]:
            return {"success": False, "message": f"✗ Error al habilitar el servicio NFS: {service_result['stderr']}"}
        print("✓ Sistema NFS preparado.")

        # Paso 2: Crear y preparar el directorio
        print(f"Paso 2: Creando y configurando directorio: {carpeta}")
        if not os.path.exists(carpeta):
            create_result = self._run_command(f"mkdir -p {carpeta}")
            if not create_result["success"]:
                return {"success": False, "message": f"✗ No se pudo crear el directorio '{carpeta}': {create_result['stderr']}"}

        perm_result = self._run_command(f"chmod ugo+rwx {carpeta}")
        if not perm_result["success"]:
            return {"success": False, "message": f"✗ No se pudieron establecer los permisos para '{carpeta}': {perm_result['stderr']}"}
        print(f"✓ Directorio '{carpeta}' preparado.")

        # Paso 3: Agregar la configuración a /etc/exports
        print(f"Paso 3: Agregando configuración a {self.exports_file}")
        linea_config = f"{carpeta} {host}({','.join(opciones)})"
        
        configs_actuales = self.leer_configuraciones()
        if linea_config in configs_actuales:
            print("✓ La configuración ya existía. Recargando para asegurar estado.")
            return self.recargar_exportaciones()

        try:
            command = f"echo '{linea_config}' | sudo tee -a {self.exports_file}"
            result = self._run_command(command)
            if not result["success"]:
                return {"success": False, "message": f"✗ Error al escribir en /etc/exports: {result['stderr']}"}
        except Exception as e:
            return {"success": False, "message": f"✗ Error inesperado al escribir en archivo: {e}"}
        print("✓ Configuración agregada.")

        # Paso 4: Recargar las exportaciones de NFS
        return self.recargar_exportaciones()

    def leer_configuraciones(self):
        """Lee las configuraciones actuales del archivo /etc/exports."""
        if not os.path.exists(self.exports_file):
            return []
        try:
            read_command = f"cat {self.exports_file}"
            result = self._run_command(read_command)
            if result["success"]:
                return [line.strip() for line in result["stdout"].splitlines() if line.strip() and not line.strip().startswith("#")]
            else:
                return []
        except IOError:
            return []

    def eliminar_configuracion(self, linea_a_eliminar):
        """Elimina una configuración del archivo /etc/exports."""
        try:
            linea_escapada = re.escape(linea_a_eliminar)
            command = f"sed -i '/^{linea_escapada}$/d' {self.exports_file}"
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
        """Ejecuta 'exportfs -v' para mostrar las exportaciones activas."""
        result = self._run_command("exportfs -v")
        if result["success"]:
            return {"success": True, "message": "📋 Exportaciones NFS activas:", "data": result["stdout"]}
        else:
            return {"success": False, "message": f"✗ Error al obtener exportaciones: {result['stderr']}"}

    def verificar_espacio_disco(self):
        """Ejecuta 'df -h' para mostrar el espacio en disco disponible."""
        result = self._run_command("df -h")
        if result["success"]:
            return {"success": True, "message": "💾 Espacio en disco disponible:", "data": result["stdout"]}
        else:
            return {"success": False, "message": f"✗ Error al obtener espacio en disco: {result['stderr']}"}

