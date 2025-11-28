# Configurador NFS

Herramienta completa para configurar y gestionar NFS (Network File System) en OpenSUSE 15.6+. Interfaz gráfica intuitiva para configurar servidores NFS y montar recursos remotos desde clientes.

## Requisitos

- OpenSUSE 15.6 o superior
- Python 3.6+
- Acceso de root (la aplicación solicita permisos automáticamente)
- Conexión de red entre servidor y cliente

## Instalación

### Opción 1: Instalación Manual

```bash
# Clonar repositorio
git clone https://github.com/anistopera/configurador-nfs.git
cd configurador-nfs

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python3 main.py
```

### Opción 2: Script de Instalación Automática

```bash
chmod +x install.sh
sudo ./install.sh
```

## Uso

1. **Ejecutar la aplicación:**
   ```bash
   python3 main.py
   ```

2. **Configurar Servidor:**
   - Ir a pestaña "Servidor"
   - Ingresar ruta de compartir y permisos
   - Configurar IP de cliente permitida
   - Hacer clic en "Agregar Configuración"

3. **Montar Recurso en Cliente:**
   - Ir a pestaña "Cliente"
   - Ingresar IP del servidor y ruta remota
   - Ingresar punto de montaje local
   - Hacer clic en "Montar Recurso NFS"

4. **Verificar Configuración:**
   - Ver exportaciones activas en sección de verificación
   - Comprobar espacio disponible en disco

## Características

✅ Configuración automática de servidor NFS
✅ Montaje de recursos remotos desde clientes
✅ Validación robusta de direcciones IP
✅ Verificación de exportaciones (exportfs -v)
✅ Monitoreo de espacio en disco
✅ Interfaz gráfica moderna con colores
✅ Detección automática de rol (Servidor/Cliente)
✅ Manejo inteligente de permisos de administrador
✅ Transferencia de archivos NFS
✅ Mensajes de error detallados

## Estructura del Proyecto

```
configurador-nfs/
├── main.py                    # Punto de entrada principal
├── gestor_nfs.py             # Lógica de servidor NFS
├── cliente_nfs.py            # Lógica de cliente NFS
├── LICENSE                   # MIT License
├── README.md                 # Este archivo
├── install.sh                # Script de instalación automática
├── ui/
│   ├── __init__.py
│   ├── ventana_principal.py  # Interfaz gráfica principal
│   └── temas.py              # Colores y estilos
└── utils/
    └── compatibilidad.py     # Funciones de compatibilidad del sistema
```

## Troubleshooting

### "Permission denied"
- La aplicación requiere permisos de root. Se relanzará automáticamente con sudo.
- Si persiste, ejecutar: `sudo python3 main.py`

### "No se pudo validar la dirección IP"
- Verificar que la IP sea válida (ej: 192.168.1.100)
- No usar espacios ni caracteres especiales

### "Recurso remoto no encontrado"
- Verificar que el servidor está ejecutando: `systemctl status nfs-server`
- Verificar exportaciones: `exportfs -v`
- Comprobar conectividad de red: `ping <IP_SERVIDOR>`

### "Punto de montaje existe"
- Usar una ruta de montaje diferente o eliminar la existente: `sudo umount /ruta/montaje`

## Licencia

MIT License - ver archivo LICENSE

## Autor

anistopera

---

**Repositorio:** https://github.com/anistopera/configurador-nfs
