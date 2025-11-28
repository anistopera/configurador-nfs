#!/usr/bin/env python3
"""
Configurador Integral NFS para OpenSUSE
Punto de entrada de la aplicación
"""

import sys
import os
import tkinter as tk
from utils.compatibilidad import (
    verificar_compatibilidad, 
    verificar_permisos_administrador,
    relanzar_con_sudo
)

# Agregar ruta de módulos locales
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Función principal de la aplicación"""
    
    # Verificar compatibilidad del sistema
    if not verificar_compatibilidad():
        print("✗ Sistema no compatible. Se requiere Linux con NFS.")
        sys.exit(1)
    
    # Verificar permisos de root
    if not verificar_permisos_administrador():
        print("⚠ Relanzando con permisos de root...")
        relanzar_con_sudo()
        sys.exit(0)
    
    print("✓ Sistema compatible")
    print("✓ Permisos de root verificados")
    
    # Importar e inicializar GUI
    from ui.ventana_principal import VentanaPrincipal
    
    root = tk.Tk()
    app = VentanaPrincipal(root)
    
    print("🚀 Iniciando interfaz gráfica...")
    root.mainloop()


if __name__ == "__main__":
    main()
