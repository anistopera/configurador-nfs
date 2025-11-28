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
        
        self._configurar_estilos()

        if not verificar_permisos_administrador():
            messagebox.showerror("Error", "Se requieren permisos de administrador (root).")
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
        
        estado = "SERVIDOR MASTER DETECTADO" if self.es_servidor_master else "MODO CLIENTE"
        messagebox.showinfo("Información", f"Estado de la máquina:\n{estado}")

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelframe', background=TemaColores.COLOR_FONDO_PRINCIPAL, foreground=TemaColores.COLOR_TEXTO)
        style.configure('TLabelframe.Label', background=TemaColores.COLOR_FONDO_PRINCIPAL, foreground=TemaColores.COLOR_PRIMARY, font=('Segoe UI', 10, 'bold'))
        style.configure('TButton', font=('Segoe UI', 9))
        style.map('TButton', background=[('active', TemaColores.COLOR_BOTON_HOVER)])
        style.configure('TLabel', background=TemaColores.COLOR_FONDO_PRINCIPAL, foreground=TemaColores.COLOR_TEXTO, font=('Segoe UI', 9))
        style.configure('TEntry', fieldbackground='white', foreground=TemaColores.COLOR_TEXTO)
        style.configure('TNotebook', background=TemaColores.COLOR_FONDO_PRINCIPAL)
        style.configure('TNotebook.Tab', padding=[20, 10])

    def _crear_frame_titulo(self):
        titulo_frame = tk.Frame(self.root, bg=TemaColores.COLOR_FONDO_DARK, height=60)
        titulo_frame.pack(side="top", fill="x")
        titulo_frame.pack_propagate(False)
        titulo_label = tk.Label(titulo_frame, text="NFS Configurador Integral", bg=TemaColores.COLOR_FONDO_DARK, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 16, 'bold'), pady=10)
        titulo_label.pack()
        subtitulo_label = tk.Label(titulo_frame, text="Gestión de Servidor Master y Cliente NFS para OpenSUSE", bg=TemaColores.COLOR_FONDO_DARK, fg=TemaColores.COLOR_TEXTO_SECONDARY, font=('Segoe UI', 9))
        subtitulo_label.pack()

    def _crear_widgets_master(self):
        form_frame = ttk.LabelFrame(self.frame_master, text="1. Formulario de Exportación", padding="15")
        form_frame.pack(fill="x", expand="no", padx=5, pady=8)

        ttk.Label(form_frame, text="Carpeta a Exportar:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.master_carpeta_var = tk.StringVar(value="/opt/data")
        ttk.Entry(form_frame, textvariable=self.master_carpeta_var, width=40).grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Host/Clientes:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.master_host_var = tk.StringVar(value="*")
        ttk.Entry(form_frame, textvariable=self.master_host_var, width=40).grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        opciones_frame = ttk.LabelFrame(form_frame, text="Opciones NFS", padding="10")
        opciones_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10, padx=5)
        
        self.opciones_vars = {
            "rw": tk.BooleanVar(value=True), "ro": tk.BooleanVar(),
            "sync": tk.BooleanVar(value=True), "async": tk.BooleanVar(),
            "root_squash": tk.BooleanVar(value=True), "no_root_squash": tk.BooleanVar(),
            "all_squash": tk.BooleanVar(), "no_all_squash": tk.BooleanVar(value=True),
            "secure": tk.BooleanVar(value=True), "insecure": tk.BooleanVar(),
        }

        row, col = 0, 0
        for opt, var in self.opciones_vars.items():
            ttk.Checkbutton(opciones_frame, text=opt, variable=var).grid(row=row, column=col, sticky="w", padx=5, pady=2)
            col += 1
            if col >= 4:
                col, row = 0, row + 1

        uid_gid_frame = tk.Frame(opciones_frame, bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        uid_gid_frame.grid(row=row + 1, column=0, columnspan=4, sticky='ew', pady=5)
        
        ttk.Label(uid_gid_frame, text="anonuid:").pack(side='left', padx=(5,0))
        self.anonuid_var = tk.StringVar(value="65534")
        ttk.Entry(uid_gid_frame, textvariable=self.anonuid_var, width=10).pack(side='left', padx=5)

        ttk.Label(uid_gid_frame, text="anongid:").pack(side='left', padx=(15,0))
        self.anongid_var = tk.StringVar(value="65534")
        ttk.Entry(uid_gid_frame, textvariable=self.anongid_var, width=10).pack(side='left', padx=5)

        tk.Button(form_frame, text="Crear y Exportar", command=self._crear_y_exportar_master, bg=TemaColores.COLOR_BOTON_SUCCESS, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 10, 'bold'), padx=15, pady=8, relief='solid', bd=0, cursor='hand2').grid(row=0, column=2, rowspan=2, padx=15, sticky="ns")

        form_frame.columnconfigure(1, weight=1)

        configs_frame = ttk.LabelFrame(self.frame_master, text="2. Configuraciones Activas (/etc/exports)", padding="15")
        configs_frame.pack(fill="both", expand="yes", padx=5, pady=8)

        self.lista_configs_master = crear_listbox_personalizado(configs_frame, height=6)
        self.lista_configs_master.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar = ttk.Scrollbar(configs_frame, orient="vertical", command=self.lista_configs_master.yview)
        scrollbar.pack(side="right", fill="y")
        self.lista_configs_master.config(yscrollcommand=scrollbar.set)
        
        btn_frame = tk.Frame(configs_frame, bg=TemaColores.COLOR_FONDO_PRINCIPAL)
        btn_frame.pack(side="left", fill="y", padx=5)
        tk.Button(btn_frame, text="Refrescar", command=self._refrescar_lista_master, bg=TemaColores.COLOR_PRIMARY, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 9, 'bold'), width=12, relief='solid', bd=0).pack(pady=5)
        tk.Button(btn_frame, text="Eliminar", command=self._eliminar_exportacion_master, bg=TemaColores.COLOR_DANGER, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 9, 'bold'), width=12, relief='solid', bd=0).pack(pady=5)

        verif_frame = ttk.LabelFrame(self.frame_master, text="3. Verificación y Diagnóstico", padding="15")
        verif_frame.pack(fill="x", expand="no", padx=5, pady=8)
        tk.Button(verif_frame, text="Exportaciones Activas", command=self._verificar_exportaciones_master, bg=TemaColores.COLOR_INFO, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 10, 'bold'), padx=15, pady=8, relief='solid', bd=0, cursor='hand2').pack(side="left", padx=8)
        tk.Button(verif_frame, text="Espacio en Disco", command=self._verificar_disco_master, bg=TemaColores.COLOR_WARNING, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 10, 'bold'), padx=15, pady=8, relief='solid', bd=0, cursor='hand2').pack(side="left", padx=8)

        self._refrescar_lista_master()

    def _crear_widgets_cliente(self):
        montaje_frame = ttk.LabelFrame(self.frame_cliente, text="1. Configuración del Cliente y Montaje", padding="15")
        montaje_frame.pack(fill="x", expand="no", padx=5, pady=8)

        ttk.Label(montaje_frame, text="IP del Master:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.cliente_ip_var = tk.StringVar()
        ttk.Entry(montaje_frame, textvariable=self.cliente_ip_var, width=25).grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(montaje_frame, text="Ruta Remota:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.cliente_ruta_remota_var = tk.StringVar(value="/opt/data")
        ttk.Entry(montaje_frame, textvariable=self.cliente_ruta_remota_var, width=25).grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(montaje_frame, text="Punto de Montaje:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.cliente_punto_montaje_var = tk.StringVar(value=self.cliente_nfs.punto_montaje)
        ttk.Entry(montaje_frame, textvariable=self.cliente_punto_montaje_var, state="readonly", width=25).grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        tk.Button(montaje_frame, text="Montar", command=self._montar_recurso_cliente, bg=TemaColores.COLOR_BOTON_SUCCESS, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 10, 'bold'), padx=15, pady=8, relief='solid', bd=0, cursor='hand2').grid(row=0, column=2, rowspan=2, padx=15, sticky="ns")
        tk.Button(montaje_frame, text="Desmontar", command=self._desmontar_recurso_cliente, bg=TemaColores.COLOR_WARNING, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 10, 'bold'), padx=15, pady=8, relief='solid', bd=0, cursor='hand2').grid(row=2, column=2, padx=15, sticky="ns")

        montaje_frame.columnconfigure(1, weight=1)

        share_frame = ttk.LabelFrame(self.frame_cliente, text="2. Compartir Archivos", padding="15")
        share_frame.pack(fill="x", expand="no", padx=5, pady=8)

        tk.Button(share_frame, text="Seleccionar Archivos para Compartir", command=self._compartir_archivos_cliente, bg=TemaColores.COLOR_PRIMARY, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 10, 'bold'), padx=20, pady=10, relief='solid', bd=0, cursor='hand2').pack()

        result_frame = ttk.LabelFrame(self.frame_cliente, text="3. Contenido del Recurso y Notificaciones", padding="15")
        result_frame.pack(fill="both", expand="yes", padx=5, pady=8)

        self.texto_resultados_cliente = tk.Text(result_frame, height=12, wrap="word", bg="#ecf0f1", fg=TemaColores.COLOR_TEXTO, font=('Consolas', 9), relief='flat', bd=1)
        self.texto_resultados_cliente.pack(fill="both", expand=True, padx=(0, 5), pady=(0, 5))
        scrollbar_res = ttk.Scrollbar(result_frame, command=self.texto_resultados_cliente.yview)
        self.texto_resultados_cliente.config(yscrollcommand=scrollbar_res.set)
        scrollbar_res.pack(side="right", fill="y")
        
        tk.Button(result_frame, text="Listar Contenido del Recurso", command=self._listar_contenido_cliente, bg=TemaColores.COLOR_INFO, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 10, 'bold'), padx=15, pady=8, relief='solid', bd=0, cursor='hand2').pack(pady=10)

    def _refrescar_lista_master(self):
        self.lista_configs_master.delete(0, tk.END)
        for config in self.gestor_nfs.leer_configuraciones():
            self.lista_configs_master.insert(tk.END, config)

    def _crear_y_exportar_master(self):
        carpeta = self.master_carpeta_var.get()
        host = self.master_host_var.get()
        opts = [opt for opt, var in self.opciones_vars.items() if var.get()]

        anonuid = self.anonuid_var.get()
        if anonuid.isdigit():
            opts.append(f"anonuid={anonuid}")

        anongid = self.anongid_var.get()
        if anongid.isdigit():
            opts.append(f"anongid={anongid}")

        res = self.gestor_nfs.crear_y_exportar_recurso(carpeta, host, opts)
        
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
            titulo = tk.Label(ventana_verif, text="Exportaciones NFS Activas", bg=TemaColores.COLOR_FONDO_DARK, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 12, 'bold'), pady=10)
            titulo.pack(fill="x")
            texto = tk.Text(ventana_verif, bg="#ecf0f1", fg=TemaColores.COLOR_TEXTO, font=('Consolas', 9), relief='flat', bd=1)
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
            titulo = tk.Label(ventana_verif, text="Espacio en Disco Disponible", bg=TemaColores.COLOR_FONDO_DARK, fg=TemaColores.COLOR_TEXTO_LIGHT, font=('Segoe UI', 12, 'bold'), pady=10)
            titulo.pack(fill="x")
            texto = tk.Text(ventana_verif, bg="#ecf0f1", fg=TemaColores.COLOR_TEXTO, font=('Consolas', 9), relief='flat', bd=1)
            texto.pack(fill="both", expand=True, padx=10, pady=10)
            texto.insert("1.0", f"{res['message']}\n\n{res['data']}")
            texto.config(state="disabled")
        else:
            messagebox.showerror("Error", res["message"])

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

