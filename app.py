import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from conexion import conectar
from seguridad import autenticar, generar_hash

FONDO = "#F2F4F7"
BLANCO = "#FFFFFF"
AZUL = "#34495E"
AZUL_CLARO = "#E8EEF4"
VERDE = "#43845C"
VERDE_CLARO = "#E7F1E9"
TERRACOTA = "#A65C32"
TEXTO = "#303943"
GRIS = "#78838D"
BORDE = "#D9E0E6"

# Módulos de mantenimiento (tabla, campos, etiquetas)
CONFIG = {
    "Categorías": ("Categoria", ["nombre", "descripcion"], ["Nombre", "Descripción"]),
    "Unidades de medida": ("Unidad_Medida", ["nombre", "abreviatura"], ["Nombre", "Abreviatura"]),
    "Productos": ("Producto", ["nombre", "descripcion", "stock_minimo", "id_categoria", "id_unidad"],
                  ["Nombre", "Descripción", "Stock mínimo", "Categoría", "Unidad"]),
    "Instituciones": ("Institucion", ["nombre", "tipo", "telefono"], ["Nombre", "Tipo", "Teléfono"]),
    "Donantes": ("Donante", ["nombre", "tipo_donante", "telefono", "id_institucion"],
                 ["Nombre", "Tipo de donante", "Teléfono", "Institución (solo si es INSTITUCION)"]),
    "Donaciones": ("Donacion", ["codigo", "id_donante", "fecha_recepcion", "destino"],
                   ["Código", "Donante", "Fecha recepción YYYY-MM-DD", "Destino"]),
    "Programas": ("Programa", ["nombre", "objetivos", "fecha_inicio", "fecha_fin"],
                  ["Nombre", "Objetivos", "Fecha inicio YYYY-MM-DD (opcional)", "Fecha fin YYYY-MM-DD (opcional)"]),
    "Mascotas beneficiarias": ("Beneficiario", ["nombre", "especie", "raza", "sexo", "edad_aprox", "fecha_ingreso"],
                               ["Nombre", "Especie", "Raza", "Sexo", "Edad aproximada", "Fecha ingreso YYYY-MM-DD"]),
    "Inscribir mascota en programa": ("Programa_Beneficiario", ["id_programa", "id_beneficiario", "fecha_registro"],
                                      ["Programa", "Mascota", "Fecha YYYY-MM-DD"]),
    "Usuarios": ("Usuario", ["nombre_usuario", "contrasena_hash", "nombre_completo", "rol", "activo"],
                 ["Usuario", "Contraseña (mín. 8, se guarda cifrada)", "Nombre completo", "Rol", "Activo (1 = sí, 0 = no)"]),
}

# Clave primaria de cada tabla (Programa_Beneficiario tiene clave compuesta)
PK = {
    "Categoria": ["id_categoria"], "Unidad_Medida": ["id_unidad"], "Producto": ["id_producto"],
    "Institucion": ["id_institucion"], "Donante": ["id_donante"], "Donacion": ["id_donacion"],
    "Programa": ["id_programa"], "Beneficiario": ["id_beneficiario"],
    "Programa_Beneficiario": ["id_programa", "id_beneficiario"], "Usuario": ["id_usuario"],
}

# Campos que se eligen de una lista desplegable
FK_SQL = {
    "id_categoria": "SELECT id_categoria, nombre FROM Categoria ORDER BY nombre",
    "id_unidad": "SELECT id_unidad, CONCAT(nombre,' (',abreviatura,')') FROM Unidad_Medida ORDER BY nombre",
    "id_institucion": "SELECT id_institucion, nombre FROM Institucion ORDER BY nombre",
    "id_donante": "SELECT id_donante, nombre FROM Donante ORDER BY nombre",
    "id_programa": "SELECT id_programa, nombre FROM Programa ORDER BY nombre",
    "id_beneficiario": "SELECT id_beneficiario, CONCAT(nombre,' (',especie,')') FROM Beneficiario ORDER BY nombre",
}
ENUMS = {
    "tipo_donante": ["PERSONA", "INSTITUCION"],
    "sexo": ["Macho", "Hembra"],
    "rol": ["ADMIN", "OPERADOR"],
    "activo": ["1", "0"],
}
OPCIONALES = {"id_institucion", "fecha_fin", "fecha_inicio", "descripcion", "objetivos",
              "raza", "edad_aprox", "telefono", "tipo"}
CAMPOS_FECHA = {"fecha_recepcion", "fecha_inicio", "fecha_fin", "fecha_ingreso", "fecha_registro"}
FECHA_HOY = {"fecha_recepcion", "fecha_ingreso", "fecha_registro"}
DEFAULTS = {"rol": "OPERADOR", "activo": "1", "stock_minimo": "0"}

# Productos con su existencia vigente (sin contar lotes vencidos)
SQL_PRODUCTOS = """
    SELECT p.id_producto,
           CONCAT(p.nombre, ' [', u.abreviatura, '] disponible: ',
                  COALESCE(SUM(CASE WHEN l.fecha_vencimiento IS NULL
                                      OR l.fecha_vencimiento >= CURDATE()
                                    THEN l.cantidad_actual END), 0))
    FROM Producto p
    JOIN Unidad_Medida u ON u.id_unidad = p.id_unidad
    LEFT JOIN Lote l ON l.id_producto = p.id_producto
    GROUP BY p.id_producto, p.nombre, u.abreviatura
    ORDER BY p.nombre
"""


class PeluchinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Albergue de Mascotas Peluchin | Inventario y Suministros")
        self.root.geometry("1180x760")
        self.root.minsize(980, 650)
        self.usuario = None
        self.construir_login()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def db(self):
        cn = conectar()
        if cn is None:
            messagebox.showerror("Base de datos", "No se pudo conectar a MySQL.\nRevisa conexion.py y que MySQL esté iniciado.")
        return cn

    def limpiar(self):
        for w in self.root.winfo_children():
            w.destroy()

    def opciones(self, sql, params=(), vacio=False):
        """Devuelve una lista 'id - texto' para los desplegables."""
        datos = []
        cn = self.db()
        if cn is not None:
            cur = cn.cursor()
            try:
                cur.execute(sql, params)
                datos = [f"{f[0]} - {f[1]}" for f in cur.fetchall()]
            except Exception as e:
                messagebox.showerror("Consulta", str(e))
            finally:
                cur.close()
                cn.close()
        return ([""] + datos) if vacio else datos

    @staticmethod
    def id_de(texto):
        texto = (texto or "").strip()
        return int(texto.split(" - ")[0]) if texto else None

    @staticmethod
    def leer_fecha(texto, nombre, obligatoria=True):
        texto = (texto or "").strip()
        if not texto:
            if obligatoria:
                raise ValueError(f"{nombre}: es obligatoria (formato AAAA-MM-DD).")
            return None
        try:
            return datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"{nombre}: usa el formato AAAA-MM-DD (ejemplo 2026-11-16).")

    @staticmethod
    def leer_cantidad(texto):
        try:
            c = Decimal((texto or "").strip().replace(",", "."))
        except InvalidOperation:
            raise ValueError("La cantidad no es un número válido.")
        if not c.is_finite() or c <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        return c

    # ------------------------------------------------------------------
    # Login y menú
    # ------------------------------------------------------------------
    def construir_login(self):
        self.limpiar()
        self.root.configure(bg=FONDO)
        marco = tk.Frame(self.root, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        marco.place(relx=.5, rely=.5, anchor="center", width=430, height=440)
        tk.Frame(marco, bg=TERRACOTA, height=7).pack(fill="x")
        tk.Label(marco, text="🐾  🐶  🐱  🐾", bg=BLANCO, fg=TERRACOTA,
                 font=("Arial", 25)).pack(pady=(28, 5))
        tk.Label(marco, text="ALBERGUE DE MASCOTAS", bg=BLANCO, fg=AZUL,
                 font=("Arial", 15, "bold")).pack()
        tk.Label(marco, text="PELUCHIN", bg=BLANCO, fg=TERRACOTA,
                 font=("Arial", 23, "bold")).pack(pady=3)
        tk.Label(marco, text="Sistema de Inventario y Suministros", bg=BLANCO,
                 fg=GRIS, font=("Arial", 10)).pack(pady=(0, 22))
        tk.Label(marco, text="Usuario", bg=BLANCO, fg=TEXTO, font=("Arial", 10, "bold")).pack(anchor="w", padx=55)
        self.in_usuario = ttk.Entry(marco, width=37)
        self.in_usuario.pack(pady=(5, 13), ipady=6)
        tk.Label(marco, text="Contraseña", bg=BLANCO, fg=TEXTO, font=("Arial", 10, "bold")).pack(anchor="w", padx=55)
        self.in_clave = ttk.Entry(marco, width=37, show="•")
        self.in_clave.pack(pady=(5, 18), ipady=6)
        self.in_clave.bind("<Return>", lambda e: self.entrar())
        tk.Button(marco, text="INGRESAR", command=self.entrar, bg=AZUL, fg=BLANCO,
                  activebackground=VERDE, activeforeground=BLANCO, relief="flat",
                  font=("Arial", 10, "bold"), cursor="hand2").pack(fill="x", padx=55, ipady=10)
        tk.Label(marco, text="Cuidando a quienes nos necesitan ♥", bg=BLANCO,
                 fg=GRIS, font=("Arial", 9, "italic")).pack(pady=22)

    def entrar(self):
        usuario = self.in_usuario.get().strip()
        clave = self.in_clave.get()
        if not usuario or not clave:
            messagebox.showwarning("Acceso", "Escribe usuario y contraseña.")
            return
        datos = autenticar(usuario, clave)
        if not datos:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos, o cuenta inactiva.")
            return
        self.usuario = datos
        self.inicio()

    def encabezado(self, contenedor):
        head = tk.Frame(contenedor, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        head.pack(fill="x", padx=22, pady=(18, 14))
        tk.Frame(head, bg=TERRACOTA, height=5).pack(fill="x")
        fila = tk.Frame(head, bg=BLANCO)
        fila.pack(fill="x", padx=18, pady=10)
        tk.Label(fila, text="🐾  ALBERGUE DE MASCOTAS PELUCHIN", bg=BLANCO,
                 fg=AZUL, font=("Arial", 17, "bold")).pack(side="left")
        tk.Label(fila, text=f"{self.usuario['nombre']}  |  {self.usuario['rol']}",
                 bg=BLANCO, fg=VERDE, font=("Arial", 9, "bold")).pack(side="right")
        tk.Label(head, text="Sistema de Inventario y Suministros  •  Cuidando a quienes nos necesitan",
                 bg=BLANCO, fg=GRIS, font=("Arial", 9)).pack(pady=(0, 10))

    def inicio(self):
        self.limpiar()
        self.root.configure(bg=FONDO)
        self.encabezado(self.root)
        cuerpo = tk.Frame(self.root, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=30, pady=5)
        tk.Label(cuerpo, text="MENÚ PRINCIPAL", bg=FONDO, fg=AZUL,
                 font=("Arial", 17, "bold")).pack(pady=(4, 14))
        tarjetas = tk.Frame(cuerpo, bg=FONDO)
        tarjetas.pack()
        modulos = [
            ("Productos", "📦"), ("Categorías", "▦"), ("Unidades de medida", "⚖"),
            ("Inventario", "📋"), ("Lotes", "🧾"), ("Registrar entrada", "⬇"),
            ("Registrar salida", "⬆"), ("Registrar entrega a mascota", "🐾"), ("Historial de movimientos", "🕘"),
            ("Donaciones", "🎁"), ("Donantes", "🤝"), ("Instituciones", "🏢"),
            ("Mascotas beneficiarias", "🐶"), ("Programas", "❤"), ("Inscribir mascota en programa", "🐾"),
            ("Alertas y reportes", "📊"),
        ]
        if self.usuario["rol"] == "ADMIN":
            modulos.append(("Usuarios", "👤"))
        for i, (nombre, icono) in enumerate(modulos):
            r, c = divmod(i, 3)
            color = VERDE_CLARO if i % 2 == 0 else AZUL_CLARO
            b = tk.Button(tarjetas, text=f"{icono}   {nombre.upper()}", width=34, height=2,
                          command=lambda n=nombre: self.abrir(n), bg=BLANCO, fg=AZUL,
                          activebackground=color, relief="solid", bd=1,
                          highlightbackground=BORDE, font=("Arial", 9, "bold"), cursor="hand2")
            b.grid(row=r, column=c, padx=8, pady=6, sticky="ew")
        pie = tk.Frame(cuerpo, bg=FONDO)
        pie.pack(fill="x", pady=15)
        tk.Button(pie, text="VER RESUMEN GENERAL", command=self.resumen,
                  bg=AZUL, fg=BLANCO, relief="flat", font=("Arial", 10, "bold"),
                  padx=20, pady=9, cursor="hand2").pack(side="left", padx=10)
        tk.Button(pie, text="CERRAR SESIÓN", command=self.cerrar_sesion,
                  bg=TERRACOTA, fg=BLANCO, relief="flat", font=("Arial", 9, "bold"),
                  padx=16, pady=9, cursor="hand2").pack(side="right", padx=10)

    def cerrar_sesion(self):
        self.usuario = None
        self.construir_login()

    def abrir(self, nombre):
        if nombre == "Usuarios" and self.usuario["rol"] != "ADMIN":
            messagebox.showwarning("Acceso restringido", "Solo un ADMIN puede administrar usuarios.")
            return
        if nombre in CONFIG:
            self.crud(nombre)
        elif nombre == "Registrar entrada":
            self.form_entrada()
        elif nombre == "Registrar salida":
            self.form_salida(False)
        elif nombre == "Registrar entrega a mascota":
            self.form_salida(True)
        elif nombre == "Inventario":
            self.inventario()
        elif nombre == "Lotes":
            self.lotes()
        elif nombre == "Historial de movimientos":
            self.historial()
        elif nombre == "Alertas y reportes":
            self.alertas()

    def pantalla_modulo(self, titulo):
        self.root.configure(bg=FONDO)
        barra = tk.Frame(self.root, bg=AZUL)
        barra.pack(fill="x")
        tk.Label(barra, text=f"🐾  PELUCHIN  |  {titulo.upper()}", bg=AZUL, fg=BLANCO,
                 font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=14)
        tk.Button(barra, text="VOLVER AL MENÚ", command=self.inicio, bg=BLANCO, fg=AZUL,
                  relief="flat", padx=12, pady=6).pack(side="right", padx=18)
        self.area = tk.Frame(self.root, bg=FONDO)
        self.area.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Mantenimiento (CRUD)
    # ------------------------------------------------------------------
    def crud(self, nombre):
        tabla, campos, etiquetas = CONFIG[nombre]
        pk_cols = PK[tabla]
        compuesta = all(c in campos for c in pk_cols)
        cols_sel = list(campos) if compuesta else pk_cols + list(campos)

        self.limpiar()
        self.pantalla_modulo(nombre)
        cont = self.area
        form = tk.LabelFrame(cont, text="Datos del registro", bg=BLANCO, fg=AZUL, padx=10, pady=10)
        form.pack(fill="x", padx=20, pady=10)
        entradas = {}
        opc_fk = {}
        for i, (campo, etiqueta) in enumerate(zip(campos, etiquetas)):
            tk.Label(form, text=etiqueta, bg=BLANCO, fg=TEXTO).grid(
                row=i // 3 * 2, column=i % 3, sticky="w", padx=6, pady=(4, 0))
            if campo in FK_SQL:
                opc_fk[campo] = self.opciones(FK_SQL[campo], vacio=(campo in OPCIONALES))
                ent = ttk.Combobox(form, width=30, state="readonly", values=opc_fk[campo])
            elif campo in ENUMS:
                ent = ttk.Combobox(form, width=30, state="readonly", values=ENUMS[campo])
            else:
                ent = ttk.Entry(form, width=32, show="•" if campo == "contrasena_hash" else "")
            ent.grid(row=i // 3 * 2 + 1, column=i % 3, sticky="ew", padx=6, pady=(2, 7))
            entradas[campo] = ent
        for c in range(3):
            form.grid_columnconfigure(c, weight=1)

        barra = tk.Frame(cont, bg=FONDO)
        barra.pack(fill="x", padx=20, pady=5)
        caja = tk.Frame(cont, bg=FONDO)
        caja.pack(fill="both", expand=True, padx=20, pady=10)
        tabla_ui = ttk.Treeview(caja, columns=cols_sel, show="headings", height=14)
        sb = ttk.Scrollbar(caja, orient="vertical", command=tabla_ui.yview)
        tabla_ui.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tabla_ui.pack(side="left", fill="both", expand=True)
        for col in cols_sel:
            tabla_ui.heading(col, text=col.replace("_", " ").upper())
            tabla_ui.column(col, width=130, anchor="center")

        seleccionado = {"id": None}   # tupla con los valores de la clave primaria

        def poner(campo, texto):
            w = entradas[campo]
            if isinstance(w, ttk.Combobox):
                w.set(texto)
            else:
                w.delete(0, "end")
                w.insert(0, texto)

        def limpiar_form():
            seleccionado["id"] = None
            for c in campos:
                defecto = DEFAULTS.get(c, date.today().isoformat() if c in FECHA_HOY else "")
                poner(c, defecto)
            tabla_ui.selection_remove(tabla_ui.selection())

        def cargar():
            for item in tabla_ui.get_children():
                tabla_ui.delete(item)
            cn = self.db()
            if not cn:
                return
            cur = cn.cursor()
            try:
                cols = ", ".join(f"`{c}`" for c in cols_sel)
                cur.execute(f"SELECT {cols} FROM `{tabla}` ORDER BY 1 DESC")
                for fila in cur.fetchall():
                    fila = ["" if v is None else v for v in fila]
                    if tabla == "Usuario":
                        fila[cols_sel.index("contrasena_hash")] = "••••••••"
                    tabla_ui.insert("", "end", values=fila)
            except Exception as e:
                messagebox.showerror("Consulta", str(e))
            finally:
                cur.close()
                cn.close()

        def elegir(event=None):
            sel = tabla_ui.selection()
            if not sel:
                return
            valores = tabla_ui.item(sel[0], "values")
            if compuesta:
                seleccionado["id"] = tuple(valores[cols_sel.index(c)] for c in pk_cols)
                datos = valores
            else:
                seleccionado["id"] = tuple(valores[:len(pk_cols)])
                datos = valores[len(pk_cols):]
            for campo, valor in zip(campos, datos):
                if campo == "contrasena_hash":
                    poner(campo, "")
                elif campo in FK_SQL:
                    poner(campo, next((o for o in opc_fk[campo] if o.split(" - ")[0] == str(valor)), ""))
                else:
                    poner(campo, str(valor))
        tabla_ui.bind("<<TreeviewSelect>>", elegir)

        def guardar():
            try:
                valores = []
                for campo, etiqueta in zip(campos, etiquetas):
                    v = entradas[campo].get().strip()
                    if campo == "contrasena_hash":
                        if v:
                            if len(v) < 8:
                                raise ValueError("La contraseña debe tener al menos 8 caracteres.")
                            v = generar_hash(v)
                        elif seleccionado["id"] is not None:
                            v = None   # al editar, vacío = conservar la contraseña actual
                        else:
                            raise ValueError("La contraseña es obligatoria para un usuario nuevo.")
                    elif v == "":
                        if campo in OPCIONALES:
                            v = None
                        else:
                            raise ValueError(f"Completa el campo: {etiqueta}.")
                    elif campo in FK_SQL:
                        v = self.id_de(v)
                    elif campo in CAMPOS_FECHA:
                        v = self.leer_fecha(v, etiqueta).isoformat()
                    elif campo == "edad_aprox":
                        if not v.isdigit():
                            raise ValueError("La edad aproximada debe ser un número entero (0 o más).")
                        v = int(v)
                    elif campo == "stock_minimo":
                        try:
                            v = Decimal(v.replace(",", "."))
                        except InvalidOperation:
                            raise ValueError("El stock mínimo debe ser un número.")
                        if not v.is_finite() or v < 0:
                            raise ValueError("El stock mínimo no puede ser negativo.")
                    elif campo in ("rol", "tipo_donante"):
                        v = v.upper()
                    valores.append(v)

                datos = dict(zip(campos, valores))
                if tabla == "Donante":
                    if datos["tipo_donante"] == "INSTITUCION" and datos["id_institucion"] is None:
                        raise ValueError("Para un donante INSTITUCION elige la institución.")
                    if datos["tipo_donante"] == "PERSONA" and datos["id_institucion"] is not None:
                        raise ValueError("Una PERSONA no lleva institución; déjala en blanco.")
                if (tabla == "Usuario" and seleccionado["id"] is not None
                        and str(seleccionado["id"][0]) == str(self.usuario["id"])
                        and str(datos["activo"]) == "0"):
                    raise ValueError("No puedes desactivar tu propia cuenta.")

                cn = self.db()
                if not cn:
                    return
                cur = cn.cursor()
                try:
                    if seleccionado["id"] is not None:
                        pares = [(c, v) for c, v in zip(campos, valores)
                                 if not (c == "contrasena_hash" and v is None)]
                        asign = ", ".join(f"`{c}`=%s" for c, _ in pares)
                        donde = " AND ".join(f"`{c}`=%s" for c in pk_cols)
                        cur.execute(f"UPDATE `{tabla}` SET {asign} WHERE {donde}",
                                    tuple(v for _, v in pares) + tuple(seleccionado["id"]))
                    else:
                        cols = ", ".join(f"`{c}`" for c in campos)
                        marks = ", ".join(["%s"] * len(campos))
                        cur.execute(f"INSERT INTO `{tabla}` ({cols}) VALUES ({marks})", tuple(valores))
                    cn.commit()
                except Exception:
                    cn.rollback()
                    raise
                finally:
                    cur.close()
                    cn.close()
                messagebox.showinfo("Correcto", "Registro guardado correctamente.")
                limpiar_form()
                cargar()
            except ValueError as e:
                messagebox.showwarning("Validación", str(e))
            except Exception as e:
                messagebox.showerror("No se pudo guardar", f"Verifica los datos y las relaciones.\n\n{e}")

        def eliminar():
            if seleccionado["id"] is None:
                messagebox.showwarning("Eliminar", "Selecciona un registro.")
                return
            if tabla == "Usuario" and str(seleccionado["id"][0]) == str(self.usuario["id"]):
                messagebox.showwarning("Eliminar", "No puedes eliminar tu propia cuenta.")
                return
            if not messagebox.askyesno("Confirmar", "¿Deseas eliminar el registro seleccionado?"):
                return
            cn = self.db()
            if not cn:
                return
            cur = cn.cursor()
            try:
                donde = " AND ".join(f"`{c}`=%s" for c in pk_cols)
                cur.execute(f"DELETE FROM `{tabla}` WHERE {donde}", tuple(seleccionado["id"]))
                cn.commit()
            except Exception as e:
                cn.rollback()
                messagebox.showerror("No se puede eliminar",
                                     f"El registro puede estar relacionado con otros datos.\n{e}")
                return
            finally:
                cur.close()
                cn.close()
            limpiar_form()
            cargar()

        tk.Button(barra, text="GUARDAR / ACTUALIZAR", command=guardar, bg=VERDE, fg=BLANCO,
                  relief="flat", padx=12, pady=7).pack(side="left", padx=4)
        tk.Button(barra, text="NUEVO / LIMPIAR", command=limpiar_form, bg=AZUL, fg=BLANCO,
                  relief="flat", padx=12, pady=7).pack(side="left", padx=4)
        tk.Button(barra, text="ELIMINAR", command=eliminar, bg=TERRACOTA, fg=BLANCO,
                  relief="flat", padx=12, pady=7).pack(side="left", padx=4)
        tk.Button(barra, text="ACTUALIZAR LISTA", command=cargar, bg=GRIS, fg=BLANCO,
                  relief="flat", padx=12, pady=7).pack(side="left", padx=4)
        cargar()
        limpiar_form()

    # ------------------------------------------------------------------
    # Entrada de stock (crea un lote)
    # ------------------------------------------------------------------
    def form_entrada(self):
        self.limpiar()
        self.pantalla_modulo("Registrar entrada")
        f = tk.Frame(self.area, bg=BLANCO, padx=24, pady=22, highlightbackground=BORDE, highlightthickness=1)
        f.pack(fill="x", padx=35, pady=25)
        f.grid_columnconfigure(1, weight=1)
        tk.Label(f, text="REGISTRAR ENTRADA", bg=BLANCO, fg=AZUL, font=("Arial", 15, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        def etiqueta(r, texto):
            tk.Label(f, text=texto, bg=BLANCO, fg=TEXTO).grid(row=r, column=0, sticky="w", pady=7)

        etiqueta(1, "Producto")
        cb_prod = ttk.Combobox(f, state="readonly", values=self.opciones(SQL_PRODUCTOS))
        cb_prod.grid(row=1, column=1, sticky="ew", pady=7, padx=10)
        etiqueta(2, "Cantidad")
        e_cant = ttk.Entry(f, width=42)
        e_cant.grid(row=2, column=1, sticky="ew", pady=7, padx=10)
        etiqueta(3, "Donación de origen (opcional)")
        cb_don = ttk.Combobox(f, state="readonly", values=self.opciones(
            "SELECT id_donacion, CONCAT(codigo,' (',fecha_recepcion,')') FROM Donacion "
            "ORDER BY fecha_recepcion DESC", vacio=True))
        cb_don.grid(row=3, column=1, sticky="ew", pady=7, padx=10)
        etiqueta(4, "Fecha de ingreso (YYYY-MM-DD)")
        e_fecha = ttk.Entry(f, width=42)
        e_fecha.grid(row=4, column=1, sticky="ew", pady=7, padx=10)
        e_fecha.insert(0, date.today().isoformat())
        etiqueta(5, "Fecha de vencimiento (opcional)")
        e_venc = ttk.Entry(f, width=42)
        e_venc.grid(row=5, column=1, sticky="ew", pady=7, padx=10)
        etiqueta(6, "Observación")
        e_obs = ttk.Entry(f, width=42)
        e_obs.grid(row=6, column=1, sticky="ew", pady=7, padx=10)

        def guardar():
            try:
                producto = self.id_de(cb_prod.get())
                if producto is None:
                    raise ValueError("Selecciona un producto.")
                cantidad = self.leer_cantidad(e_cant.get())
                f_ing = self.leer_fecha(e_fecha.get(), "Fecha de ingreso")
                f_ven = self.leer_fecha(e_venc.get(), "Fecha de vencimiento", obligatoria=False)
                if f_ven and f_ven < f_ing:
                    raise ValueError("El vencimiento no puede ser anterior a la fecha de ingreso.")
                donacion = self.id_de(cb_don.get())
                obs = e_obs.get().strip() or None
                cn = self.db()
                if not cn:
                    return
                cur = cn.cursor()
                try:
                    cur.execute("INSERT INTO Movimiento(tipo_movimiento,id_usuario,observacion) "
                                "VALUES('ENTRADA',%s,%s)", (self.usuario["id"], obs))
                    mid = cur.lastrowid
                    cur.execute("""INSERT INTO Lote(id_producto,id_donacion,cantidad_inicial,cantidad_actual,
                                                    fecha_ingreso,fecha_vencimiento)
                                   VALUES(%s,%s,%s,%s,%s,%s)""",
                                (producto, donacion, cantidad, cantidad, f_ing, f_ven))
                    lote = cur.lastrowid
                    cur.execute("INSERT INTO Detalle_Movimiento(id_movimiento,id_lote,cantidad) VALUES(%s,%s,%s)",
                                (mid, lote, cantidad))
                    cn.commit()
                except Exception:
                    cn.rollback()
                    raise
                finally:
                    cur.close()
                    cn.close()
                messagebox.showinfo("Correcto", f"Entrada registrada.\nN.º movimiento: {mid}\nN.º lote creado: {lote}")
                cb_prod["values"] = self.opciones(SQL_PRODUCTOS)
                cb_prod.set("")
                cb_don.set("")
                for e in (e_cant, e_venc, e_obs):
                    e.delete(0, "end")
            except ValueError as e:
                messagebox.showerror("Datos incorrectos", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(f, text="GUARDAR ENTRADA", command=guardar, bg=VERDE, fg=BLANCO,
                  relief="flat", padx=18, pady=9).grid(row=7, column=0, columnspan=2, pady=18)

    # ------------------------------------------------------------------
    # Salida de stock (lote que vence primero) y entrega a mascota
    # ------------------------------------------------------------------
    def crear_salida(self, cur, items, obs):
        """items = [(id_producto, nombre, cantidad)]. Descuenta primero el lote que vence antes.
        Los lotes vencidos no se entregan. Devuelve el id del Movimiento SALIDA."""
        plan = []
        for id_producto, nombre, cantidad in items:
            cur.execute("""SELECT id_lote, cantidad_actual FROM Lote
                           WHERE id_producto=%s AND cantidad_actual>0
                             AND (fecha_vencimiento IS NULL OR fecha_vencimiento>=CURDATE())
                           ORDER BY fecha_vencimiento IS NULL, fecha_vencimiento, fecha_ingreso, id_lote
                           FOR UPDATE""", (id_producto,))
            pendiente = cantidad
            for id_lote, actual in cur.fetchall():
                if pendiente <= 0:
                    break
                tomar = min(Decimal(str(actual)), pendiente)
                plan.append((id_lote, tomar))
                pendiente -= tomar
            if pendiente > 0:
                raise ValueError(f"Stock vigente insuficiente de «{nombre}». "
                                 f"Faltan {pendiente} (los lotes vencidos no se entregan).")
        cur.execute("INSERT INTO Movimiento(tipo_movimiento,id_usuario,observacion) VALUES('SALIDA',%s,%s)",
                    (self.usuario["id"], obs))
        mid = cur.lastrowid
        for id_lote, tomar in plan:
            cur.execute("UPDATE Lote SET cantidad_actual=cantidad_actual-%s WHERE id_lote=%s", (tomar, id_lote))
            cur.execute("INSERT INTO Detalle_Movimiento(id_movimiento,id_lote,cantidad) VALUES(%s,%s,%s)",
                        (mid, id_lote, tomar))
        return mid

    def form_salida(self, con_entrega=False):
        titulo = "Registrar entrega a mascota" if con_entrega else "Registrar salida"
        self.limpiar()
        self.pantalla_modulo(titulo)
        f = tk.Frame(self.area, bg=BLANCO, padx=24, pady=18, highlightbackground=BORDE, highlightthickness=1)
        f.pack(fill="both", expand=True, padx=35, pady=20)
        f.grid_columnconfigure(1, weight=1)
        r = 0
        tk.Label(f, text=titulo.upper(), bg=BLANCO, fg=AZUL, font=("Arial", 15, "bold")).grid(
            row=r, column=0, columnspan=3, sticky="w", pady=(0, 12))
        r += 1

        cb_prog = cb_masc = None
        if con_entrega:
            tk.Label(f, text="Programa", bg=BLANCO, fg=TEXTO).grid(row=r, column=0, sticky="w", pady=6)
            cb_prog = ttk.Combobox(f, state="readonly", values=self.opciones(
                "SELECT id_programa, nombre FROM Programa ORDER BY nombre"))
            cb_prog.grid(row=r, column=1, columnspan=2, sticky="ew", padx=10)
            r += 1
            tk.Label(f, text="Mascota inscrita", bg=BLANCO, fg=TEXTO).grid(row=r, column=0, sticky="w", pady=6)
            cb_masc = ttk.Combobox(f, state="readonly")
            cb_masc.grid(row=r, column=1, columnspan=2, sticky="ew", padx=10)
            r += 1

            def cargar_mascotas(event=None):
                cb_masc.set("")
                idp = self.id_de(cb_prog.get())
                if idp is None:
                    cb_masc["values"] = []
                    return
                lista = self.opciones(
                    """SELECT b.id_beneficiario, CONCAT(b.nombre,' (',b.especie,')')
                       FROM Programa_Beneficiario pb
                       JOIN Beneficiario b ON b.id_beneficiario=pb.id_beneficiario
                       WHERE pb.id_programa=%s ORDER BY b.nombre""", (idp,))
                cb_masc["values"] = lista
                if not lista:
                    messagebox.showinfo("Programa", "Este programa no tiene mascotas inscritas.\n"
                                                    "Inscríbelas primero en «Inscribir mascota en programa».")
            cb_prog.bind("<<ComboboxSelected>>", cargar_mascotas)

        tk.Label(f, text="Producto", bg=BLANCO, fg=TEXTO).grid(row=r, column=0, sticky="w", pady=6)
        cb_prod = ttk.Combobox(f, state="readonly", values=self.opciones(SQL_PRODUCTOS))
        cb_prod.grid(row=r, column=1, columnspan=2, sticky="ew", padx=10)
        r += 1
        tk.Label(f, text="Cantidad", bg=BLANCO, fg=TEXTO).grid(row=r, column=0, sticky="w", pady=6)
        e_cant = ttk.Entry(f, width=20)
        e_cant.grid(row=r, column=1, sticky="w", padx=10)
        tk.Button(f, text="AGREGAR A LA LISTA", command=lambda: agregar(), bg=AZUL, fg=BLANCO,
                  relief="flat", padx=10, pady=4).grid(row=r, column=2, padx=6)
        r += 1

        tv = ttk.Treeview(f, columns=("producto", "cantidad"), show="headings", height=7)
        tv.heading("producto", text="PRODUCTO")
        tv.heading("cantidad", text="CANTIDAD")
        tv.column("producto", width=420, anchor="w")
        tv.column("cantidad", width=120, anchor="center")
        tv.grid(row=r, column=0, columnspan=3, sticky="nsew", pady=10)
        f.grid_rowconfigure(r, weight=1)
        r += 1

        tk.Label(f, text="Observación", bg=BLANCO, fg=TEXTO).grid(row=r, column=0, sticky="w", pady=6)
        e_obs = ttk.Entry(f, width=50)
        e_obs.grid(row=r, column=1, columnspan=2, sticky="ew", padx=10)
        r += 1

        items = {}   # id_producto -> [nombre, cantidad]

        def refrescar():
            for i in tv.get_children():
                tv.delete(i)
            for pid, (nom, cant) in items.items():
                tv.insert("", "end", iid=str(pid), values=(nom, cant))

        def recargar_productos():
            cb_prod["values"] = self.opciones(SQL_PRODUCTOS)
            cb_prod.set("")
            e_cant.delete(0, "end")

        def agregar():
            try:
                texto = cb_prod.get()
                pid = self.id_de(texto)
                if pid is None:
                    raise ValueError("Selecciona un producto.")
                cant = self.leer_cantidad(e_cant.get())
            except ValueError as e:
                messagebox.showerror("Datos incorrectos", str(e))
                return
            nom = texto.split(" - ", 1)[1].split(" [")[0]
            if pid in items:
                items[pid][1] += cant
            else:
                items[pid] = [nom, cant]
            refrescar()
            cb_prod.set("")
            e_cant.delete(0, "end")

        def quitar():
            sel = tv.selection()
            if sel:
                items.pop(int(sel[0]), None)
                refrescar()

        def registrar():
            try:
                if not items:
                    raise ValueError("Agrega al menos un producto a la lista.")
                idp = idb = None
                if con_entrega:
                    idp = self.id_de(cb_prog.get())
                    idb = self.id_de(cb_masc.get())
                    if idp is None or idb is None:
                        raise ValueError("Selecciona el programa y la mascota.")
                obs = e_obs.get().strip() or None
                lista = [(pid, nom, cant) for pid, (nom, cant) in items.items()]
                cn = self.db()
                if not cn:
                    return
                cur = cn.cursor()
                try:
                    mid = self.crear_salida(cur, lista, obs)
                    if con_entrega:
                        cur.execute("INSERT INTO Entrega(id_programa,id_beneficiario,id_movimiento) "
                                    "VALUES(%s,%s,%s)", (idp, idb, mid))
                    cn.commit()
                except Exception:
                    cn.rollback()
                    raise
                finally:
                    cur.close()
                    cn.close()
                messagebox.showinfo("Correcto", ("Entrega" if con_entrega else "Salida") +
                                    f" registrada.\nN.º movimiento: {mid}")
                items.clear()
                refrescar()
                e_obs.delete(0, "end")
                recargar_productos()
            except ValueError as e:
                messagebox.showerror("Datos incorrectos", str(e))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        botones = tk.Frame(f, bg=BLANCO)
        botones.grid(row=r, column=0, columnspan=3, pady=12)
        tk.Button(botones, text="QUITAR SELECCIONADO", command=quitar, bg=TERRACOTA, fg=BLANCO,
                  relief="flat", padx=14, pady=8).pack(side="left", padx=8)
        tk.Button(botones, text="REGISTRAR " + ("ENTREGA" if con_entrega else "SALIDA"),
                  command=registrar, bg=VERDE, fg=BLANCO, relief="flat", padx=18, pady=8).pack(side="left", padx=8)

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def tabla_consulta(self, sql, encabezados):
        caja = tk.Frame(self.area, bg=BLANCO)
        caja.pack(fill="both", expand=True, padx=22, pady=15)
        tv = ttk.Treeview(caja, columns=encabezados, show="headings")
        sb = ttk.Scrollbar(caja, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        for col in encabezados:
            tv.heading(col, text=col)
            tv.column(col, width=130, anchor="center")
        sb.pack(side="right", fill="y")
        tv.pack(side="left", fill="both", expand=True)
        cn = self.db()
        if cn:
            cur = cn.cursor()
            try:
                cur.execute(sql)
                for row in cur.fetchall():
                    tv.insert("", "end", values=["" if v is None else v for v in row])
            except Exception as e:
                messagebox.showerror("Consulta", str(e))
            finally:
                cur.close()
                cn.close()

    def inventario(self):
        self.limpiar()
        self.pantalla_modulo("Inventario actual")
        self.tabla_consulta("""
            SELECT p.id_producto, p.nombre, c.nombre, u.abreviatura,
                   COALESCE(SUM(CASE WHEN l.fecha_vencimiento IS NULL OR l.fecha_vencimiento>=CURDATE()
                                     THEN l.cantidad_actual END),0) AS vigente,
                   COALESCE(SUM(CASE WHEN l.fecha_vencimiento<CURDATE()
                                     THEN l.cantidad_actual END),0) AS vencido,
                   p.stock_minimo
            FROM Producto p
            JOIN Categoria c ON c.id_categoria=p.id_categoria
            JOIN Unidad_Medida u ON u.id_unidad=p.id_unidad
            LEFT JOIN Lote l ON l.id_producto=p.id_producto
            GROUP BY p.id_producto,p.nombre,c.nombre,u.abreviatura,p.stock_minimo
            ORDER BY p.nombre
        """, ["ID", "PRODUCTO", "CATEGORÍA", "UNIDAD", "EXISTENCIA VIGENTE", "VENCIDO", "STOCK MÍNIMO"])

    def lotes(self):
        self.limpiar()
        self.pantalla_modulo("Lotes")
        self.tabla_consulta("""
            SELECT l.id_lote, p.nombre, u.abreviatura, l.cantidad_inicial, l.cantidad_actual,
                   l.fecha_ingreso, l.fecha_vencimiento,
                   COALESCE(d.codigo,'Compra / sin donación'),
                   CASE WHEN l.cantidad_actual=0 THEN 'AGOTADO'
                        WHEN l.fecha_vencimiento IS NOT NULL AND l.fecha_vencimiento<CURDATE() THEN 'VENCIDO'
                        WHEN l.fecha_vencimiento IS NOT NULL
                             AND l.fecha_vencimiento<=DATE_ADD(CURDATE(),INTERVAL 30 DAY) THEN 'POR VENCER'
                        ELSE 'VIGENTE' END
            FROM Lote l
            JOIN Producto p ON p.id_producto=l.id_producto
            JOIN Unidad_Medida u ON u.id_unidad=p.id_unidad
            LEFT JOIN Donacion d ON d.id_donacion=l.id_donacion
            ORDER BY (l.cantidad_actual=0), l.fecha_vencimiento IS NULL, l.fecha_vencimiento, l.id_lote
        """, ["LOTE", "PRODUCTO", "UNIDAD", "CANT. INICIAL", "CANT. ACTUAL",
              "INGRESO", "VENCE", "DONACIÓN", "ESTADO"])

    def historial(self):
        self.limpiar()
        self.pantalla_modulo("Historial de movimientos")
        self.tabla_consulta("""
            SELECT m.id_movimiento, m.fecha, m.tipo_movimiento, p.nombre, d.id_lote, d.cantidad,
                   us.nombre_usuario,
                   COALESCE(CONCAT(pr.nombre,' / ',b.nombre),'') AS entrega
            FROM Movimiento m
            JOIN Usuario us ON us.id_usuario=m.id_usuario
            JOIN Detalle_Movimiento d ON d.id_movimiento=m.id_movimiento
            JOIN Lote l ON l.id_lote=d.id_lote
            JOIN Producto p ON p.id_producto=l.id_producto
            LEFT JOIN Entrega e ON e.id_movimiento=m.id_movimiento
            LEFT JOIN Programa pr ON pr.id_programa=e.id_programa
            LEFT JOIN Beneficiario b ON b.id_beneficiario=e.id_beneficiario
            ORDER BY m.fecha DESC, m.id_movimiento DESC
            LIMIT 500
        """, ["N.º MOV.", "FECHA", "TIPO", "PRODUCTO", "LOTE", "CANTIDAD", "USUARIO", "ENTREGA (PROGRAMA / MASCOTA)"])

    def alertas(self):
        self.limpiar()
        self.pantalla_modulo("Alertas y reportes")
        tk.Label(self.area, text="STOCK BAJO, LOTES VENCIDOS Y PRÓXIMOS A VENCER",
                 bg=FONDO, fg=AZUL, font=("Arial", 13, "bold")).pack(pady=15)
        self.tabla_consulta("""
            SELECT 'STOCK BAJO' AS alerta, p.nombre AS producto, NULL AS lote,
                   COALESCE(SUM(CASE WHEN l.fecha_vencimiento IS NULL OR l.fecha_vencimiento>=CURDATE()
                                     THEN l.cantidad_actual END),0) AS cantidad,
                   u.abreviatura AS unidad, CONCAT('Mínimo: ', p.stock_minimo) AS detalle
            FROM Producto p
            JOIN Unidad_Medida u ON u.id_unidad=p.id_unidad
            LEFT JOIN Lote l ON l.id_producto=p.id_producto
            GROUP BY p.id_producto,p.nombre,p.stock_minimo,u.abreviatura
            HAVING p.stock_minimo>0 AND cantidad<=p.stock_minimo
            UNION ALL
            SELECT CASE WHEN l.fecha_vencimiento<CURDATE() THEN 'VENCIDO' ELSE 'POR VENCER' END,
                   p.nombre, l.id_lote, l.cantidad_actual, u.abreviatura,
                   CONCAT('Vence: ', l.fecha_vencimiento)
            FROM Lote l
            JOIN Producto p ON p.id_producto=l.id_producto
            JOIN Unidad_Medida u ON u.id_unidad=p.id_unidad
            WHERE l.cantidad_actual>0 AND l.fecha_vencimiento IS NOT NULL
              AND l.fecha_vencimiento<=DATE_ADD(CURDATE(),INTERVAL 30 DAY)
            ORDER BY 1, 2
        """, ["ALERTA", "PRODUCTO", "LOTE", "CANTIDAD", "UNIDAD", "DETALLE"])
        tk.Label(self.area, text="Por vencer = dentro de los próximos 30 días. El stock bajo cuenta solo lotes vigentes.",
                 bg=FONDO, fg=GRIS).pack(pady=8)

    def resumen(self):
        self.limpiar()
        self.pantalla_modulo("Resumen general")
        cn = self.db()
        if not cn:
            return
        cur = cn.cursor()
        consultas = [
            ("Productos registrados", "SELECT COUNT(*) FROM Producto"),
            ("Mascotas beneficiarias", "SELECT COUNT(*) FROM Beneficiario"),
            ("Donaciones recibidas", "SELECT COUNT(*) FROM Donacion"),
            ("Programas activos", "SELECT COUNT(*) FROM Programa WHERE fecha_fin IS NULL OR fecha_fin>=CURDATE()"),
            ("Lotes con existencia vigente",
             "SELECT COUNT(*) FROM Lote WHERE cantidad_actual>0 AND (fecha_vencimiento IS NULL OR fecha_vencimiento>=CURDATE())"),
            ("Entregas realizadas a mascotas", "SELECT COUNT(*) FROM Entrega"),
        ]
        caja = tk.Frame(self.area, bg=FONDO)
        caja.pack(fill="x", padx=30, pady=25)
        try:
            for i, (titulo, sql) in enumerate(consultas):
                cur.execute(sql)
                valor = cur.fetchone()[0]
                tarjeta = tk.Frame(caja, bg=BLANCO, padx=22, pady=20, highlightbackground=BORDE, highlightthickness=1)
                tarjeta.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
                tk.Label(tarjeta, text=titulo, bg=BLANCO, fg=GRIS, font=("Arial", 10)).pack()
                tk.Label(tarjeta, text=str(valor), bg=BLANCO, fg=VERDE, font=("Arial", 24, "bold")).pack(pady=7)
            caja.grid_columnconfigure(0, weight=1)
            caja.grid_columnconfigure(1, weight=1)
        finally:
            cur.close()
            cn.close()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = PeluchinApp(ventana)
    ventana.mainloop()