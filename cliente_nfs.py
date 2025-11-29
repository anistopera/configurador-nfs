
import os
import subprocess
import ipaddress


class ClienteNFS:
    """
    Clase que maneja la lógica del cliente NFS.
    Valida, monta, comparte archivos y lista el contenido.
    """
    def __init__(self, punto_montaje=""):
        self.punto_montaje = punto_montaje
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

    def validar_ip(self, ip):
        """
        Valida si el string proporcionado tiene formato de IPv4 válido.
        """
        try:
            ipaddress.IPv4Address(ip)
            return True
        except (ipaddress.AddressValueError, ValueError):
            return False

    def montar_recurso(self, ip_master, ruta_remota):
        """Crea el punto de montaje y monta el recurso NFS."""
        if not self.punto_montaje:
            return {"success": False, "message": "[ERROR] El punto de montaje no puede estar vacío."}
        if not self.validar_ip(ip_master):
            return {"success": False, "message": f"[ERROR] Formato de IP inválido: '{ip_master}'."}

        if not os.path.exists(self.punto_montaje):
            create_dir_result = self._run_command(f"mkdir -p {self.punto_montaje}")
            if not create_dir_result["success"]:
                return {"success": False, "message": f"[ERROR] Al crear punto de montaje: {create_dir_result['stderr']}"}
        
        if os.path.ismount(self.punto_montaje):
            return {"success": True, "message": f"[INFO] El recurso ya estaba montado en {self.punto_montaje}."}
        
        mount_command = f"mount -t nfs {ip_master}:{ruta_remota} {self.punto_montaje}"
        mount_result = self._run_command(mount_command)

        if not mount_result["success"]:
            stderr = mount_result["stderr"].lower()
            if "connection refused" in stderr or "no route" in stderr:
                return {"success": False, "message": f"[ERROR] IP inaccesible o servidor NFS no disponible ({ip_master})"}
            elif "permission denied" in stderr or "access denied" in stderr:
                return {"success": False, "message": "[ERROR] Acceso denegado por el servidor NFS"}
            else:
                return {"success": False, "message": f"[ERROR] Al montar el recurso: {mount_result['stderr']}"}

        return {"success": True, "message": f"[OK] Recurso montado con éxito en {self.punto_montaje}."}

    def compartir_archivos(self, archivos_a_copiar):
        """Copia una lista de archivos al punto de montaje y reporta el resultado."""
        if not os.path.ismount(self.punto_montaje):
             return {"success": False, "message": "[ERROR] El recurso no está montado. Monta el recurso primero."}

        exitos = 0
        fallos = 0
        archivos_fallidos = []

        for archivo in archivos_a_copiar:
            command = f"cp \"{archivo}\" \"{self.punto_montaje}/\""
            result = self._run_command(command)
            if result["success"]:
                exitos += 1
            else:
                fallos += 1
                nombre_archivo = os.path.basename(archivo)
                stderr = result["stderr"].lower()
                
                if "permission denied" in stderr:
                    archivos_fallidos.append(f"{nombre_archivo} (Permiso denegado)")
                elif "no such file" in stderr:
                    archivos_fallidos.append(f"{nombre_archivo} (No encontrado)")
                elif "is a directory" in stderr:
                    archivos_fallidos.append(f"{nombre_archivo} (Es un directorio)")
                else:
                    archivos_fallidos.append(f"{nombre_archivo} (Error: {result['stderr'].strip()})")
        
        informe = f"[ÉXITO] Se compartieron {exitos} archivo(s).\n"
        if fallos > 0:
            informe += f"[FALLO] No se pudieron compartir {fallos} archivo(s):\n"
            informe += "\n".join([f" - {f}" for f in archivos_fallidos])
        
        return {"success": exitos > 0, "message": informe}

    def listar_contenido(self):
        """Lista el contenido del punto de montaje."""
        if not os.path.ismount(self.punto_montaje):
            return {"success": False, "message": "[ERROR] El recurso no está montado."}
        
        list_result = self._run_command(f"ls -lA {self.punto_montaje}")
        if list_result["success"]:
            return {"success": True, "message": "[INFO] Contenido del recurso compartido:", "data": list_result["stdout"]}
        else:
            return {"success": False, "message": f"[ERROR] Al listar el contenido: {list_result['stderr']}"}

    def desmontar_recurso(self):
        """Desmonta el recurso NFS del sistema."""
        if not os.path.ismount(self.punto_montaje):
            return {"success": True, "message": "[INFO] El recurso no estaba montado."}

        umount_result = self._run_command(f"umount {self.punto_montaje}")
        if umount_result["success"]:
            return {"success": True, "message": "[OK] Recurso desmontado con éxito."}
        else:
            stderr = umount_result['stderr'].lower()
            if "target is busy" in stderr or "device is busy" in stderr:
                return {"success": False, "message": f"[ERROR] No se pudo desmontar: el recurso está en uso."}
            return {"success": False, "message": f"[ERROR] Al desmontar: {umount_result['stderr']}"}
