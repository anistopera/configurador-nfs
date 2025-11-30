"""
Tema personalizado y configuración de estilos para la interfaz
"""
import tkinter
from tkinter import ttk

class TemaColores:
    """Configuración de colores para la interfaz"""
    
    # Colores principales
    COLOR_FONDO_PRINCIPAL = "#f0f0f0"
    COLOR_FONDO_FRAME = "#ffffff"
    COLOR_FONDO_DARK = "#2c3e50"
    
    # Colores de acentos
    COLOR_PRIMARY = "#3498db"
    COLOR_SUCCESS = "#27ae60"
    COLOR_WARNING = "#f39c12"
    COLOR_DANGER = "#e74c3c"
    COLOR_INFO = "#2980b9"
    
    # Colores de texto
    COLOR_TEXTO = "#2c3e50"
    COLOR_TEXTO_LIGHT = "#ffffff"
    COLOR_TEXTO_SECONDARY = "#7f8c8d"
    
    # Colores para elementos
    COLOR_BOTON_MASTER = "#e74c3c"
    COLOR_BOTON_CLIENTE = "#3498db"
    COLOR_BOTON_SUCCESS = "#27ae60"
    COLOR_BOTON_HOVER = "#2980b9"
    
    # Colores para listbox
    COLOR_LISTBOX_BG = "#ecf0f1"
    COLOR_LISTBOX_FG = "#2c3e50"
    COLOR_LISTBOX_SELECT = "#3498db"


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
    """
    Crea un Listbox con estilos y una Scrollbar vertical asociada.
    Devuelve una tupla (listbox, scrollbar) para ser empaquetada externamente.
    """
    listbox = tkinter.Listbox(
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
    
    scrollbar = ttk.Scrollbar(
        parent,
        orient="vertical",
        command=listbox.yview
    )
    
    listbox.config(yscrollcommand=scrollbar.set)
    
    return listbox, scrollbar

