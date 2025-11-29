import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gestor_nfs import GestorNFS
from cliente_nfs import ClienteNFS
from utils.compatibilidad import es_servidor_master, verificar_permisos_administrador
from .temas import TemaColores, crear_listbox_personalizado

class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Configurador NFS para OpenSUSE")
        self.root.geometry("1000x750")
        self.root.configure(bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        
        self._configurar_estilos()

        if not verificar_permisos_administrador():
            messagebox.showerror("Error de Permisos", "Se requieren permisos de administrador (root).")
            self.root.quit()
            return

        self.gestor_nfs = GestorNFS()
        self.cliente_nfs = ClienteNFS()
        self.es_servidor_master = es_servidor_master()

        self._crear_frame_titulo()
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.frame_master = ttk.Frame(self.notebook, padding="10")
        self.frame_cliente = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.frame_master, text='Servidor (Master)')
        self.notebook.add(self.frame_cliente, text='Compartir Archivos')

        self._crear_widgets_master()
        self._crear_widgets_cliente()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Segoe UI', 10))
        style.configure('TLabelframe', background=TemaColores.COLOR_FONDO_PRINCIPAL)
        style.configure('TLabelframe.Label', background=TemaColores.COLOR_FONDO_PRINCIPAL, foreground=TemaColores.COLOR_PRIMARY, font=('Segoe UI', 10, 'bold'))
        style.configure('TLabel', background=TemaColores.COLOR_FONDO_PRINCIPAL)

    def _crear_frame_titulo(self):
        titulo_frame = tk.Frame(self.root, bg=TemaColores.COLOR_FONDO_DARK, height=50)
        titulo_frame.pack(side="top", fill="x")
        titulo_frame.pack_propagate(False)
        titulo_label = tk.Label(titulo_frame, text="Configurador NFS Integral", bg=TemaColores.COLOR_FONDO_DARK, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 14, 'bold'))
        titulo_label.pack(pady=10)

    def _crear_widgets_master(self):
        # --- 1. Formulario de Exportación ---
        form_frame = ttk.LabelFrame(self.frame_master, text="1. Exportar Nuevo Recurso", padding="15")
        form_frame.pack(fill="x", expand="no", padx=5, pady=8)

        ttk.Label(form_frame, text="Ruta a Exportar:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.master_carpeta_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.master_carpeta_var, width=40).grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Hosts Permitidos:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.master_host_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.master_host_var, width=40).grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        opciones_frame = ttk.LabelFrame(form_frame, text="Opciones NFS", padding="10")
        opciones_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10, padx=5)
        
        self.opciones_vars = {
            "rw": tk.BooleanVar(value=True), "ro": tk.BooleanVar(),
            "sync": tk.BooleanVar(value=True), "async": tk.BooleanVar(),
            "root_squash": tk.BooleanVar(value=True), "no_root_squash": tk.BooleanVar(),
            "all_squash": tk.BooleanVar(), "no_all_squash": tk.BooleanVar(value=True),
        }

        row, col = 0, 0
        for opt, var in self.opciones_vars.items():
            ttk.Checkbutton(opciones_frame, text=opt, variable=var).grid(row=row, column=col, sticky="w", padx=5, pady=2)
            col = (col + 1) % 4
            if col == 0: row += 1

        tk.Button(form_frame, text="Crear y Exportar", command=self._crear_y_exportar_master, bg=TemaColores.COLOR_BOTON_SUCCESS, fg='white', font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, rowspan=2, padx=15, sticky="ns", ipady=10)
        form_frame.columnconfigure(1, weight=1)

        # --- 2. Configuraciones Activas ---
        configs_frame = ttk.LabelFrame(self.frame_master, text="2. Configuraciones Activas en /etc/exports", padding="15")
        configs_frame.pack(fill="both", expand="yes", padx=5, pady=8)

        self.lista_configs_master, scrollbar = crear_listbox_personalizado(configs_frame, height=6)
        self.lista_configs_master.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        btn_frame_master = tk.Frame(configs_frame, bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        btn_frame_master.pack(side="left", fill="y", padx=10)
        tk.Button(btn_frame_master, text="Refrescar Lista", command=self._refrescar_lista_master, bg=TemaColores.COLOR_PRIMARY, fg='white').pack(pady=5, ipadx=10)
        tk.Button(btn_frame_master, text="Eliminar Seleccionado", command=self._eliminar_exportacion_master, bg=TemaColores.COLOR_DANGER, fg='white').pack(pady=5, ipadx=10)

        # --- 3. Diagnóstico ---
        verif_frame = ttk.LabelFrame(self.frame_master, text="3. Diagnóstico del Sistema", padding="15")
        verif_frame.pack(fill="x", expand="no", padx=5, pady=8)
        tk.Button(verif_frame, text="Ver Montajes y Disco (df -h)", command=self._verificar_montajes_y_disco_master, bg=TemaColores.COLOR_INFO, fg='white').pack(side="left", padx=8, ipady=5)
        
        self._refrescar_lista_master()

    def _crear_widgets_cliente(self):
        montaje_frame = ttk.LabelFrame(self.frame_cliente, text="1. Montar Recurso Compartido", padding="15")
        montaje_frame.pack(fill="x", expand="no", padx=5, pady=8)

        ttk.Label(montaje_frame, text="IP del Servidor:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.cliente_ip_var = tk.StringVar()
        ttk.Entry(montaje_frame, textvariable=self.cliente_ip_var, width=30).grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(montaje_frame, text="Ruta Remota (del servidor):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.cliente_ruta_remota_var = tk.StringVar()
        ttk.Entry(montaje_frame, textvariable=self.cliente_ruta_remota_var, width=30).grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        
        ttk.Label(montaje_frame, text="Punto de Montaje (local):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.cliente_punto_montaje_var = tk.StringVar()
        ttk.Entry(montaje_frame, textvariable=self.cliente_punto_montaje_var, width=30).grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        tk.Button(montaje_frame, text="Montar Recurso", command=self._montar_recurso_cliente, bg=TemaColores.COLOR_BOTON_SUCCESS, fg='white', font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, rowspan=2, padx=15, sticky="ns", ipady=5)
        tk.Button(montaje_frame, text="Desmontar Recurso", command=self._desmontar_recurso_cliente, bg=TemaColores.COLOR_WARNING, fg='black').grid(row=2, column=2, padx=15, sticky="ns", ipady=5)
        montaje_frame.columnconfigure(1, weight=1)

        share_frame = ttk.LabelFrame(self.frame_cliente, text="2. Transferir Archivos al Recurso Montado", padding="15")
        share_frame.pack(fill="x", expand="no", padx=5, pady=8)
        tk.Button(share_frame, text="Seleccionar y Copiar Archivos", command=self._compartir_archivos_cliente, bg=TemaColores.COLOR_PRIMARY, fg='white').pack(pady=10, ipady=5)

        result_frame = ttk.LabelFrame(self.frame_cliente, text="3. Contenido del Recurso y Notificaciones", padding="15")
        result_frame.pack(fill="both", expand="yes", padx=5, pady=8)

        self.texto_resultados_cliente = tk.Text(result_frame, height=10, wrap="word", bg="#2c3e50", fg="#ecf0f1", font=('Consolas', 10), relief='flat', bd=5)
        self.texto_resultados_cliente.pack(fill="both", expand=True, side="left")
        
        tk.Button(result_frame, text="Listar Contenido", command=self._listar_contenido_cliente, bg=TemaColores.COLOR_INFO, fg='white').pack(pady=5, padx=10, ipadx=10, side="left")

    def _crear_y_exportar_master(self):
        carpeta = self.master_carpeta_var.get()
        host = self.master_host_var.get()
        opts = [opt for opt, var in self.opciones_vars.items() if var.get()]
        res = self.gestor_nfs.crear_y_exportar_recurso(carpeta, host, opts)
        messagebox.showinfo("Resultado de la Exportación", res["message"])
        if res["success"]:
            self._refrescar_lista_master()

    def _refrescar_lista_master(self):
        self.lista_configs_master.delete(0, tk.END)
        configs = self.gestor_nfs.leer_configuraciones()
        for config in configs:
            self.lista_configs_master.insert(tk.END, config)

    def _eliminar_exportacion_master(self):
        try:
            seleccion = self.lista_configs_master.curselection()
            if not seleccion: return
            config_a_eliminar = self.lista_configs_master.get(seleccion[0])
            if messagebox.askyesno("Confirmar Eliminación", f"¿Seguro que quieres eliminar esta exportación?\n\n{config_a_eliminar}"):
                res = self.gestor_nfs.eliminar_configuracion(config_a_eliminar)
                messagebox.showinfo("Resultado de la Eliminación", res["message"])
                if res["success"]:
                    self._refrescar_lista_master()
        except tk.TclError:
            messagebox.showwarning("Selección Vacía", "Por favor, selecciona un elemento de la lista para eliminar.")

    def _verificar_montajes_y_disco_master(self):
        res = self.gestor_nfs.verificar_montajes_y_disco()
        if res["success"]:
            self._mostrar_ventana_resultados("Diagnóstico de Disco y Montajes (df -h)", res["data"])
        else:
            messagebox.showerror("Error de Diagnóstico", res["message"])

    def _montar_recurso_cliente(self):
        self.cliente_nfs.punto_montaje = self.cliente_punto_montaje_var.get()
        res = self.cliente_nfs.montar_recurso(self.cliente_ip_var.get(), self.cliente_ruta_remota_var.get())
        self._actualizar_resultados_cliente(res)
        
    def _desmontar_recurso_cliente(self):
        self.cliente_nfs.punto_montaje = self.cliente_punto_montaje_var.get()
        res = self.cliente_nfs.desmontar_recurso()
        self._actualizar_resultados_cliente(res)

    def _compartir_archivos_cliente(self):
        if not os.path.ismount(self.cliente_punto_montaje_var.get()):
            messagebox.showwarning("Recurso no Montado", "Por favor, monta el recurso antes de intentar compartir archivos.")
            return
        archivos = filedialog.askopenfilenames(title="Selecciona archivos para copiar al recurso NFS")
        if not archivos: return
        res = self.cliente_nfs.compartir_archivos(archivos)
        self._actualizar_resultados_cliente(res)

    def _listar_contenido_cliente(self):
        self.cliente_nfs.punto_montaje = self.cliente_punto_montaje_var.get()
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

    def _mostrar_ventana_resultados(self, titulo, contenido):
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.geometry("700x450")
        ventana.configure(bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        texto = tk.Text(ventana, bg="#2c3e50", fg="#ecf0f1", font=('Consolas', 10), relief='flat', bd=5)
        texto.pack(fill="both", expand=True, padx=10, pady=10)
        texto.insert("1.0", contenido)
        texto.config(state="disabled")

