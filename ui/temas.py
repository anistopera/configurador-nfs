"""
Tema personalizado y configuración de estilos para la interfaz
"""

class TemaColores:
    """Configuración de colores para la interfaz"""
    
    # Colores principales
    COLOR_FONDO_PRINCIPAL = "#f0f0f0"      # Gris claro
    COLOR_FONDO_FRAME = "#ffffff"          # Blanco
    COLOR_FONDO_DARK = "#2c3e50"           # Azul oscuro
    
    # Colores de acentos
    COLOR_PRIMARY = "#3498db"              # Azul
    COLOR_SUCCESS = "#27ae60"              # Verde
    COLOR_WARNING = "#f39c12"              # Naranja
    COLOR_DANGER = "#e74c3c"               # Rojo
    COLOR_INFO = "#2980b9"                 # Azul oscuro
    
    # Colores de texto
    COLOR_TEXTO = "#2c3e50"                # Texto oscuro
    COLOR_TEXTO_LIGHT = "#ffffff"          # Texto claro
    COLOR_TEXTO_SECONDARY = "#7f8c8d"      # Texto gris
    
    # Colores para elementos
    COLOR_BOTON_MASTER = "#e74c3c"         # Rojo (Master)
    COLOR_BOTON_CLIENTE = "#3498db"        # Azul (Cliente)
    COLOR_BOTON_SUCCESS = "#27ae60"        # Verde (Éxito)
    COLOR_BOTON_HOVER = "#2980b9"          # Hover
    
    # Colores para listbox
    COLOR_LISTBOX_BG = "#ecf0f1"           # Gris muy claro
    COLOR_LISTBOX_FG = "#2c3e50"           # Texto oscuro
    COLOR_LISTBOX_SELECT = "#3498db"       # Selección azul


def crear_estilo_buttons(root):
    """Crea estilos personalizados para botones"""
    style_dict = {
        'font': ('Segoe UI', 10, 'bold'),
        'padx': 15,
        'pady': 8,
        'relief': 'solid',
        'bd': 0,
        'cursor': 'hand2',
    }
    return style_dict


def crear_listbox_personalizado(parent, **kwargs):
    """Crea un Listbox con estilos personalizados"""
    listbox = __import__('tkinter').Listbox(
        parent,
        bg=TemaColores.COLOR_LISTBOX_BG,
        fg=TemaColores.COLOR_LISTBOX_FG,
        selectbackground=TemaColores.COLOR_LISTBOX_SELECT,
        selectforeground=TemaColores.COLOR_TEXTO_LIGHT,
        font=('Consolas', 9),
        relief='flat',
        bd=1,
        **kwargs
    )
    return listbox
