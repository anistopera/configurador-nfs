import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gestor_nfs import GestorNFS
from cliente_nfs import ClienteNFS
from utils.compatibilidad import es_servidor_master, verificar_permisos_administrador
from .temas import TemaColores, crear_listbox_personalizado


class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurador Integral NFS (Master & Cliente)")
        self.root.geometry("1000x750")
        self.root.configure(bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        
        # Configurar estilo ttk
        self._configurar_estilos()

        # Verificar permisos de root
        if not verificar_permisos_administrador():
            messagebox.showerror("Error", "Se requieren permisos de administrador (root).\nEjecuta: sudo python3 main.py")
            self.root.quit()
            return

        # Inicializar backends
        self.gestor_nfs = GestorNFS()
        self.cliente_nfs = ClienteNFS()
        
        # Detectar automáticamente si es servidor Master
        self.es_servidor_master = es_servidor_master()

        # Crear frame superior con título
        self._crear_frame_titulo()

        # Crear el panel de pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Crear las pestañas
        self.frame_master = ttk.Frame(self.notebook, padding="10")
        self.frame_cliente = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.frame_master, text='Servidor (Master)')
        self.notebook.add(self.frame_cliente, text='Cliente')

        # Construir la interfaz de cada pestaña
        self._crear_widgets_master()
        self._crear_widgets_cliente()
        
        # Mostrar estado de la máquina
        estado = "SERVIDOR MASTER DETECTADO" if self.es_servidor_master else "MODO CLIENTE"
        messagebox.showinfo("Información", f"Estado de la máquina:\n{estado}")

    def _configurar_estilos(self):
        """Configura los estilos de la aplicación"""
        style = ttk.Style()
        
        # Tema general
        style.theme_use('clam')
        
        # Colores para LabelFrame
        style.configure('TLabelframe', background=TemaColores.COLOR_FONDO_PRINCIPAL, 
                       foreground=TemaColores.COLOR_TEXTO)
        style.configure('TLabelframe.Label', background=TemaColores.COLOR_FONDO_PRINCIPAL,
                       foreground=TemaColores.COLOR_PRIMARY, font=('Segoe UI', 10, 'bold'))
        
        # Colores para botones
        style.configure('TButton', font=('Segoe UI', 9))
        style.map('TButton', background=[('active', TemaColores.COLOR_BOTON_HOVER)])
        
        # Colores para labels
        style.configure('TLabel', background=TemaColores.COLOR_FONDO_PRINCIPAL,
                       foreground=TemaColores.COLOR_TEXTO, font=('Segoe UI', 9))
        
        # Colores para entry
        style.configure('TEntry', fieldbackground='white', foreground=TemaColores.COLOR_TEXTO)
        
        # Colores para notebook
        style.configure('TNotebook', background=TemaColores.COLOR_FONDO_PRINCIPAL)
        style.configure('TNotebook.Tab', padding=[20, 10])

    def _crear_frame_titulo(self):
        """Crea un frame de título atractivo"""
        titulo_frame = tk.Frame(self.root, bg=TemaColores.COLOR_FONDO_DARK, height=60)
        titulo_frame.pack(side="top", fill="x")
        titulo_frame.pack_propagate(False)
        
        titulo_label = tk.Label(
            titulo_frame,
            text="NFS Configurador Integral",
            bg=TemaColores.COLOR_FONDO_DARK,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 16, 'bold'),
            pady=10
        )
        titulo_label.pack()
        
        subtitulo_label = tk.Label(
            titulo_frame,
            text="Gestión de Servidor Master y Cliente NFS para OpenSUSE",
            bg=TemaColores.COLOR_FONDO_DARK,
            fg=TemaColores.COLOR_TEXTO_SECONDARY,
            font=('Segoe UI', 9)
        )
        subtitulo_label.pack()

    def _crear_widgets_master(self):
        """Crea los widgets de la sección Master"""
        # --- Frame de preparación del sistema ---
        prep_frame = ttk.LabelFrame(self.frame_master, text="1. Preparación del Sistema Master", padding="15")
        prep_frame.pack(fill="x", expand="no", padx=5, pady=8)

        btn_preparar_sistema = tk.Button(
            prep_frame, 
            text="Instalar y Habilitar NFS",
            command=self._preparar_sistema_master,
            bg=TemaColores.COLOR_BOTON_MASTER,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 10, 'bold'),
            padx=15, pady=8,
            relief='solid', bd=0,
            cursor='hand2'
        )
        btn_preparar_sistema.pack(side="left", padx=8)

        btn_crear_dir = tk.Button(
            prep_frame,
            text="Crear /opt/data con Permisos",
            command=self._crear_directorio_master,
            bg=TemaColores.COLOR_BOTON_SUCCESS,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 10, 'bold'),
            padx=15, pady=8,
            relief='solid', bd=0,
            cursor='hand2'
        )
        btn_crear_dir.pack(side="left", padx=8)

        # --- Frame de formulario de exportación ---
        form_frame = ttk.LabelFrame(self.frame_master, text="2. Formulario de Exportación", padding="15")
        form_frame.pack(fill="x", expand="no", padx=5, pady=8)

        ttk.Label(form_frame, text="Carpeta a Exportar:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.master_carpeta_var = tk.StringVar(value="/opt/data")
        carpeta_entry = ttk.Entry(form_frame, textvariable=self.master_carpeta_var, width=35)
        carpeta_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Host/Clientes:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.master_host_var = tk.StringVar(value="*")
        host_entry = ttk.Entry(form_frame, textvariable=self.master_host_var, width=35)
        host_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        # Opciones con Checkbuttons
        opciones_frame = ttk.LabelFrame(form_frame, text="Opciones", padding="10")
        opciones_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10, padx=5)
        
        self.opciones_vars = {
            "rw": tk.BooleanVar(value=True),
            "sync": tk.BooleanVar(value=True),
            "root_squash": tk.BooleanVar(value=True),
            "no_root_squash": tk.BooleanVar(),
        }
        
        col = 0
        for opt, var in self.opciones_vars.items():
            ttk.Checkbutton(opciones_frame, text=opt, variable=var).grid(row=0, column=col, padx=10)
            col += 1

        btn_agregar = tk.Button(
            form_frame,
            text="Agregar y Aplicar",
            command=self._agregar_exportacion_master,
            bg=TemaColores.COLOR_BOTON_SUCCESS,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 10, 'bold'),
            padx=15, pady=8,
            relief='solid', bd=0,
            cursor='hand2'
        )
        btn_agregar.grid(row=0, column=2, rowspan=2, padx=15, sticky="ns")

        form_frame.columnconfigure(1, weight=1)

        # --- Frame de configuraciones actuales ---
        configs_frame = ttk.LabelFrame(self.frame_master, text="3. Configuraciones Activas (/etc/exports)", padding="15")
        configs_frame.pack(fill="both", expand="yes", padx=5, pady=8)

        self.lista_configs_master = crear_listbox_personalizado(configs_frame, height=6)
        self.lista_configs_master.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        scrollbar = ttk.Scrollbar(configs_frame, orient="vertical", command=self.lista_configs_master.yview)
        scrollbar.pack(side="right", fill="y")
        self.lista_configs_master.config(yscrollcommand=scrollbar.set)
        
        btn_frame = tk.Frame(configs_frame, bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        btn_frame.pack(side="left", fill="y", padx=5)
        
        btn_refrescar = tk.Button(
            btn_frame,
            text="Refrescar",
            command=self._refrescar_lista_master,
            bg=TemaColores.COLOR_PRIMARY,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 9, 'bold'),
            width=12,
            relief='solid', bd=0
        )
        btn_refrescar.pack(pady=5)
        
        btn_eliminar = tk.Button(
            btn_frame,
            text="Eliminar",
            command=self._eliminar_exportacion_master,
            bg=TemaColores.COLOR_DANGER,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 9, 'bold'),
            width=12,
            relief='solid', bd=0
        )
        btn_eliminar.pack(pady=5)

        # --- Frame de verificación ---
        verif_frame = ttk.LabelFrame(self.frame_master, text="4. Verificación y Diagnóstico", padding="15")
        verif_frame.pack(fill="x", expand="no", padx=5, pady=8)
        
        btn_verificar_exp = tk.Button(
            verif_frame,
            text="Exportaciones Activas",
            command=self._verificar_exportaciones_master,
            bg=TemaColores.COLOR_INFO,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 10, 'bold'),
            padx=15, pady=8,
            relief='solid', bd=0,
            cursor='hand2'
        )
        btn_verificar_exp.pack(side="left", padx=8)
        
        btn_verificar_disco = tk.Button(
            verif_frame,
            text="Espacio en Disco",
            command=self._verificar_disco_master,
            bg=TemaColores.COLOR_WARNING,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 10, 'bold'),
            padx=15, pady=8,
            relief='solid', bd=0,
            cursor='hand2'
        )
        btn_verificar_disco.pack(side="left", padx=8)

        self._refrescar_lista_master()

    def _crear_widgets_cliente(self):
        """Crea los widgets de la sección Cliente"""
        # --- Frame de montaje ---
        montaje_frame = ttk.LabelFrame(self.frame_cliente, text="1. Configuración del Cliente y Montaje", padding="15")
        montaje_frame.pack(fill="x", expand="no", padx=5, pady=8)

        ttk.Label(montaje_frame, text="IP del Master:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.cliente_ip_var = tk.StringVar()
        ip_entry = ttk.Entry(montaje_frame, textvariable=self.cliente_ip_var, width=25)
        ip_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(montaje_frame, text="Ruta Remota:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.cliente_ruta_remota_var = tk.StringVar(value="/opt/data")
        ruta_entry = ttk.Entry(montaje_frame, textvariable=self.cliente_ruta_remota_var, width=25)
        ruta_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(montaje_frame, text="Punto de Montaje:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.cliente_punto_montaje_var = tk.StringVar(value=self.cliente_nfs.punto_montaje)
        punto_entry = ttk.Entry(montaje_frame, textvariable=self.cliente_punto_montaje_var, state="readonly", width=25)
        punto_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        btn_montar = tk.Button(
            montaje_frame,
            text="Montar",
            command=self._montar_recurso_cliente,
            bg=TemaColores.COLOR_BOTON_SUCCESS,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 10, 'bold'),
            padx=15, pady=8,
            relief='solid', bd=0,
            cursor='hand2'
        )
        btn_montar.grid(row=0, column=2, rowspan=2, padx=15, sticky="ns")
        
        btn_desmontar = tk.Button(
            montaje_frame,
            text="Desmontar",
            command=self._desmontar_recurso_cliente,
            bg=TemaColores.COLOR_WARNING,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 10, 'bold'),
            padx=15, pady=8,
            relief='solid', bd=0,
            cursor='hand2'
        )
        btn_desmontar.grid(row=2, column=2, padx=15, sticky="ns")

        montaje_frame.columnconfigure(1, weight=1)

        # --- Frame de compartir archivos ---
        share_frame = ttk.LabelFrame(self.frame_cliente, text="2. Compartir Archivos", padding="15")
        share_frame.pack(fill="x", expand="no", padx=5, pady=8)

        btn_seleccionar = tk.Button(
            share_frame,
            text="Seleccionar Archivos para Compartir",
            command=self._compartir_archivos_cliente,
            bg=TemaColores.COLOR_PRIMARY,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 10, 'bold'),
            padx=20, pady=10,
            relief='solid', bd=0,
            cursor='hand2'
        )
        btn_seleccionar.pack()

        # --- Frame de resultados y listado ---
        result_frame = ttk.LabelFrame(self.frame_cliente, text="3. Contenido del Recurso y Notificaciones", padding="15")
        result_frame.pack(fill="both", expand="yes", padx=5, pady=8)

        self.texto_resultados_cliente = tk.Text(
            result_frame,
            height=12,
            wrap="word",
            bg="#ecf0f1",
            fg=TemaColores.COLOR_TEXTO,
            font=('Consolas', 9),
            relief='flat',
            bd=1
        )
        self.texto_resultados_cliente.pack(fill="both", expand=True, padx=(0, 5), pady=(0, 5))
        
        scrollbar_res = ttk.Scrollbar(result_frame, command=self.texto_resultados_cliente.yview)
        self.texto_resultados_cliente.config(yscrollcommand=scrollbar_res.set)
        scrollbar_res.pack(side="right", fill="y")
        
        btn_listar = tk.Button(
            result_frame,
            text="Listar Contenido del Recurso",
            command=self._listar_contenido_cliente,
            bg=TemaColores.COLOR_INFO,
            fg=TemaColores.COLOR_TEXTO_LIGHT,
            font=('Segoe UI', 10, 'bold'),
            padx=15, pady=8,
            relief='solid', bd=0,
            cursor='hand2'
        )
        btn_listar.pack(pady=10)

    # --- Lógica de los botones MASTER ---
    def _preparar_sistema_master(self):
        res = self.gestor_nfs.preparar_sistema()
        messagebox.showinfo("Resultado", res["message"])

    def _crear_directorio_master(self):
        res = self.gestor_nfs.crear_y_preparar_directorio(self.master_carpeta_var.get())
        messagebox.showinfo("Resultado", res["message"])

    def _refrescar_lista_master(self):
        self.lista_configs_master.delete(0, tk.END)
        for config in self.gestor_nfs.leer_configuraciones():
            self.lista_configs_master.insert(tk.END, config)

    def _agregar_exportacion_master(self):
        carpeta = self.master_carpeta_var.get()
        host = self.master_host_var.get()
        opts = [opt for opt, var in self.opciones_vars.items() if var.get()]
        res = self.gestor_nfs.agregar_configuracion(carpeta, host, opts)
        messagebox.showinfo("Resultado", res["message"])
        if res["success"]:
            self._refrescar_lista_master()

    def _eliminar_exportacion_master(self):
        seleccion = self.lista_configs_master.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una configuración de la lista para eliminar.")
            return
        config_a_eliminar = self.lista_configs_master.get(seleccion[0])
        if messagebox.askyesno("Confirmar", f"¿Seguro que quieres eliminar esta exportación?\n\n{config_a_eliminar}"):
            res = self.gestor_nfs.eliminar_configuracion(config_a_eliminar)
            messagebox.showinfo("Resultado", res["message"])
            if res["success"]:
                self._refrescar_lista_master()

    def _verificar_exportaciones_master(self):
        res = self.gestor_nfs.verificar_exportaciones()
        if res["success"]:
            ventana_verif = tk.Toplevel(self.root)
            ventana_verif.title("Exportaciones Activas (exportfs -v)")
            ventana_verif.geometry("700x450")
            ventana_verif.configure(bg=TemaColores.COLOR_FONDO_PRINCIPAL)
            
            titulo = tk.Label(
                ventana_verif,
                text="Exportaciones NFS Activas",
                bg=TemaColores.COLOR_FONDO_DARK,
                fg=TemaColores.COLOR_TEXTO_LIGHT,
                font=('Segoe UI', 12, 'bold'),
                pady=10
            )
            titulo.pack(fill="x")
            
            texto = tk.Text(
                ventana_verif,
                bg="#ecf0f1",
                fg=TemaColores.COLOR_TEXTO,
                font=('Consolas', 9),
                relief='flat',
                bd=1
            )
            texto.pack(fill="both", expand=True, padx=10, pady=10)
            texto.insert("1.0", f"{res['message']}\n\n{res['data']}")
            texto.config(state="disabled")
        else:
            messagebox.showerror("Error", res["message"])

    def _verificar_disco_master(self):
        res = self.gestor_nfs.verificar_espacio_disco()
        if res["success"]:
            ventana_verif = tk.Toplevel(self.root)
            ventana_verif.title("Espacio en Disco (df -h)")
            ventana_verif.geometry("700x450")
            ventana_verif.configure(bg=TemaColores.COLOR_FONDO_PRINCIPAL)
            
            titulo = tk.Label(
                ventana_verif,
                text="Espacio en Disco Disponible",
                bg=TemaColores.COLOR_FONDO_DARK,
                fg=TemaColores.COLOR_TEXTO_LIGHT,
                font=('Segoe UI', 12, 'bold'),
                pady=10
            )
            titulo.pack(fill="x")
            
            texto = tk.Text(
                ventana_verif,
                bg="#ecf0f1",
                fg=TemaColores.COLOR_TEXTO,
                font=('Consolas', 9),
                relief='flat',
                bd=1
            )
            texto.pack(fill="both", expand=True, padx=10, pady=10)
            texto.insert("1.0", f"{res['message']}\n\n{res['data']}")
            texto.config(state="disabled")
        else:
            messagebox.showerror("Error", res["message"])

    # --- Lógica de los botones CLIENTE ---
    def _montar_recurso_cliente(self):
        ip = self.cliente_ip_var.get()
        ruta_remota = self.cliente_ruta_remota_var.get()
        res = self.cliente_nfs.montar_recurso(ip, ruta_remota)
        self._actualizar_resultados_cliente(res)
        
    def _desmontar_recurso_cliente(self):
        res = self.cliente_nfs.desmontar_recurso()
        self._actualizar_resultados_cliente(res)

    def _compartir_archivos_cliente(self):
        archivos = filedialog.askopenfilenames(title="Selecciona archivos para copiar al recurso NFS")
        if not archivos:
            return
        res = self.cliente_nfs.compartir_archivos(archivos)
        self._actualizar_resultados_cliente(res)

    def _listar_contenido_cliente(self):
        res = self.cliente_nfs.listar_contenido()
        if res.get("data"):
             self._actualizar_resultados_cliente({"message": res["message"] + "\n\n" + res["data"]})
        else:
             self._actualizar_resultados_cliente(res)

    def _actualizar_resultados_cliente(self, resultado):
        self.texto_resultados_cliente.config(state="normal")
        self.texto_resultados_cliente.delete("1.0", tk.END)
        self.texto_resultados_cliente.insert("1.0", resultado.get("message", "Acción completada."))
        self.texto_resultados_cliente.config(state="disabled")
