import os
import sys
import subprocess


def verificar_compatibilidad():
    """
    Verifica si el sistema es compatible (Linux con NFS)
    """
    try:
        if os.path.exists("/etc/exports"):
            print("✓ Archivo /etc/exports encontrado")
            return True
        else:
            print("⚠ Advertencia: Archivo /etc/exports no encontrado (Sistema NFS no instalado)")
            return False
            
    except Exception as error:
        print(f"✗ Error verificando compatibilidad: {error}")
        return False  


def verificar_permisos_administrador():
    """
    Verifica si la aplicación tiene permisos de administrador (root).
    Si no está en root, intenta relanzarse con sudo.
    """
    try:
        # Verificar si ya es root
        if os.geteuid() == 0:
            return True
        else:
            print("⚠ Se requieren permisos de administrador (root).")
            print("Intenta relanzar la aplicación con: sudo python3 <script>")
            return False
    except AttributeError:
        # En Windows o sistemas sin geteuid
        return True


def relanzar_con_sudo():
    """
    Si no se está ejecutando como root, relanza el script con sudo.
    Útil para ejecutar la GUI con permisos de root.
    """
    try:
        if os.geteuid() != 0:
            print("🔄 Relanzando aplicación con permisos de root...")
            # Relanzar el script con sudo
            os.execvp("sudo", ["sudo"] + sys.argv)
    except (AttributeError, OSError):
        # En Windows o si falla execvp, no hacer nada
        pass


def es_servidor_master():
    """
    Detecta automáticamente si esta máquina es el Servidor Master.
    Lee /etc/exports y verifica si hay líneas de exportación configuradas.
    """
    try:
        exports_file = "/etc/exports"
        if not os.path.exists(exports_file):
            return False
        
        with open(exports_file, "r") as f:
            lineas = [line.strip() for line in f 
                     if line.strip() and not line.strip().startswith("#")]
        
        # Si hay configuraciones, es Master
        return len(lineas) > 0
    except Exception as e:
        print(f"Error detectando rol de servidor: {e}")
        return False

        
