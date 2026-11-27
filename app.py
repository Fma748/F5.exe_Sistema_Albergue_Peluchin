import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta
from decimal import Decimal

from conexion import conectar
from seguridad import autenticar, generar_hash
import validaciones as V
import calculo_alertas as CA

CARPETA = os.path.dirname(os.path.abspath(__file__))
FUENTE = "Segoe UI"
FUENTE_EMOJI = "Segoe UI Emoji"

# ----------------------------------------------------------------------
# Colores (combinan con el logo: fondo negro, líneas blancas)
# ----------------------------------------------------------------------
NEGRO = "#000000"
FONDO = "#FFF8EE"
BLANCO = "#FFFFFF"
NARANJA = "#F2994A"
VERDE = "#23874B"
AZUL = "#2563C9"
CELESTE = "#3B9BD9"
ROSA = "#E0608A"
ROJO = "#C93B3B"
GRIS = "#6B7280"
TEXTO = "#222222"
BORDE = "#E5D9C8"
AYUDA_BG = "#FFF1CC"

# ----------------------------------------------------------------------
# Datos de los formularios (qué se registra en cada pantalla)
# ----------------------------------------------------------------------
# FK_INFO: campo -> (tabla, clave primaria, texto que se muestra)
FK_INFO = {
    "id_categoria": ("Categoria", "id_categoria", "x.nombre"),
    "id_unidad": ("Unidad_Medida", "id_unidad", "CONCAT(x.nombre,' (',x.abreviatura,')')"),
    "id_especie": ("Especie", "id_especie", "x.nombre"),
    "id_raza": ("Raza", "id_raza", "x.nombre"),
    "id_institucion": ("Institucion", "id_institucion", "x.nombre"),
    "id_donante": ("Donante", "id_donante", "x.nombre"),
    "id_cuidado": ("Cuidados_Especiales", "id_cuidado", "x.nombre"),
    "id_mascota": ("Mascota", "id_mascota", "CONCAT(x.nombre,' (',x.codigo,')')"),
}
ENUMS = {
    "tipo_donante": ["PERSONA", "INSTITUCION"],
    "sexo": ["Macho", "Hembra"],
    "rol": ["ADMIN", "OPERADOR"],
    "activo": ["Sí", "No"],
}


def titulo_columna(etiqueta):
    t = etiqueta.split(" (")[0]
    if t in ("Nombre de usuario", "Nombre completo"):
        return {"Nombre de usuario": "Usuario"}.get(t, t)
    if t.startswith("Nombre"):
        return "Nombre"
    return {"Especie a la que sirve": "Especie", "Institución": "Institución"}.get(t, t)


def F(campo, etiqueta, tipo="texto", req=True, **kw):
    """Define un campo del formulario.
    tipo: texto | entero | telefono | decimal | decimal+ | fecha | fk | enum | bool | clave
    valida (solo texto): "letras" = solo letras | "con_letra" = no puede ser solo números
                         | "usuario" = letras, números, punto o guion bajo
    max / min: largo máximo (el de la columna en la base) y mínimo
    no_futura: la fecha no puede ser posterior a hoy
    estadia: la fecha debe caer entre el ingreso y la salida de la mascota elegida"""
    d = dict(campo=campo, etiqueta=etiqueta, tipo=tipo, req=req)
    d.update(kw)
    return d


MODULOS = {
    "Productos": dict(
        tabla="Producto", pk="id_producto", prefijo="PRD", icono="📦",
        buscar=["codigo", "nombre"],
        ayuda="Aquí registras los productos del albergue (alimentos, medicinas, insumos de limpieza...). "
              "El stock mínimo sirve para que el sistema te avise cuando quede poco. "
              "Para sumar o restar cantidades usa «Registrar entrada o salida».",
        campos=[
            F("nombre", "Nombre del producto", valida="con_letra", max=100, min=2),
            F("id_categoria", "Categoría", "fk"),
            F("id_unidad", "Unidad de medida", "fk"),
            F("id_especie", "Especie a la que sirve", "fk", req=False, nulo="Todas"),
            F("stock_minimo", "Stock mínimo (aviso)", "decimal", default="0"),
            F("descripcion", "Descripción", req=False, max=200),
        ],
        virtuales={"stock_minimo": "(SELECT i.stock_minimo FROM Inventario i WHERE i.id_producto=t.id_producto)"},
        extras=[("stock_actual", "Stock total",
                 "(SELECT i.stock_actual FROM Inventario i WHERE i.id_producto=t.id_producto)")],
    ),
    "Categorías de productos": dict(
        tabla="Categoria", pk="id_categoria", prefijo="CAT", icono="🗂",
        buscar=["codigo", "nombre"],
        ayuda="Las categorías agrupan los productos (por ejemplo: Alimento, Medicina, Limpieza). "
              "Se usan al registrar productos y el consumo de las mascotas.",
        campos=[F("nombre", "Nombre de la categoría", valida="con_letra", max=100, min=2),
                F("descripcion", "Descripción", req=False, max=200)],
    ),
    "Unidades de medida": dict(
        tabla="Unidad_Medida", pk="id_unidad", prefijo="UNI", icono="⚖",
        buscar=["codigo", "nombre", "abreviatura"],
        ayuda="Es la forma de medir un producto (kilogramo, bolsa, caja, dosis, litro...). "
              "Escribe el nombre completo y su abreviatura.",
        campos=[F("nombre", "Nombre (ej. Kilogramo)", valida="con_letra", max=50, min=2),
                F("abreviatura", "Abreviatura (ej. kg)", valida="con_letra", max=10)],
    ),
    "Especies": dict(
        tabla="Especie", pk="id_especie", prefijo="ESP", icono="🐾",
        buscar=["codigo", "nombre"],
        ayuda="Tipos de animal que atiende el albergue (Perro, Gato...). "
              "Se eligen al registrar mascotas y razas.",
        campos=[F("nombre", "Nombre de la especie", valida="letras", max=50, min=2)],
    ),
    "Razas": dict(
        tabla="Raza", pk="id_raza", prefijo="RAZ", icono="🐕",
        buscar=["codigo", "nombre"],
        ayuda="Razas de cada especie. Primero elige la especie y luego escribe el nombre de la raza.",
        campos=[F("id_especie", "Especie", "fk"), F("nombre", "Nombre de la raza", valida="letras", max=80, min=2)],
    ),
    "Mascotas": dict(
        tabla="Mascota", pk="id_mascota", prefijo="MAS", icono="🐶",
        buscar=["codigo", "nombre"],
        ayuda="Registro de los animales del albergue. Al elegir la especie, la lista de razas se filtra sola. "
              "Cuando una mascota sale del albergue, edítala y escribe su fecha de salida.",
        campos=[
            F("nombre", "Nombre de la mascota", valida="letras", max=100, min=2),
            F("id_especie", "Especie", "fk"),
            F("id_raza", "Raza", "fk", req=False, depende="id_especie"),
            F("sexo", "Sexo", "enum"),
            F("fecha_nacimiento", "Nacimiento aprox. (AAAA-MM-DD)", "fecha", req=False, no_futura=True),
            F("fecha_ingreso", "Fecha de ingreso (AAAA-MM-DD)", "fecha", hoy=True, no_futura=True),
            F("fecha_salida", "Fecha de salida (AAAA-MM-DD)", "fecha", req=False),
        ],
        extras=[("edad", "Edad (años)", "TIMESTAMPDIFF(YEAR, t.fecha_nacimiento, CURDATE())")],
    ),
    "Consumo por mascota": dict(
        tabla="Beneficiario", pk="cod_beneficiario", col_codigo="cod_beneficiario", prefijo="BEN", icono="🍽",
        buscar=["codigo", "id_mascota"],
        ayuda="Aquí queda anotado qué recibe cada mascota (por ejemplo: 2 kg de alimento). "
              "Estos registros también se crean solos cuando haces una salida de inventario para una mascota.",
        campos=[
            F("id_mascota", "Mascota", "fk"),
            F("id_categoria", "Categoría", "fk"),
            F("fecha", "Fecha (AAAA-MM-DD)", "fecha", hoy=True, no_futura=True, estadia=True),
            F("cantidad", "Cantidad", "decimal+"),
            F("id_unidad", "Unidad de medida", "fk"),
        ],
    ),
    "Cuidados especiales": dict(
        tabla="Cuidados_Especiales", pk="id_cuidado", prefijo="CUI", icono="❤",
        buscar=["codigo", "nombre"],
        ayuda="Programas de atención especial (por ejemplo: Rehabilitación, Adopción, Mascotas en tratamiento). "
              "Las fechas son opcionales.",
        campos=[
            F("nombre", "Nombre del cuidado especial", valida="con_letra", max=120, min=2),
            F("objetivos", "Objetivos", req=False, max=1000),
            F("fecha_inicio", "Inicio (AAAA-MM-DD)", "fecha", req=False),
            F("fecha_fin", "Fin (AAAA-MM-DD)", "fecha", req=False),
        ],
    ),
    "Inscribir mascota en cuidado especial": dict(
        tabla="Mascota_Cuidado", pk="id_mascota_cuidado", prefijo="MCU", icono="📝",
        buscar=["codigo", "id_mascota", "id_cuidado"],
        ayuda="Aquí inscribes una mascota en uno de los cuidados especiales. "
              "Una mascota no puede inscribirse dos veces en el mismo cuidado.",
        campos=[
            F("id_cuidado", "Cuidado especial", "fk"),
            F("id_mascota", "Mascota", "fk"),
            F("fecha_registro", "Fecha de inscripción (AAAA-MM-DD)", "fecha", hoy=True, no_futura=True, estadia=True),
        ],
    ),
    "Donaciones": dict(
        tabla="Donacion", pk="id_donacion", prefijo="DON", icono="🎁",
        buscar=["codigo", "id_donante"],
        ayuda="Registro de las donaciones recibidas: quién donó, cuándo y para qué se destina. "
              "Primero registra al donante en «Donantes».",
        campos=[
            F("id_donante", "Donante", "fk"),
            F("fecha_recepcion", "Fecha de recepción (AAAA-MM-DD)", "fecha", hoy=True, no_futura=True),
            F("destino", "Destino de la donación", valida="con_letra", max=150, min=2),
        ],
    ),
    "Donantes": dict(
        tabla="Donante", pk="id_donante", prefijo="DNT", icono="🤝",
        buscar=["codigo", "nombre"],
        ayuda="Personas o instituciones que donan al albergue. "
              "Si el donante es una INSTITUCION, elige cuál; si es una PERSONA, deja ese campo vacío.",
        campos=[
            F("nombre", "Nombre del donante", valida="con_letra", max=120, min=2),
            F("tipo_donante", "Tipo de donante", "enum"),
            F("telefono", "Teléfono (7 u 8 dígitos)", "telefono", req=False),
            F("id_institucion", "Institución (solo si es INSTITUCION)", "fk", req=False),
        ],
    ),
    "Instituciones": dict(
        tabla="Institucion", pk="id_institucion", prefijo="INS", icono="🏢",
        buscar=["codigo", "nombre"],
        ayuda="Organizaciones que colaboran con el albergue (empresas, fundaciones, colegios...).",
        campos=[
            F("nombre", "Nombre de la institución", valida="con_letra", max=120, min=2),
            F("tipo", "Tipo (empresa, fundación...)", req=False, valida="con_letra", max=50, min=2),
            F("telefono", "Teléfono (7 u 8 dígitos)", "telefono", req=False),
        ],
    ),
    "Usuarios": dict(
        tabla="Usuario", pk="id_usuario", prefijo="USR", icono="👤",
        buscar=["codigo", "nombre_usuario", "nombre_completo"],
        ayuda="Personas que pueden usar el sistema. El ADMIN puede hacerlo todo; el OPERADOR no administra usuarios. "
              "Al editar un usuario, deja la contraseña vacía para conservar la actual.",
        campos=[
            F("nombre_usuario", "Nombre de usuario", valida="usuario", max=50),
            F("contrasena_hash", "Contraseña (mín. 8)", "clave", max=64),
            F("nombre_completo", "Nombre completo", valida="letras", max=120, min=2),
            F("rol", "Rol", "enum", default="OPERADOR"),
            F("activo", "¿Está activo?", "bool", default="Sí"),
        ],
    ),
}

# Productos con su existencia vigente (sin contar lotes vencidos)
SQL_PRODUCTOS = """
    SELECT p.id_producto,
           CONCAT(p.nombre, ' [', u.abreviatura, ']  disponible: ',
                  COALESCE(SUM(CASE WHEN l.fecha_vencimiento IS NULL
                                      OR l.fecha_vencimiento >= CURDATE()
                                    THEN l.cantidad_actual END), 0))
    FROM Producto p
    JOIN Unidad_Medida u ON u.id_unidad = p.id_unidad
    LEFT JOIN Lote l ON l.id_producto = p.id_producto
    GROUP BY p.id_producto, p.nombre, u.abreviatura
    ORDER BY p.nombre
"""

CONCEPTOS_ENTRADA = ["Compra", "Donación", "Devolución", "Otro"]
CONCEPTOS_SALIDA = ["Alimentación de mascotas", "Atención veterinaria", "Entrega a institución",
                    "Baja por vencimiento", "Otro"]


# ----------------------------------------------------------------------
# Utilidades generales
# ----------------------------------------------------------------------
def siguiente_codigo(cur, tabla, columna, prefijo):
    """Código automático: PRD-0001, PRD-0002..."""
    cur.execute(f"SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(`{columna}`,'-',-1) AS UNSIGNED)),0)+1 "
                f"FROM `{tabla}`")
    return f"{prefijo}-{int(cur.fetchone()[0]):04d}"


def texto_error(e):
    n = getattr(e, "errno", None)
    msg = getattr(e, "msg", str(e))
    if n == 1062:
        return "Ya existe un registro con esos datos (nombre o código repetido)."
    if n == 1451:
        return "No se puede eliminar: este registro se usa en otras partes del sistema."
    if n == 1452:
        return "Uno de los datos elegidos ya no existe. Actualiza la lista e inténtalo otra vez."
    if n == 1406:
        return "Uno de los textos es demasiado largo. Acórtalo e inténtalo otra vez."
    if n in (1264, 1690):
        return "Una cantidad es demasiado grande para guardarse."
    if n == 1292:
        return "Una fecha no es válida. Usa el formato AAAA-MM-DD con una fecha que exista."
    if n in (3819, 4025):
        for regla, texto in V.MENSAJES_REGLAS.items():
            if f"`{regla}`" in msg or f"'{regla}'" in msg:
                return texto
        if "_rango" in msg:
            return f"Las fechas deben estar entre {V.FECHA_MIN.year} y {V.FECHA_MAX.year}."
        return "Algún valor no cumple las reglas (cantidades o fechas incorrectas)."
    if n == 1644:
        return msg
    return str(e)


def mezclar(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def boton(parent, texto, comando, bg=VERDE, fg=BLANCO, padx=16, pady=8, size=10):
    b = tk.Button(parent, text=texto, command=comando, bg=bg, fg=fg,
                  activebackground=mezclar(bg, NEGRO, .18), activeforeground=fg,
                  relief="flat", bd=0, cursor="hand2", padx=padx, pady=pady,
                  font=(FUENTE, size, "bold"), disabledforeground="#DDDDDD")
    b.bind("<Enter>", lambda e: b["state"] == "normal" and b.configure(bg=mezclar(bg, NEGRO, .12)))
    b.bind("<Leave>", lambda e: b["state"] == "normal" and b.configure(bg=bg))
    return b


class Accion(tk.Frame):
    """Botón grande con icono, título y una línea que explica para qué sirve."""

    def __init__(self, parent, icono, titulo, descripcion, comando, color):
        super().__init__(parent, bg=BLANCO, cursor="hand2",
                         highlightbackground=BORDE, highlightthickness=1)
        self.comando = comando
        self.tinte = mezclar(color, BLANCO, .82)
        self.normal = BLANCO
        tk.Label(self, text=icono, bg=BLANCO, fg=color,
                 font=(FUENTE_EMOJI, 16), width=2).pack(side="left", padx=(6, 0), pady=8)
        caja = tk.Frame(self, bg=BLANCO)
        caja.pack(side="left", fill="x", expand=True, padx=(2, 8), pady=5)
        tk.Label(caja, text=titulo, bg=BLANCO, fg=NEGRO, anchor="w", justify="left",
                 wraplength=185, font=(FUENTE, 10, "bold")).pack(fill="x")
        tk.Label(caja, text=descripcion, bg=BLANCO, fg=GRIS, anchor="w", justify="left",
                 wraplength=185, font=(FUENTE, 8)).pack(fill="x")
        for w in self.winfo_children():
            self._enlazar(w)

    def _enlazar(self, w):
        w.bind("<Button-1>", lambda e: self.comando())
        w.bind("<Enter>", lambda e: self._fondo(self.tinte))
        w.bind("<Leave>", lambda e: self._fondo(self.normal))
        for h in w.winfo_children():
            self._enlazar(h)

    def _fondo(self, color):
        self.configure(bg=color)
        for w in self._todos(self):
            try:
                w.configure(bg=color)
            except tk.TclError:
                pass

    def _todos(self, w):
        for h in w.winfo_children():
            yield h
            yield from self._todos(h)


# ----------------------------------------------------------------------
# Aplicación
# ----------------------------------------------------------------------
class PeluchinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Albergue de Mascotas Peluchin | Inventario y Suministros")
        ancho, alto = 1240, 700
        x = max((root.winfo_screenwidth() - ancho) // 2, 0)
        y = max((root.winfo_screenheight() - alto) // 2 - 20, 0)
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.root.minsize(1100, 620)
        self.usuario = None
        self.logos = {}
        for nombre in ("grande", "pequeno", "mini"):
            ruta = os.path.join(CARPETA, "imagenes", f"logo_{nombre}.png")
            try:
                self.logos[nombre] = tk.PhotoImage(file=ruta)
            except tk.TclError:
                self.logos[nombre] = None
        self.estilos()
        self.construir_login()

    # ------------------------------------------------------------------
    def estilos(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")
        s.configure("Treeview", rowheight=28, font=(FUENTE, 10), background=BLANCO,
                    fieldbackground=BLANCO, foreground=TEXTO, borderwidth=0)
        s.configure("Treeview.Heading", background=NEGRO, foreground=BLANCO,
                    font=(FUENTE, 10, "bold"), relief="flat", padding=7)
        s.map("Treeview.Heading", background=[("active", "#333333")])
        s.map("Treeview", background=[("selected", NARANJA)], foreground=[("selected", NEGRO)])
        s.configure("TEntry", padding=6, font=(FUENTE, 10))
        s.configure("TCombobox", padding=6, font=(FUENTE, 10))
        s.map("TCombobox", fieldbackground=[("readonly", BLANCO), ("disabled", "#EEEEEE")],
              foreground=[("readonly", TEXTO)])
        self.root.option_add("*TCombobox*Listbox.font", (FUENTE, 10))
        s.configure("Vertical.TScrollbar", background=BORDE, troughcolor=FONDO, borderwidth=0)

    def db(self):
        cn = conectar()
        if cn is None:
            messagebox.showerror("Base de datos", "No se pudo conectar a MySQL.\n"
                                                   "Revisa conexion.py y que MySQL esté iniciado.")
        return cn

    def limpiar(self):
        for w in self.root.winfo_children():
            w.destroy()
        for tecla in ("<Left>", "<Right>"):      # las usa la pantalla «Cálculo de las alertas»
            self.root.unbind(tecla)

    def opciones(self, sql, params=(), vacio=False):
        """Lista 'id - texto' para los desplegables."""
        datos = []
        cn = self.db()
        if cn is not None:
            cur = cn.cursor()
            try:
                cur.execute(sql, params)
                datos = [f"{f[0]} - {f[1]}" for f in cur.fetchall()]
            except Exception as e:
                messagebox.showerror("Consulta", texto_error(e))
            finally:
                cur.close()
                cn.close()
        return ([""] + datos) if vacio else datos

    def opciones_fk(self, campo, padre=None, vacio=False):
        ref, pkr, txt = FK_INFO[campo]
        if campo == "id_raza":
            if padre is None:
                return [""] if vacio else []
            return self.opciones(f"SELECT x.{pkr}, {txt} FROM {ref} x WHERE x.id_especie=%s ORDER BY 2",
                                 (padre,), vacio)
        return self.opciones(f"SELECT x.{pkr}, {txt} FROM {ref} x ORDER BY 2", (), vacio)

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
            f = datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"{nombre}: usa el formato AAAA-MM-DD con una fecha que exista "
                             f"(ejemplo 2026-11-16).")
        return V.revisar_rango_fecha(f, nombre)

    def revisar_estadia(self, id_mascota, fecha, nombre):
        """La fecha debe caer mientras la mascota estuvo en el albergue."""
        cn = self.db()
        if cn is None:
            return
        cur = cn.cursor()
        try:
            cur.execute("SELECT fecha_ingreso, fecha_salida FROM Mascota WHERE id_mascota=%s", (id_mascota,))
            fila = cur.fetchone()
        finally:
            cur.close()
            cn.close()
        if fila:
            ingreso, salida = fila
            if fecha < ingreso.isoformat():
                raise ValueError(f"{nombre}: no puede ser anterior al ingreso de la mascota ({ingreso}).")
            if salida and fecha > salida.isoformat():
                raise ValueError(f"{nombre}: no puede ser posterior a la salida de la mascota ({salida}).")

    @staticmethod
    def leer_cantidad(texto, nombre="La cantidad", permitir_cero=False):
        return V.leer_cantidad(texto, nombre, permitir_cero)

    def filtrar(self, widget, filtro):
        """Corrige el texto del campo mientras se escribe, se pega o se carga
        (ej. el teléfono nunca pasa de 8 dígitos). Funciona con Entry y Combobox."""
        var = tk.StringVar(master=self.root, value=widget.get())
        widget.configure(textvariable=var)

        def corregir(*_):
            actual = var.get()
            bueno = filtro(actual)
            if bueno != actual:
                var.set(bueno)
                widget.icursor("end")
        var.trace_add("write", corregir)
        widget._filtro_var = var          # que no lo borre el recolector de basura
        return widget

    def entrada(self, padre, tipo="texto", width=30, show="", valida=None, maximo=None):
        w = ttk.Entry(padre, width=width, show=show)
        if tipo == "telefono":
            filtro = V.filtro_digitos(V.TELEFONO_MAX)
        elif tipo == "entero":
            filtro = V.filtro_digitos(maximo or 10)
        elif tipo in ("decimal", "decimal+"):
            filtro = V.filtro_decimal
        elif tipo == "fecha":
            filtro = V.filtro_fecha
        elif valida == "letras":
            filtro = V.filtro_letras(maximo or 100)
        elif valida == "usuario":
            filtro = V.filtro_usuario(maximo or V.USUARIO_MAX)
        else:
            filtro = V.filtro_texto(maximo or 200)
        return self.filtrar(w, filtro)

    # ------------------------------------------------------------------
    # Inicio de sesión
    # ------------------------------------------------------------------
    def construir_login(self):
        self.limpiar()
        self.root.configure(bg=FONDO)
        izq = tk.Frame(self.root, bg=NEGRO, width=470)
        izq.pack(side="left", fill="y")
        izq.pack_propagate(False)
        centro = tk.Frame(izq, bg=NEGRO)
        centro.place(relx=.5, rely=.5, anchor="center")
        if self.logos["grande"]:
            tk.Label(centro, image=self.logos["grande"], bg=NEGRO).pack()
        else:
            tk.Label(centro, text="PELUCHIN", bg=NEGRO, fg=BLANCO, font=(FUENTE, 28, "bold")).pack()
        tk.Label(centro, text="Sistema de Inventario y Suministros", bg=NEGRO, fg=NARANJA,
                 font=(FUENTE, 12, "bold")).pack(pady=(14, 2))
        tk.Label(centro, text="Cuidando a quienes nos necesitan", bg=NEGRO, fg="#BBBBBB",
                 font=(FUENTE, 10, "italic")).pack()

        der = tk.Frame(self.root, bg=FONDO)
        der.pack(side="left", fill="both", expand=True)
        tarjeta = tk.Frame(der, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        tarjeta.place(relx=.5, rely=.5, anchor="center", width=400, height=420)
        tk.Frame(tarjeta, bg=NARANJA, height=6).pack(fill="x")
        tk.Label(tarjeta, text="Iniciar sesión", bg=BLANCO, fg=NEGRO,
                 font=(FUENTE, 20, "bold")).pack(pady=(26, 2))
        tk.Label(tarjeta, text="Escribe tu usuario y contraseña para entrar", bg=BLANCO, fg=GRIS,
                 font=(FUENTE, 10)).pack(pady=(0, 20))
        tk.Label(tarjeta, text="👤  Usuario", bg=BLANCO, fg=TEXTO,
                 font=(FUENTE, 10, "bold")).pack(anchor="w", padx=40)
        self.in_usuario = self.filtrar(ttk.Entry(tarjeta, width=34), V.filtro_texto(V.USUARIO_MAX))
        self.in_usuario.pack(pady=(4, 12), padx=40, fill="x")
        tk.Label(tarjeta, text="🔒  Contraseña", bg=BLANCO, fg=TEXTO,
                 font=(FUENTE, 10, "bold")).pack(anchor="w", padx=40)
        self.in_clave = self.filtrar(ttk.Entry(tarjeta, width=34, show="•"), V.filtro_texto(128))
        self.in_clave.pack(pady=(4, 6), padx=40, fill="x")
        self.in_clave.bind("<Return>", lambda e: self.entrar())
        self.in_usuario.bind("<Return>", lambda e: self.in_clave.focus())
        ver = tk.BooleanVar(value=False)
        tk.Checkbutton(tarjeta, text="Mostrar contraseña", variable=ver, bg=BLANCO, fg=GRIS,
                       activebackground=BLANCO, font=(FUENTE, 9), cursor="hand2",
                       bd=0, highlightthickness=0,
                       command=lambda: self.in_clave.configure(show="" if ver.get() else "•")
                       ).pack(anchor="w", padx=36, pady=(0, 16))
        boton(tarjeta, "INGRESAR AL SISTEMA", self.entrar, bg=NARANJA, fg=NEGRO,
              pady=11, size=11).pack(fill="x", padx=40)
        tk.Label(tarjeta, text="Si no tienes usuario, pídeselo al administrador.", bg=BLANCO,
                 fg=GRIS, font=(FUENTE, 9)).pack(pady=16)
        self.in_usuario.focus()

    def entrar(self):
        usuario = self.in_usuario.get().strip()
        clave = self.in_clave.get()
        if not usuario or not clave:
            messagebox.showwarning("Acceso", "Escribe tu usuario y tu contraseña.")
            return
        datos = autenticar(usuario, clave)
        if not datos:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos, o cuenta inactiva.")
            return
        self.usuario = datos
        self.inicio()

    def cerrar_sesion(self):
        self.usuario = None
        self.construir_login()

    # ------------------------------------------------------------------
    # Inicio (menú principal)
    # ------------------------------------------------------------------
    def barra_superior(self, titulo, subtitulo, con_volver):
        barra = tk.Frame(self.root, bg=NEGRO)
        barra.pack(fill="x")
        logo = self.logos["pequeno"] if not con_volver else self.logos["mini"]
        if logo:
            lg = tk.Label(barra, image=logo, bg=NEGRO, cursor="hand2")
            lg.pack(side="left", padx=(16, 8), pady=6)
            lg.bind("<Button-1>", lambda e: self.inicio())
        txt = tk.Frame(barra, bg=NEGRO)
        txt.pack(side="left", pady=6)
        tk.Label(txt, text=titulo, bg=NEGRO, fg=BLANCO, anchor="w",
                 font=(FUENTE, 20 if not con_volver else 17, "bold")).pack(anchor="w")
        tk.Label(txt, text=subtitulo, bg=NEGRO, fg="#BBBBBB", anchor="w",
                 font=(FUENTE, 10)).pack(anchor="w")
        der = tk.Frame(barra, bg=NEGRO)
        der.pack(side="right", padx=18)
        if con_volver:
            boton(der, "⬅  VOLVER AL INICIO", self.inicio, bg=NARANJA, fg=NEGRO,
                  pady=9, size=10).pack(side="right")
        else:
            boton(der, "Cerrar sesión", self.cerrar_sesion, bg="#333333", pady=6, size=9).pack(side="right", padx=(12, 0))
            tk.Label(der, text=f"👤  {self.usuario['nombre']}", bg=NEGRO, fg=BLANCO,
                     font=(FUENTE, 11, "bold")).pack(anchor="e")
            tk.Label(der, text=f"Rol: {self.usuario['rol']}", bg=NEGRO, fg=NARANJA,
                     font=(FUENTE, 9)).pack(anchor="e")
        tk.Frame(self.root, bg=NARANJA, height=4).pack(fill="x")

    def conteo_alertas(self):
        cn = self.db()
        if cn is None:
            return None
        cur = cn.cursor()
        try:
            cur.execute("""
                SELECT COUNT(*) FROM (
                  SELECT i.id_producto FROM Inventario i
                  LEFT JOIN Lote l ON l.id_producto=i.id_producto
                  GROUP BY i.id_producto, i.stock_minimo
                  HAVING i.stock_minimo>0 AND
                         COALESCE(SUM(CASE WHEN l.fecha_vencimiento IS NULL OR l.fecha_vencimiento>=CURDATE()
                                           THEN l.cantidad_actual END),0) <= i.stock_minimo
                ) z""")
            bajo = cur.fetchone()[0]
            cur.execute("""SELECT COUNT(*) FROM Lote WHERE cantidad_actual>0 AND fecha_vencimiento IS NOT NULL
                           AND fecha_vencimiento>=CURDATE()
                           AND fecha_vencimiento<=DATE_ADD(CURDATE(),INTERVAL 30 DAY)""")
            por_vencer = cur.fetchone()[0]
            cur.execute("""SELECT COUNT(*) FROM Lote WHERE cantidad_actual>0
                           AND fecha_vencimiento IS NOT NULL AND fecha_vencimiento<CURDATE()""")
            vencidos = cur.fetchone()[0]
            return bajo, por_vencer, vencidos
        except Exception:
            return None
        finally:
            cur.close()
            cn.close()

    def inicio(self):
        self.limpiar()
        self.root.configure(bg=FONDO)
        self.barra_superior("Sistema de Inventario y Suministros",
                            "Albergue de Mascotas «Peluchin»  •  Elige qué quieres hacer", False)

        # Franja de alertas
        datos = self.conteo_alertas()
        if datos is None or sum(datos) == 0:
            texto, color = "✔  Todo en orden: no hay productos con poco stock ni lotes por vencer.", VERDE
        else:
            b, p, v = datos
            partes = []
            if b:
                partes.append(f"{b} producto(s) con poco stock")
            if p:
                partes.append(f"{p} lote(s) por vencer en 30 días")
            if v:
                partes.append(f"{v} lote(s) vencido(s)")
            texto, color = "⚠  Atención: " + "  •  ".join(partes) + "   (clic para ver el detalle)", ROJO
        franja = tk.Label(self.root, text=texto, bg=color, fg=BLANCO, font=(FUENTE, 10, "bold"),
                          pady=8, cursor="hand2")
        franja.pack(fill="x")
        franja.bind("<Button-1>", lambda e: self.alertas())

        cuerpo = tk.Frame(self.root, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=18, pady=(14, 6))
        secciones = [
            ("📦  INVENTARIO", "Lo que hay en bodega y lo que entra o sale", NARANJA, [
                ("🔄", "Registrar entrada o salida", "Ingreso de productos o entrega a mascotas", "mov"),
                ("📋", "Existencias", "Cuánto hay de cada producto", "existencias"),
                ("🏷", "Lotes y vencimientos", "Cantidades y fechas de vencimiento", "lotes"),
                ("🕘", "Historial de movimientos", "Todas las entradas y salidas", "historial"),
                ("📦", "Productos", "Crear y editar los productos", "Productos"),
            ]),
            ("🐶  MASCOTAS", "Los animales que viven en el albergue", CELESTE, [
                ("🐶", "Mascotas", "Registrar y editar cada mascota", "Mascotas"),
                ("🍽", "Consumo por mascota", "Lo que recibe cada mascota", "Consumo por mascota"),
                ("❤", "Cuidados especiales", "Programas de atención especial", "Cuidados especiales"),
                ("📝", "Inscribir en un cuidado", "Asignar una mascota a un cuidado especial",
                 "Inscribir mascota en cuidado especial"),
            ]),
            ("🎁  DONACIONES", "Las personas e instituciones que ayudan", ROSA, [
                ("🎁", "Donaciones recibidas", "Registrar y consultar donaciones", "Donaciones"),
                ("🤝", "Donantes", "Personas o instituciones que donan", "Donantes"),
                ("🏢", "Instituciones", "Empresas y fundaciones aliadas", "Instituciones"),
            ]),
            ("⚙  LISTAS Y USUARIOS", "Opciones de los menús y accesos al sistema", VERDE, [
                ("🗂", "Categorías de productos", "Alimento, medicina, limpieza...", "Categorías de productos"),
                ("⚖", "Unidades de medida", "kg, bolsa, caja, dosis...", "Unidades de medida"),
                ("🐾", "Especies", "Perro, gato...", "Especies"),
                ("🐕", "Razas", "Razas de cada especie", "Razas"),
                ("👤", "Usuarios", "Quién puede usar el sistema", "Usuarios"),
            ]),
        ]
        for c in range(4):
            cuerpo.grid_columnconfigure(c, weight=1, uniform="col")
        for c, (titulo, desc, color, acciones) in enumerate(secciones):
            tarj = tk.Frame(cuerpo, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
            tarj.grid(row=0, column=c, sticky="nsew", padx=6)
            tk.Frame(tarj, bg=color, height=7).pack(fill="x")
            cab = tk.Frame(tarj, bg=BLANCO)
            cab.pack(fill="x", padx=12, pady=(10, 0))
            icono_s, nombre_s = titulo.split("  ", 1)
            tk.Label(cab, text=icono_s, bg=BLANCO, fg=color, font=(FUENTE_EMOJI, 14)).pack(side="left")
            tk.Label(cab, text=nombre_s, bg=BLANCO, fg=NEGRO, anchor="w",
                     font=(FUENTE, 12, "bold")).pack(side="left", padx=(6, 0))
            tk.Label(tarj, text=desc, bg=BLANCO, fg=GRIS, anchor="w", justify="left", wraplength=250,
                     font=(FUENTE, 9)).pack(fill="x", padx=12, pady=(0, 8))
            for icono, nombre, d, destino in acciones:
                if destino == "Usuarios" and self.usuario["rol"] != "ADMIN":
                    continue
                Accion(tarj, icono, nombre, d, lambda dst=destino: self.abrir(dst), color
                       ).pack(fill="x", padx=10, pady=4)
            tk.Frame(tarj, bg=BLANCO, height=6).pack()

        pie = tk.Frame(self.root, bg=FONDO)
        pie.pack(fill="x", padx=24, pady=(8, 14))
        boton(pie, "🚨  ALERTAS: STOCK BAJO Y VENCIMIENTOS", self.alertas, bg=ROJO, pady=10).pack(side="left", padx=4)
        boton(pie, "📐  CÁLCULO DE LAS ALERTAS", self.calculo_alertas, bg="#7C4DC4", pady=10).pack(side="left", padx=4)
        boton(pie, "📊  RESUMEN GENERAL", self.resumen, bg=NEGRO, pady=10).pack(side="left", padx=4)

    def abrir(self, destino):
        if destino == "Usuarios" and self.usuario["rol"] != "ADMIN":
            messagebox.showwarning("Acceso restringido", "Solo un ADMIN puede administrar usuarios.")
            return
        if destino in MODULOS:
            self.crud(destino)
        elif destino == "mov":
            self.form_movimientos()
        elif destino == "existencias":
            self.existencias()
        elif destino == "lotes":
            self.lotes()
        elif destino == "historial":
            self.historial()

    def pantalla_modulo(self, titulo, ayuda="", icono=""):
        self.root.configure(bg=FONDO)
        self.barra_superior(f"{icono}  {titulo}".strip(), "Sistema de Inventario y Suministros", True)
        if ayuda:
            banda = tk.Frame(self.root, bg=AYUDA_BG)
            banda.pack(fill="x")
            tk.Label(banda, text="ℹ  " + ayuda, bg=AYUDA_BG, fg="#5B4A00", justify="left", anchor="w",
                     wraplength=1160, font=(FUENTE, 10)).pack(fill="x", padx=20, pady=8)
        self.area = tk.Frame(self.root, bg=FONDO)
        self.area.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Pantallas de registro (altas, cambios y bajas)
    # ------------------------------------------------------------------
    def crud(self, clave):
        m = MODULOS[clave]
        tabla, pk, pref = m["tabla"], m["pk"], m["prefijo"]
        col_cod = m.get("col_codigo", "codigo")
        campos_def = m["campos"]
        campos = [f["campo"] for f in campos_def]
        virtuales = m.get("virtuales", {})
        extras = m.get("extras", [])
        fks = [f["campo"] for f in campos_def if f["tipo"] == "fk"]

        self.limpiar()
        self.pantalla_modulo(clave, m["ayuda"], m["icono"])
        cont = self.area

        # ---------------- Formulario ----------------
        tarjeta = tk.Frame(cont, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        tarjeta.pack(fill="x", padx=20, pady=(12, 6))
        lbl_modo = tk.Label(tarjeta, text="", bg=BLANCO, fg=NEGRO, font=(FUENTE, 12, "bold"), anchor="w")
        lbl_modo.pack(fill="x", padx=14, pady=(10, 0))
        form = tk.Frame(tarjeta, bg=BLANCO)
        form.pack(fill="x", padx=14, pady=(2, 8))
        for c in range(3):
            form.grid_columnconfigure(c, weight=1, uniform="f")

        widgets = {}
        for i, f in enumerate(campos_def):
            etiqueta = f["etiqueta"] + (" *" if f["req"] else "  (opcional)")
            tk.Label(form, text=etiqueta, bg=BLANCO, fg=TEXTO, font=(FUENTE, 9, "bold"), anchor="w").grid(
                row=i // 3 * 2, column=i % 3, sticky="w", padx=6, pady=(6, 0))
            t = f["tipo"]
            if t == "fk":
                w = ttk.Combobox(form, state="readonly", width=30,
                                 values=[] if f.get("depende") else self.opciones_fk(f["campo"], vacio=not f["req"]))
            elif t == "enum":
                w = ttk.Combobox(form, state="readonly", width=30, values=ENUMS[f["campo"]])
            elif t == "bool":
                w = ttk.Combobox(form, state="readonly", width=30, values=ENUMS["activo"])
            else:
                w = self.entrada(form, t, 32, show="•" if t == "clave" else "",
                                 valida=f.get("valida"), maximo=f.get("max"))
            w.grid(row=i // 3 * 2 + 1, column=i % 3, sticky="ew", padx=6, pady=(2, 4))
            widgets[f["campo"]] = w

        # La raza depende de la especie elegida
        for f in campos_def:
            if f.get("depende"):
                padre, hijo = widgets[f["depende"]], widgets[f["campo"]]

                def recargar(event=None, padre=padre, hijo=hijo, campo=f["campo"], req=f["req"]):
                    hijo.set("")
                    hijo["values"] = self.opciones_fk(campo, self.id_de(padre.get()), vacio=not req)
                padre.bind("<<ComboboxSelected>>", recargar)

        # ---------------- Botones y buscador ----------------
        barra = tk.Frame(cont, bg=FONDO)
        barra.pack(fill="x", padx=20, pady=4)
        buscar = tk.StringVar()
        caja = tk.Frame(cont, bg=FONDO)

        # ---------------- Tabla ----------------
        cols = ["_pk", "codigo"] + campos + [e[0] for e in extras] + ["_fk_" + c for c in fks]
        visibles = ["codigo"] + campos + [e[0] for e in extras]
        tv = ttk.Treeview(caja, columns=cols, displaycolumns=visibles, show="headings", height=11)
        sb = ttk.Scrollbar(caja, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.heading("codigo", text="CÓDIGO")
        tv.column("codigo", width=95, anchor="w", stretch=False)
        for f in campos_def:
            nombre_col = titulo_columna(f["etiqueta"]).upper()
            tv.heading(f["campo"], text=nombre_col)
            tv.column(f["campo"], width=max(120, len(nombre_col) * 10 + 28), anchor="w")
        for nombre, titulo, _ in extras:
            tv.heading(nombre, text=titulo.upper())
            tv.column(nombre, width=100, anchor="center")
        tv.tag_configure("par", background=BLANCO)
        tv.tag_configure("impar", background="#FFF4E5")
        sb.pack(side="right", fill="y")
        tv.pack(side="left", fill="both", expand=True)

        estado = {"id": None, "filas": []}

        def expr_campo(f):
            c, t = f["campo"], f["tipo"]
            if t == "fk":
                ref, pkr, txt = FK_INFO[c]
                e = f"(SELECT {txt} FROM {ref} x WHERE x.{pkr}=t.`{c}`)"
                return f"COALESCE({e},'{f['nulo']}')" if f.get("nulo") else e
            if t == "bool":
                return f"IF(t.`{c}`,'Sí','No')"
            if t == "clave":
                return "'••••••••'"
            if c in virtuales:
                return virtuales[c]
            return f"t.`{c}`"

        def poner(campo, texto):
            w = widgets[campo]
            if isinstance(w, ttk.Combobox):
                w.set(texto)
            else:
                w.delete(0, "end")
                w.insert(0, texto)

        def limpiar_form():
            estado["id"] = None
            lbl_modo.configure(text="🆕  Nuevo registro  —  llena los datos y presiona «Guardar»")
            for f in campos_def:
                defecto = f.get("default", date.today().isoformat() if f.get("hoy") else "")
                poner(f["campo"], defecto)
                if f.get("depende"):
                    widgets[f["campo"]]["values"] = []
            tv.selection_remove(tv.selection())

        # El buscador solo mira estos atributos (y el mensaje junto a la caja lo dice)
        campos_busqueda = m.get("buscar", ["codigo", "nombre"])
        cols_busqueda = [cols.index(c) for c in campos_busqueda]
        nombres_busqueda = ["código" if c == "codigo" else
                            next(f["etiqueta"] for f in campos_def if f["campo"] == c).split(" (")[0].lower()
                            for c in campos_busqueda]
        texto_busqueda = "Busca por: " + (", ".join(nombres_busqueda[:-1]) + " o " + nombres_busqueda[-1]
                                          if len(nombres_busqueda) > 1 else nombres_busqueda[0])

        def mostrar(*_):
            for i in tv.get_children():
                tv.delete(i)
            filtro = buscar.get().strip().lower()
            n = 0
            for fila in estado["filas"]:
                if filtro and not any(filtro in str(fila[i]).lower() for i in cols_busqueda):
                    continue
                tv.insert("", "end", values=fila, tags=("par" if n % 2 == 0 else "impar",))
                n += 1
            if filtro:
                lbl_busqueda.configure(text=f"{texto_busqueda}   ·   {n} resultado(s)" if n else
                                       f"{texto_busqueda}   ·   Sin resultados para «{buscar.get().strip()}»",
                                       fg=GRIS if n else ROJO)
            else:
                lbl_busqueda.configure(text=texto_busqueda, fg=GRIS)

        def cargar():
            sel = [f"t.`{pk}`", f"t.`{col_cod}`"] + [expr_campo(f) for f in campos_def] \
                  + [e[2] for e in extras] + [f"t.`{c}`" for c in fks]
            cn = self.db()
            if not cn:
                return
            cur = cn.cursor()
            try:
                cur.execute(f"SELECT {', '.join(sel)} FROM `{tabla}` t ORDER BY t.`{pk}` DESC")
                estado["filas"] = [["" if v is None else v for v in fila] for fila in cur.fetchall()]
            except Exception as e:
                messagebox.showerror("Consulta", texto_error(e))
            finally:
                cur.close()
                cn.close()
            mostrar()

        def elegir(event=None):
            sel = tv.selection()
            if not sel:
                return
            fila = dict(zip(cols, tv.item(sel[0], "values")))
            estado["id"] = fila["_pk"]
            lbl_modo.configure(text=f"✏  Editando el registro {fila['codigo']}  —  cambia los datos y presiona "
                                    f"«Guardar», o «Nuevo» para cancelar")
            for f in campos_def:
                c, t = f["campo"], f["tipo"]
                if t == "clave":
                    poner(c, "")
                elif t == "fk":
                    idv = str(fila["_fk_" + c])
                    if f.get("depende"):
                        po = widgets[f["depende"]].get()
                        padre_id = self.id_de(po) if po else None
                        widgets[c]["values"] = self.opciones_fk(c, padre_id, vacio=not f["req"])
                    opts = list(widgets[c]["values"])
                    poner(c, next((o for o in opts if o.split(" - ")[0] == idv), ""))
                else:
                    poner(c, str(fila[c]))
        tv.bind("<<TreeviewSelect>>", elegir)

        def guardar():
            try:
                valores = {}
                for f in campos_def:
                    c, t = f["campo"], f["tipo"]
                    texto = widgets[c].get().strip()
                    et = f["etiqueta"].split(" (")[0]
                    if t == "clave":
                        if texto:
                            if not 8 <= len(texto) <= 64:
                                raise ValueError("La contraseña debe tener entre 8 y 64 caracteres.")
                            valores[c] = generar_hash(texto)
                        elif estado["id"] is not None:
                            valores[c] = None          # conservar la contraseña actual
                        else:
                            raise ValueError("La contraseña es obligatoria para un usuario nuevo.")
                        continue
                    if texto == "":
                        if f["req"]:
                            raise ValueError(f"Completa el campo: {et}.")
                        valores[c] = None
                        continue
                    if t == "fk":
                        valores[c] = self.id_de(texto)
                    elif t == "fecha":
                        fecha = self.leer_fecha(texto, et)
                        if f.get("no_futura") and fecha > date.today():
                            raise ValueError(f"{et}: no puede ser una fecha futura (hoy es {date.today()}).")
                        valores[c] = fecha.isoformat()
                    elif t == "telefono":
                        if not V.es_telefono(texto):
                            raise ValueError(f"{et}: debe tener {V.TELEFONO_MIN} u {V.TELEFONO_MAX} dígitos, "
                                             f"solo números (escribiste {len(texto)}).")
                        valores[c] = texto
                    elif t == "entero":
                        if not texto.isdigit():
                            raise ValueError(f"{et}: escribe solo números.")
                        valores[c] = texto
                    elif t == "decimal":
                        valores[c] = self.leer_cantidad(texto, et, permitir_cero=True)
                    elif t == "decimal+":
                        valores[c] = self.leer_cantidad(texto, et)
                    elif t == "bool":
                        valores[c] = 1 if texto == "Sí" else 0
                    elif t == "enum" and c in ("rol", "tipo_donante"):
                        valores[c] = texto.upper()
                    else:
                        texto = " ".join(texto.split())          # sin espacios dobles
                        regla, minimo = f.get("valida"), f.get("min", 0)
                        if len(texto) > f.get("max", 200):
                            raise ValueError(f"{et}: máximo {f.get('max', 200)} caracteres.")
                        if regla == "letras" and not V.es_solo_letras(texto):
                            raise ValueError(f"{et}: solo puede tener letras (sin números ni símbolos).")
                        if regla == "con_letra" and not V.tiene_letra(texto):
                            raise ValueError(f"{et}: no puede ser solo números; escribe un texto con letras.")
                        if regla == "usuario" and not V.es_usuario(texto):
                            raise ValueError(f"{et}: de {V.USUARIO_MIN} a {V.USUARIO_MAX} caracteres; "
                                             "solo letras sin tilde, números, punto o guion bajo (sin espacios).")
                        if len(texto) < minimo:
                            raise ValueError(f"{et}: debe tener al menos {minimo} caracteres.")
                        valores[c] = texto

                # Reglas del negocio
                if tabla == "Donante":
                    if valores["tipo_donante"] == "INSTITUCION" and valores["id_institucion"] is None:
                        raise ValueError("Para un donante INSTITUCION elige la institución.")
                    if valores["tipo_donante"] == "PERSONA" and valores["id_institucion"] is not None:
                        raise ValueError("Una PERSONA no lleva institución; deja ese campo vacío.")
                if tabla == "Mascota":
                    hoy = date.today().isoformat()
                    nac, ing, sal = valores["fecha_nacimiento"], valores["fecha_ingreso"], valores["fecha_salida"]
                    if nac and nac > hoy:
                        raise ValueError(f"La fecha de nacimiento no puede ser futura (hoy es {hoy}).")
                    if ing > hoy:
                        raise ValueError(f"La fecha de ingreso no puede ser futura (hoy es {hoy}).")
                    if nac and nac > ing:
                        raise ValueError("La fecha de nacimiento no puede ser posterior a la de ingreso.")
                    if sal and nac and sal < nac:
                        raise ValueError("La fecha de salida no puede ser anterior a la de nacimiento.")
                    if sal and sal < ing:
                        raise ValueError("La fecha de salida no puede ser anterior a la de ingreso.")
                for f in campos_def:
                    if f.get("estadia") and valores.get(f["campo"]):
                        self.revisar_estadia(valores["id_mascota"], valores[f["campo"]],
                                             f["etiqueta"].split(" (")[0])
                if tabla == "Cuidados_Especiales" and valores["fecha_inicio"] and valores["fecha_fin"] \
                        and valores["fecha_fin"] < valores["fecha_inicio"]:
                    raise ValueError("La fecha de fin no puede ser anterior a la de inicio.")
                if (tabla == "Usuario" and estado["id"] is not None
                        and str(estado["id"]) == str(self.usuario["id"]) and valores["activo"] == 0):
                    raise ValueError("No puedes desactivar tu propia cuenta.")

                reales = [c for c in campos if c not in virtuales]
                cn = self.db()
                if not cn:
                    return
                cur = cn.cursor()
                try:
                    if estado["id"] is not None:
                        pares = [(c, valores[c]) for c in reales
                                 if not (c == "contrasena_hash" and valores[c] is None)]
                        asign = ", ".join(f"`{c}`=%s" for c, _ in pares)
                        cur.execute(f"UPDATE `{tabla}` SET {asign} WHERE `{pk}`=%s",
                                    tuple(v for _, v in pares) + (estado["id"],))
                        if tabla == "Producto":
                            cur.execute("UPDATE Inventario SET stock_minimo=%s WHERE id_producto=%s",
                                        (valores["stock_minimo"], estado["id"]))
                    else:
                        codigo = siguiente_codigo(cur, tabla, col_cod, pref)
                        cols_ins = [col_cod] + [c for c in reales if c != col_cod]
                        vals = [codigo] + [valores[c] for c in reales if c != col_cod]
                        marks = ", ".join(["%s"] * len(cols_ins))
                        cur.execute(f"INSERT INTO `{tabla}` ({', '.join(f'`{c}`' for c in cols_ins)}) "
                                    f"VALUES ({marks})", tuple(vals))
                        if tabla == "Producto":
                            id_nuevo = cur.lastrowid   # guardarlo ANTES de otro SELECT
                            cod_inv = siguiente_codigo(cur, "Inventario", "codigo", "INV")
                            cur.execute("INSERT INTO Inventario(codigo,id_producto,stock_actual,stock_minimo) "
                                        "VALUES(%s,%s,0,%s)", (cod_inv, id_nuevo, valores["stock_minimo"]))
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
                messagebox.showwarning("Revisa los datos", str(e))
            except Exception as e:
                messagebox.showerror("No se pudo guardar", texto_error(e))

        def eliminar():
            if estado["id"] is None:
                messagebox.showwarning("Eliminar", "Primero elige un registro de la tabla.")
                return
            if tabla == "Usuario" and str(estado["id"]) == str(self.usuario["id"]):
                messagebox.showwarning("Eliminar", "No puedes eliminar tu propia cuenta.")
                return
            if not messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar el registro seleccionado?\n"
                                                    "Esta acción no se puede deshacer."):
                return
            cn = self.db()
            if not cn:
                return
            cur = cn.cursor()
            try:
                if tabla == "Producto":
                    cur.execute("DELETE FROM Inventario WHERE id_producto=%s AND stock_actual=0", (estado["id"],))
                cur.execute(f"DELETE FROM `{tabla}` WHERE `{pk}`=%s", (estado["id"],))
                cn.commit()
            except Exception as e:
                cn.rollback()
                messagebox.showerror("No se puede eliminar", texto_error(e))
                return
            finally:
                cur.close()
                cn.close()
            limpiar_form()
            cargar()

        boton(barra, "💾  GUARDAR", guardar, bg=VERDE).pack(side="left", padx=(0, 6))
        boton(barra, "🆕  NUEVO / LIMPIAR", limpiar_form, bg=AZUL).pack(side="left", padx=6)
        boton(barra, "🗑  ELIMINAR", eliminar, bg=ROJO).pack(side="left", padx=6)
        boton(barra, "🔄  ACTUALIZAR LISTA", cargar, bg=GRIS).pack(side="left", padx=6)
        zona = tk.Frame(barra, bg=FONDO)
        zona.pack(side="left", padx=(30, 0))
        tk.Label(zona, text="🔎 Buscar:", bg=FONDO, fg=TEXTO, font=(FUENTE, 10, "bold")).grid(row=0, column=0, padx=(0, 4))
        ttk.Entry(zona, textvariable=buscar, width=30).grid(row=0, column=1, sticky="w")
        lbl_busqueda = tk.Label(zona, text=texto_busqueda, bg=FONDO, fg=GRIS, font=(FUENTE, 8, "italic"))
        lbl_busqueda.grid(row=1, column=1, sticky="w")
        buscar.trace_add("write", mostrar)

        caja.pack(fill="both", expand=True, padx=20, pady=(4, 12))
        cargar()
        limpiar_form()
        # Referencias de la pantalla actual (útiles para pruebas automáticas)
        self.pantalla = dict(widgets=widgets, guardar=guardar, eliminar=eliminar,
                             nuevo=limpiar_form, tabla=tv, elegir=elegir, buscar=buscar)

    # ------------------------------------------------------------------
    # Movimientos: entradas y salidas en una sola pantalla
    # ------------------------------------------------------------------
    def form_movimientos(self):
        self.limpiar()
        self.pantalla_modulo(
            "Registrar entrada o salida",
            "Elige ENTRADA cuando llegan productos (compra, donación...) o SALIDA cuando salen "
            "(alimentación, entrega a una mascota o institución...). Agrega los productos a la lista y presiona «Registrar».",
            "🔄")
        tipo = tk.StringVar(value="ENTRADA")
        items = []          # [id_producto, nombre, cantidad, vencimiento(date|None)]

        sel = tk.Frame(self.area, bg=FONDO)
        sel.pack(fill="x", padx=20, pady=(12, 4))
        btn_ent = tk.Button(sel, text="⬇  ENTRADA  —  ingresan productos", relief="flat", bd=0, cursor="hand2",
                            font=(FUENTE, 11, "bold"), padx=22, pady=10,
                            command=lambda: cambiar("ENTRADA"))
        btn_sal = tk.Button(sel, text="⬆  SALIDA  —  salen productos", relief="flat", bd=0, cursor="hand2",
                            font=(FUENTE, 11, "bold"), padx=22, pady=10,
                            command=lambda: cambiar("SALIDA"))
        btn_ent.pack(side="left", padx=(0, 8))
        btn_sal.pack(side="left")

        f = tk.Frame(self.area, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        f.pack(fill="both", expand=True, padx=20, pady=(2, 12))
        form = tk.Frame(f, bg=BLANCO)
        form.pack(fill="x", padx=16, pady=(10, 4))
        form.grid_columnconfigure(1, weight=1, uniform="m")
        form.grid_columnconfigure(3, weight=1, uniform="m")

        def etiqueta(r, c, texto):
            lb = tk.Label(form, text=texto, bg=BLANCO, fg=TEXTO, font=(FUENTE, 9, "bold"), anchor="w")
            lb.grid(row=r, column=c, sticky="w", padx=(0, 8), pady=5)
            return lb

        etiqueta(0, 0, "Producto *")
        cb_prod = ttk.Combobox(form, state="readonly", values=self.opciones(SQL_PRODUCTOS))
        cb_prod.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=5)
        etiqueta(0, 2, "Cantidad *")
        e_cant = self.entrada(form, "decimal", 20)
        e_cant.grid(row=0, column=3, sticky="w", pady=5)

        etiqueta(1, 0, "Concepto *")
        cb_conc = self.filtrar(ttk.Combobox(form, values=CONCEPTOS_ENTRADA), V.filtro_texto(150))
        cb_conc.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=5)

        # Solo ENTRADA
        lb_venc = etiqueta(1, 2, "Vence (AAAA-MM-DD)  (opcional)")
        e_venc = self.entrada(form, "fecha", 20)
        e_venc.grid(row=1, column=3, sticky="w", pady=5)
        lb_fing = etiqueta(2, 0, "Fecha de ingreso (AAAA-MM-DD) *")
        e_fing = self.entrada(form, "fecha", 20)
        e_fing.grid(row=2, column=1, sticky="w", pady=5)
        e_fing.insert(0, date.today().isoformat())
        # Solo SALIDA
        lb_dest = etiqueta(1, 2, "Destinatario *  (quién recibe)")
        e_dest = self.entrada(form, "texto", 30, maximo=100)
        e_dest.grid(row=1, column=3, sticky="ew", pady=5)
        lb_masc = etiqueta(2, 0, "Mascota beneficiaria  (opcional)")
        cb_masc = ttk.Combobox(form, state="readonly", values=self.opciones(
            "SELECT id_mascota, CONCAT(nombre,' (',codigo,')') FROM Mascota "
            "WHERE fecha_salida IS NULL ORDER BY nombre", vacio=True))
        cb_masc.grid(row=2, column=1, sticky="ew", padx=(0, 20), pady=5)

        def al_elegir_mascota(event=None):
            if cb_masc.get():
                e_dest.delete(0, "end")
                e_dest.insert(0, "Mascota: " + cb_masc.get().split(" - ", 1)[1])
        cb_masc.bind("<<ComboboxSelected>>", al_elegir_mascota)

        etiqueta(2, 2, "Observación  (opcional)")
        e_obs = self.entrada(form, "texto", 30, maximo=200)
        e_obs.grid(row=2, column=3, sticky="ew", pady=5)

        solo_entrada = [lb_venc, e_venc, lb_fing, e_fing]
        solo_salida = [lb_dest, e_dest, lb_masc, cb_masc]

        fila_add = tk.Frame(f, bg=BLANCO)
        fila_add.pack(fill="x", padx=16, pady=(2, 4))
        tv = ttk.Treeview(f, columns=("producto", "cantidad", "vence"), show="headings", height=6)
        tv.heading("producto", text="PRODUCTO")
        tv.heading("cantidad", text="CANTIDAD")
        tv.heading("vence", text="VENCE")
        tv.column("producto", width=480, anchor="w")
        tv.column("cantidad", width=120, anchor="center")
        tv.column("vence", width=140, anchor="center")
        tv.tag_configure("par", background=BLANCO)
        tv.tag_configure("impar", background="#FFF4E5")
        tv.pack(fill="both", expand=True, padx=16, pady=4)
        fila_fin = tk.Frame(f, bg=BLANCO)
        fila_fin.pack(fill="x", padx=16, pady=(4, 12))

        def refrescar_lista():
            for i in tv.get_children():
                tv.delete(i)
            for n, (pid, nom, cant, venc) in enumerate(items):
                tv.insert("", "end", iid=str(n), tags=("par" if n % 2 == 0 else "impar",),
                          values=(nom, cant, venc.isoformat() if venc else "—"))

        def recargar_productos():
            cb_prod["values"] = self.opciones(SQL_PRODUCTOS)
            cb_prod.set("")
            e_cant.delete(0, "end")

        def cambiar(nuevo, forzar=False):
            if nuevo != tipo.get() and items and not forzar:
                if not messagebox.askyesno("Cambiar tipo", "La lista actual se vaciará. ¿Continuar?"):
                    return
                items.clear()
                refrescar_lista()
            tipo.set(nuevo)
            ent = nuevo == "ENTRADA"
            btn_ent.configure(bg=VERDE if ent else "#E9E2D6", fg=BLANCO if ent else GRIS)
            btn_sal.configure(bg=NARANJA if not ent else "#E9E2D6", fg=NEGRO if not ent else GRIS)
            for w in solo_entrada:
                (w.grid if ent else w.grid_remove)()
            for w in solo_salida:
                (w.grid if not ent else w.grid_remove)()
            cb_conc["values"] = CONCEPTOS_ENTRADA if ent else CONCEPTOS_SALIDA
            cb_conc.set("")
            btn_reg.configure(text="✔  REGISTRAR ENTRADA" if ent else "✔  REGISTRAR SALIDA",
                              bg=VERDE if ent else NARANJA, fg=BLANCO if ent else NEGRO)

        def agregar():
            try:
                texto = cb_prod.get()
                pid = self.id_de(texto)
                if pid is None:
                    raise ValueError("Elige un producto.")
                cant = self.leer_cantidad(e_cant.get())
                venc = None
                if tipo.get() == "ENTRADA":
                    venc = self.leer_fecha(e_venc.get(), "Fecha de vencimiento", obligatoria=False)
                    f_ing = self.leer_fecha(e_fing.get(), "Fecha de ingreso")
                    if f_ing > date.today():
                        raise ValueError(f"La fecha de ingreso no puede ser futura (hoy es {date.today()}).")
                    if venc and venc < f_ing:
                        raise ValueError("El vencimiento no puede ser anterior a la fecha de ingreso.")
                    if venc and venc < date.today():
                        raise ValueError("Ese producto ya está vencido; no se puede ingresar al inventario.")
            except ValueError as e:
                messagebox.showerror("Revisa los datos", str(e))
                return
            nom = texto.split(" - ", 1)[1].split(" [")[0]
            if tipo.get() == "SALIDA":
                for it in items:
                    if it[0] == pid:
                        it[2] += cant
                        break
                else:
                    items.append([pid, nom, cant, None])
            else:
                items.append([pid, nom, cant, venc])
            refrescar_lista()
            cb_prod.set("")
            e_cant.delete(0, "end")
            e_venc.delete(0, "end")

        def quitar():
            sel_ = tv.selection()
            if sel_:
                items.pop(int(sel_[0]))
                refrescar_lista()
            else:
                messagebox.showinfo("Quitar", "Elige primero una fila de la lista.")

        def registrar():
            try:
                if not items:
                    raise ValueError("Agrega al menos un producto a la lista (botón «Agregar a la lista»).")
                concepto = " ".join(cb_conc.get().split())
                if not concepto:
                    raise ValueError("Escribe o elige el concepto del movimiento.")
                if not V.tiene_letra(concepto) or len(concepto) < 2:
                    raise ValueError("El concepto debe tener letras (no solo números).")
                es_ent = tipo.get() == "ENTRADA"
                dest = " ".join(e_dest.get().split())
                if not es_ent and not dest:
                    raise ValueError("En una salida debes indicar el destinatario.")
                if not es_ent and (not V.tiene_letra(dest) or len(dest) < 2):
                    raise ValueError("El destinatario debe tener letras (no solo números).")
                f_ing = self.leer_fecha(e_fing.get(), "Fecha de ingreso") if es_ent else date.today()
                if f_ing > date.today():
                    raise ValueError(f"La fecha de ingreso no puede ser futura (hoy es {date.today()}).")
                if es_ent:
                    for _pid, nom, _cant, venc in items:   # la fecha de ingreso pudo cambiar después de agregar
                        if venc and venc < f_ing:
                            raise ValueError(f"«{nom}» vence ({venc}) antes de la fecha de ingreso ({f_ing}).")
                obs = e_obs.get().strip() or None
                id_masc = self.id_de(cb_masc.get()) if not es_ent else None
                cn = self.db()
                if not cn:
                    return
                cur = cn.cursor()
                try:
                    if es_ent:
                        mid, cod_mov = self.crear_entrada(cur, items, concepto, f_ing, obs)
                    else:
                        mid, cod_mov = self.crear_salida(cur, items, concepto, dest, obs, id_masc)
                    cn.commit()
                except Exception:
                    cn.rollback()
                    raise
                finally:
                    cur.close()
                    cn.close()
                messagebox.showinfo("Correcto", f"{'Entrada' if es_ent else 'Salida'} registrada.\n"
                                                f"Código del movimiento: {cod_mov}")
                items.clear()
                refrescar_lista()
                for e in (e_obs, e_dest, e_venc):
                    e.delete(0, "end")
                cb_masc.set("")
                cb_conc.set("")
                recargar_productos()
            except ValueError as e:
                messagebox.showerror("Revisa los datos", str(e))
            except Exception as e:
                messagebox.showerror("No se pudo registrar", texto_error(e))

        boton(fila_add, "➕  AGREGAR A LA LISTA", agregar, bg=AZUL).pack(side="left")
        tk.Label(fila_add, text="  Agrega todos los productos del movimiento y luego presiona «Registrar».",
                 bg=BLANCO, fg=GRIS, font=(FUENTE, 9)).pack(side="left")
        boton(fila_fin, "✖  QUITAR LA FILA ELEGIDA", quitar, bg=GRIS).pack(side="left")
        btn_reg = boton(fila_fin, "", registrar, bg=VERDE, pady=10, size=11)
        btn_reg.pack(side="right")
        cambiar("ENTRADA", forzar=True)
        self.pantalla = dict(cambiar=cambiar, producto=cb_prod, cantidad=e_cant, concepto=cb_conc,
                             vence=e_venc, destinatario=e_dest, mascota=cb_masc, agregar=agregar,
                             registrar=registrar, lista=tv, items=items, obs=e_obs)

    def asegurar_inventario(self, cur, id_producto):
        cur.execute("SELECT id_inventario FROM Inventario WHERE id_producto=%s FOR UPDATE", (id_producto,))
        if cur.fetchone() is None:
            cod = siguiente_codigo(cur, "Inventario", "codigo", "INV")
            cur.execute("INSERT INTO Inventario(codigo,id_producto,stock_actual,stock_minimo) "
                        "VALUES(%s,%s,0,0)", (cod, id_producto))

    def crear_entrada(self, cur, items, concepto, f_ing, obs):
        """Cada producto que entra genera un lote. Suma al inventario."""
        cod_mov = siguiente_codigo(cur, "Movimiento", "codigo", "MOV")
        cur.execute("INSERT INTO Movimiento(codigo,tipo_movimiento,id_usuario,observacion) "
                    "VALUES(%s,'ENTRADA',%s,%s)", (cod_mov, self.usuario["id"], obs))
        mid = cur.lastrowid
        for pid, _nom, cant, venc in items:
            self.asegurar_inventario(cur, pid)
            cod_lote = siguiente_codigo(cur, "Lote", "codigo", "LOT")
            cur.execute("""INSERT INTO Lote(codigo,id_producto,cantidad_inicial,cantidad_actual,
                                            fecha_ingreso,fecha_vencimiento)
                           VALUES(%s,%s,%s,%s,%s,%s)""", (cod_lote, pid, cant, cant, f_ing, venc))
            lote = cur.lastrowid
            cod_det = siguiente_codigo(cur, "Detalle_Movimiento", "codigo", "DET")
            cur.execute("""INSERT INTO Detalle_Movimiento(codigo,id_movimiento,id_lote,cantidad,concepto,destinatario)
                           VALUES(%s,%s,%s,%s,%s,NULL)""", (cod_det, mid, lote, cant, concepto))
            cur.execute("UPDATE Inventario SET stock_actual=stock_actual+%s WHERE id_producto=%s", (cant, pid))
        return mid, cod_mov

    def crear_salida(self, cur, items, concepto, destinatario, obs, id_mascota=None):
        """Descuenta primero el lote que vence antes. Los lotes vencidos no se entregan.
        Si hay mascota beneficiaria, también anota lo que recibió en Beneficiario."""
        plan = []          # (id_producto, id_lote, cantidad)
        for pid, nombre, cantidad, _ in items:
            cur.execute("""SELECT id_lote, cantidad_actual FROM Lote
                           WHERE id_producto=%s AND cantidad_actual>0
                             AND (fecha_vencimiento IS NULL OR fecha_vencimiento>=CURDATE())
                           ORDER BY fecha_vencimiento IS NULL, fecha_vencimiento, fecha_ingreso, id_lote
                           FOR UPDATE""", (pid,))
            pendiente = cantidad
            for id_lote, actual in cur.fetchall():
                if pendiente <= 0:
                    break
                tomar = min(Decimal(str(actual)), pendiente)
                plan.append((pid, id_lote, tomar))
                pendiente -= tomar
            if pendiente > 0:
                raise ValueError(f"No hay stock vigente suficiente de «{nombre}». "
                                 f"Faltan {pendiente} (los lotes vencidos no se entregan).")
        cod_mov = siguiente_codigo(cur, "Movimiento", "codigo", "MOV")
        cur.execute("INSERT INTO Movimiento(codigo,tipo_movimiento,id_usuario,observacion) "
                    "VALUES(%s,'SALIDA',%s,%s)", (cod_mov, self.usuario["id"], obs))
        mid = cur.lastrowid
        for pid, id_lote, tomar in plan:
            self.asegurar_inventario(cur, pid)
            cur.execute("UPDATE Lote SET cantidad_actual=cantidad_actual-%s WHERE id_lote=%s", (tomar, id_lote))
            cod_det = siguiente_codigo(cur, "Detalle_Movimiento", "codigo", "DET")
            cur.execute("""INSERT INTO Detalle_Movimiento(codigo,id_movimiento,id_lote,cantidad,concepto,destinatario)
                           VALUES(%s,%s,%s,%s,%s,%s)""", (cod_det, mid, id_lote, tomar, concepto, destinatario))
            cur.execute("UPDATE Inventario SET stock_actual=stock_actual-%s WHERE id_producto=%s", (tomar, pid))
        if id_mascota:
            for pid, _nom, cant, _v in items:
                cur.execute("SELECT id_categoria, id_unidad FROM Producto WHERE id_producto=%s", (pid,))
                cat, uni = cur.fetchone()
                cod_ben = siguiente_codigo(cur, "Beneficiario", "cod_beneficiario", "BEN")
                cur.execute("""INSERT INTO Beneficiario(cod_beneficiario,id_mascota,id_categoria,fecha,id_unidad,cantidad)
                               VALUES(%s,%s,%s,CURDATE(),%s,%s)""", (cod_ben, id_mascota, cat, uni, cant))
        return mid, cod_mov

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def tabla_consulta(self, sql, encabezados, col_estado=None, anchos=None):
        caja = tk.Frame(self.area, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        caja.pack(fill="both", expand=True, padx=20, pady=12)
        tv = ttk.Treeview(caja, columns=encabezados, show="headings")
        sb = ttk.Scrollbar(caja, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        for i, col in enumerate(encabezados):
            tv.heading(col, text=col)
            tv.column(col, width=(anchos or {}).get(col, 100), minwidth=70, anchor="center")
        tags = {"STOCK BAJO": "#FFE0E0", "SIN STOCK": "#E6E6E6", "AGOTADO": "#E6E6E6", "VENCIDO": "#FFD0D0",
                "POR VENCER": "#FFF0C2", "ENTRADA": "#E3F4E8", "SALIDA": "#FFEAD3"}
        for nombre, color in tags.items():
            tv.tag_configure(nombre, background=color)
        tv.tag_configure("par", background=BLANCO)
        tv.tag_configure("impar", background="#FFF4E5")
        sb.pack(side="right", fill="y")
        tv.pack(side="left", fill="both", expand=True)
        cn = self.db()
        if cn:
            cur = cn.cursor()
            try:
                cur.execute(sql)
                for n, row in enumerate(cur.fetchall()):
                    vals = ["" if v is None else v for v in row]
                    etiqueta = vals[col_estado] if col_estado is not None else None
                    tag = etiqueta if etiqueta in tags else ("par" if n % 2 == 0 else "impar")
                    tv.insert("", "end", values=vals, tags=(tag,))
            except Exception as e:
                messagebox.showerror("Consulta", texto_error(e))
            finally:
                cur.close()
                cn.close()

    def leyenda(self, texto):
        tk.Label(self.area, text=texto, bg=FONDO, fg=GRIS, font=(FUENTE, 9)).pack(pady=(0, 8))

    def existencias(self):
        self.limpiar()
        self.pantalla_modulo("Existencias", "Cuánto hay de cada producto. «Vigente» es lo que se puede usar; "
                                            "«Vencido» es lo que ya no sirve. Las filas en color necesitan atención.", "📋")
        self.tabla_consulta("""
            SELECT z.*, CASE WHEN z.vigente<=0 THEN 'SIN STOCK'
                             WHEN z.stock_minimo>0 AND z.vigente<=z.stock_minimo THEN 'STOCK BAJO'
                             ELSE 'OK' END AS estado
            FROM (
              SELECT p.codigo, p.nombre, c.nombre AS categoria, COALESCE(e.nombre,'Todas') AS especie,
                     u.abreviatura, COALESCE(i.stock_actual,0) AS stock_total,
                     COALESCE(SUM(CASE WHEN l.fecha_vencimiento IS NULL OR l.fecha_vencimiento>=CURDATE()
                                       THEN l.cantidad_actual END),0) AS vigente,
                     COALESCE(SUM(CASE WHEN l.fecha_vencimiento<CURDATE() THEN l.cantidad_actual END),0) AS vencido,
                     COALESCE(i.stock_minimo,0) AS stock_minimo
              FROM Producto p
              JOIN Categoria c ON c.id_categoria=p.id_categoria
              JOIN Unidad_Medida u ON u.id_unidad=p.id_unidad
              LEFT JOIN Especie e ON e.id_especie=p.id_especie
              LEFT JOIN Inventario i ON i.id_producto=p.id_producto
              LEFT JOIN Lote l ON l.id_producto=p.id_producto
              GROUP BY p.id_producto, p.codigo, p.nombre, c.nombre, e.nombre, u.abreviatura,
                       i.stock_actual, i.stock_minimo
            ) z ORDER BY z.nombre
        """, ["CÓDIGO", "PRODUCTO", "CATEGORÍA", "ESPECIE", "UNIDAD", "STOCK TOTAL", "VIGENTE", "VENCIDO",
              "STOCK MÍNIMO", "ESTADO"], col_estado=9, anchos={"PRODUCTO": 190})

    def lotes(self):
        self.limpiar()
        self.pantalla_modulo("Lotes y vencimientos", "Cada vez que entra un producto se crea un lote con su cantidad "
                                                     "y fecha de vencimiento. Al hacer una salida se usa primero el lote que vence antes.", "🏷")
        self.tabla_consulta("""
            SELECT l.codigo, p.nombre, u.abreviatura, l.cantidad_inicial, l.cantidad_actual,
                   l.fecha_ingreso, l.fecha_vencimiento,
                   CASE WHEN l.cantidad_actual=0 THEN 'AGOTADO'
                        WHEN l.fecha_vencimiento IS NOT NULL AND l.fecha_vencimiento<CURDATE() THEN 'VENCIDO'
                        WHEN l.fecha_vencimiento IS NOT NULL
                             AND l.fecha_vencimiento<=DATE_ADD(CURDATE(),INTERVAL 30 DAY) THEN 'POR VENCER'
                        ELSE 'VIGENTE' END
            FROM Lote l
            JOIN Producto p ON p.id_producto=l.id_producto
            JOIN Unidad_Medida u ON u.id_unidad=p.id_unidad
            ORDER BY (l.cantidad_actual=0), l.fecha_vencimiento IS NULL, l.fecha_vencimiento, l.id_lote
        """, ["LOTE", "PRODUCTO", "UNIDAD", "CANT. INICIAL", "CANT. ACTUAL", "INGRESO", "VENCE", "ESTADO"],
            col_estado=7, anchos={"PRODUCTO": 200})

    def historial(self):
        self.limpiar()
        self.pantalla_modulo("Historial de movimientos", "Todas las entradas (verde) y salidas (naranja) registradas, "
                                                         "con su concepto, destinatario y el usuario que las hizo.", "🕘")
        self.tabla_consulta("""
            SELECT m.codigo, m.fecha, m.tipo_movimiento, p.nombre, l.codigo, d.cantidad, d.concepto,
                   COALESCE(d.destinatario,''), us.nombre_usuario, COALESCE(m.observacion,'')
            FROM Movimiento m
            JOIN Usuario us ON us.id_usuario=m.id_usuario
            JOIN Detalle_Movimiento d ON d.id_movimiento=m.id_movimiento
            JOIN Lote l ON l.id_lote=d.id_lote
            JOIN Producto p ON p.id_producto=l.id_producto
            ORDER BY m.fecha DESC, m.id_movimiento DESC, d.id_detalle
            LIMIT 500
        """, ["MOVIMIENTO", "FECHA", "TIPO", "PRODUCTO", "LOTE", "CANTIDAD", "CONCEPTO", "DESTINATARIO",
              "USUARIO", "OBSERVACIÓN"], col_estado=2, anchos={"PRODUCTO": 160, "CONCEPTO": 160, "FECHA": 140})

    def alertas(self):
        self.limpiar()
        self.pantalla_modulo("Alertas: stock bajo y vencimientos", "Productos con poco stock, lotes vencidos y lotes que "
                                                                   "vencen en los próximos 30 días. Conviene revisarlos pronto.", "🚨")
        self.tabla_consulta("""
            SELECT 'STOCK BAJO' AS alerta, p.nombre AS producto, '' AS lote,
                   COALESCE(SUM(CASE WHEN l.fecha_vencimiento IS NULL OR l.fecha_vencimiento>=CURDATE()
                                     THEN l.cantidad_actual END),0) AS cantidad,
                   u.abreviatura AS unidad, CONCAT('Mínimo: ', i.stock_minimo) AS detalle
            FROM Inventario i
            JOIN Producto p ON p.id_producto=i.id_producto
            JOIN Unidad_Medida u ON u.id_unidad=p.id_unidad
            LEFT JOIN Lote l ON l.id_producto=p.id_producto
            GROUP BY p.id_producto,p.nombre,i.stock_minimo,u.abreviatura
            HAVING i.stock_minimo>0 AND cantidad<=i.stock_minimo
            UNION ALL
            SELECT CASE WHEN l.fecha_vencimiento<CURDATE() THEN 'VENCIDO' ELSE 'POR VENCER' END,
                   p.nombre, l.codigo, l.cantidad_actual, u.abreviatura,
                   CONCAT('Vence: ', l.fecha_vencimiento)
            FROM Lote l
            JOIN Producto p ON p.id_producto=l.id_producto
            JOIN Unidad_Medida u ON u.id_unidad=p.id_unidad
            WHERE l.cantidad_actual>0 AND l.fecha_vencimiento IS NOT NULL
              AND l.fecha_vencimiento<=DATE_ADD(CURDATE(),INTERVAL 30 DAY)
            ORDER BY 1, 2
        """, ["ALERTA", "PRODUCTO", "LOTE", "CANTIDAD", "UNIDAD", "DETALLE"], col_estado=0,
            anchos={"PRODUCTO": 220, "DETALLE": 180})
        self.leyenda("Por vencer = dentro de los próximos 30 días. El stock bajo cuenta solo los lotes vigentes.")
        boton(self.area, "📐  VER CÓMO SE CALCULA CADA ALERTA (PASO A PASO)", self.calculo_alertas,
              bg="#7C4DC4", pady=9).pack(pady=(0, 12))

    # ------------------------------------------------------------------
    # Cálculo de las alertas paso a paso (modelo matemático)
    # ------------------------------------------------------------------
    def datos_alertas(self, desde, ids=None):
        """Lee de la base los datos del modelo. Devuelve (hoy, filas) con una fila por producto:
        (id, nombre, unidad, I, E, D, m, X, F)."""
        cn = self.db()
        if cn is None:
            return None, []
        cur = cn.cursor()
        try:
            cur.execute("SELECT CURDATE()")
            hoy = cur.fetchone()[0]
            mov = """COALESCE((SELECT SUM(d.cantidad) FROM Detalle_Movimiento d
                                JOIN Movimiento mv ON mv.id_movimiento = d.id_movimiento
                                JOIN Lote lm ON lm.id_lote = d.id_lote
                               WHERE lm.id_producto = p.id_producto AND mv.tipo_movimiento = '{}'
                                 AND mv.fecha >= %s), 0)"""
            filtro = ""
            params = [desde, desde]
            if ids:
                filtro = "WHERE p.id_producto IN (" + ",".join(["%s"] * len(ids)) + ")"
                params += list(ids)
            cur.execute(f"""
                SELECT p.id_producto, p.nombre, u.abreviatura,
                       {mov.format('ENTRADA')} AS E,
                       {mov.format('SALIDA')} AS D,
                       COALESCE(i.stock_minimo, 0) AS m,
                       COALESCE((SELECT SUM(l.cantidad_actual) FROM Lote l
                                  WHERE l.id_producto = p.id_producto
                                    AND l.fecha_vencimiento < CURDATE()), 0) AS X,
                       COALESCE((SELECT SUM(l.cantidad_actual) FROM Lote l
                                  WHERE l.id_producto = p.id_producto), 0) AS F
                FROM Producto p
                JOIN Unidad_Medida u ON u.id_unidad = p.id_unidad
                LEFT JOIN Inventario i ON i.id_producto = p.id_producto
                {filtro}
                ORDER BY p.nombre""", tuple(params))
            filas = []
            for pid, nombre, uni, E, D, m, X, F in cur.fetchall():
                E, D, m, X, F = (Decimal(str(v)) for v in (E, D, m, X, F))
                filas.append((pid, nombre, uni, F - E + D, E, D, m, X, F))   # I = hoy − E + D
            return hoy, filas
        except Exception as e:
            messagebox.showerror("Consulta", texto_error(e))
            return None, []
        finally:
            cur.close()
            cn.close()

    def lotes_alertas(self, ids):
        """Lotes con existencia y fecha de vencimiento de los productos elegidos (el que vence antes primero)."""
        cn = self.db()
        if cn is None:
            return []
        cur = cn.cursor()
        try:
            cur.execute("""SELECT p.nombre, l.cantidad_actual, l.fecha_vencimiento, l.codigo, u.abreviatura
                           FROM Lote l
                           JOIN Producto p ON p.id_producto = l.id_producto
                           JOIN Unidad_Medida u ON u.id_unidad = p.id_unidad
                           WHERE l.cantidad_actual > 0 AND l.fecha_vencimiento IS NOT NULL
                             AND l.id_producto IN (""" + ",".join(["%s"] * len(ids)) + """)
                           ORDER BY l.fecha_vencimiento, l.id_lote""", tuple(ids))
            return [(n, Decimal(str(q)), fv, cod, u) for n, q, fv, cod, u in cur.fetchall()]
        finally:
            cur.close()
            cn.close()

    def calculo_alertas(self):
        self.limpiar()
        self.pantalla_modulo("Cálculo de las alertas", "", "📐")
        cuerpo = tk.Frame(self.area, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=14, pady=8)

        izq = tk.Frame(cuerpo, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1, width=410)
        izq.pack(side="left", fill="y", padx=(0, 12))
        izq.pack_propagate(False)
        tk.Frame(izq, bg="#7C4DC4", height=5).pack(fill="x")
        tk.Label(izq, text="1.  Período", bg=BLANCO, fg=NEGRO, font=(FUENTE, 11, "bold")).pack(
            anchor="w", padx=12, pady=(8, 0))
        fila = tk.Frame(izq, bg=BLANCO)
        fila.pack(anchor="w", padx=12, pady=(2, 0))
        tk.Label(fila, text="Movimientos desde:", bg=BLANCO, fg=TEXTO, font=(FUENTE, 9)).pack(side="left")
        e_desde = self.entrada(fila, "fecha", 12)
        e_desde.pack(side="left", padx=6)
        e_desde.insert(0, (date.today() - timedelta(days=30)).isoformat())
        lbl_hoy = tk.Label(izq, text="", bg=BLANCO, fg=GRIS, font=(FUENTE, 8), justify="left", wraplength=380)
        lbl_hoy.pack(anchor="w", padx=12)

        tk.Label(izq, text=f"2.  Productos (de 1 a {CA.MAX_PRODUCTOS})", bg=BLANCO, fg=NEGRO,
                 font=(FUENTE, 11, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        tk.Label(izq, text="Ya vienen marcados los que tienen alerta.\nCtrl + clic para elegir varios.",
                 bg=BLANCO, fg=GRIS, font=(FUENTE, 8), justify="left").pack(anchor="w", padx=12)
        caja = tk.Frame(izq, bg=BLANCO)
        caja.pack(fill="both", expand=True, padx=12, pady=(4, 0))
        tv = ttk.Treeview(caja, columns=("p", "v", "m", "e"), show="headings", selectmode="extended", height=9)
        for col, txt, w in (("p", "PRODUCTO", 132), ("v", "VIGENTE", 82), ("m", "MÍN.", 52), ("e", "ALERTA", 84)):
            tv.heading(col, text=txt)
            tv.column(col, width=w, anchor="w" if col == "p" else "center", stretch=col == "p")
        tv.tag_configure("alerta", background="#FBE3E3", foreground=ROJO)
        tv.tag_configure("ok", background=BLANCO)
        sb = ttk.Scrollbar(caja, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tv.pack(side="left", fill="both", expand=True)

        pasos = CA.PasoAPaso(cuerpo, self.root, boton)

        def cargar_lista():
            hoy, filas = self.datos_alertas(date.today().isoformat())
            if hoy is None:
                return
            lbl_hoy.configure(text=f"hasta hoy (t = {hoy}).\nAviso de vencimiento: k = {CA.K_DIAS} días (igual que «Alertas»).")
            tv.delete(*tv.get_children())
            con_alerta = []
            for pid, nombre, uni, _I, _E, _D, m, X, F in filas:
                vig = F - X
                alerta = m > 0 and vig <= m
                tv.insert("", "end", iid=str(pid), tags=("alerta" if alerta else "ok",),
                          values=(nombre, CA.fmt(vig), CA.fmt(m), "⚠ BAJO" if alerta else ("—" if m <= 0 else "OK")))
                if alerta:
                    con_alerta.append(str(pid))
            # productos con lotes por vencer o vencidos también se marcan
            cn = self.db()
            if cn is not None:
                cur = cn.cursor()
                try:
                    cur.execute("""SELECT DISTINCT id_producto FROM Lote WHERE cantidad_actual > 0
                                     AND fecha_vencimiento IS NOT NULL
                                     AND fecha_vencimiento <= DATE_ADD(CURDATE(), INTERVAL %s DAY)""", (CA.K_DIAS,))
                    for (pid,) in cur.fetchall():
                        if str(pid) not in con_alerta and tv.exists(str(pid)):
                            con_alerta.append(str(pid))
                            tv.item(str(pid), tags=("alerta",))
                            vals = list(tv.item(str(pid), "values"))
                            vals[3] = "⚠ LOTE" if vals[3] in ("OK", "—") else vals[3]
                            tv.item(str(pid), values=vals)
                finally:
                    cur.close()
                    cn.close()
            elegidos = con_alerta[:CA.MAX_PRODUCTOS] or list(tv.get_children())[:CA.MAX_PRODUCTOS]
            tv.selection_set(elegidos)
            if elegidos:
                tv.see(elegidos[0])

        def resolver():
            try:
                desde = self.leer_fecha(e_desde.get(), "Movimientos desde")
                if desde > date.today():
                    raise ValueError("«Movimientos desde» no puede ser una fecha futura.")
                ids = [int(i) for i in tv.selection()]
                if not ids:
                    raise ValueError("Elige al menos un producto de la lista.")
                if len(ids) > CA.MAX_PRODUCTOS:
                    raise ValueError(f"Elige como máximo {CA.MAX_PRODUCTOS} productos "
                                     f"(elegiste {len(ids)}): es lo que cabe en el dibujo.")
            except ValueError as e:
                messagebox.showwarning("Revisa los datos", str(e))
                return
            hoy, filas = self.datos_alertas(desde.isoformat(), ids)
            if hoy is None or not filas:
                return
            productos = [(nombre, uni, I, E, D, m, X) for _pid, nombre, uni, I, E, D, m, X, _F in filas]
            lotes = self.lotes_alertas(ids)
            pasos.mostrar(dict(productos=productos, lotes=lotes[:CA.MAX_LOTES], hoy=hoy, k=CA.K_DIAS,
                               desde=desde, lotes_ocultos=max(len(lotes) - CA.MAX_LOTES, 0)))

        boton(izq, "▶  RESOLVER PASO A PASO", resolver, bg=VERDE, pady=9, size=11).pack(
            fill="x", padx=12, pady=(8, 4))
        boton(izq, "🚨  Ver la lista de alertas", self.alertas, bg=ROJO, size=9, pady=6).pack(
            fill="x", padx=12, pady=(0, 10))
        cargar_lista()
        self.pantalla = dict(desde=e_desde, lista=tv, resolver=resolver, pasos=pasos)

    def resumen(self):
        self.limpiar()
        self.pantalla_modulo("Resumen general", "Un vistazo rápido a los números del albergue.", "📊")
        cn = self.db()
        if not cn:
            return
        cur = cn.cursor()
        consultas = [
            ("Productos registrados", "SELECT COUNT(*) FROM Producto", NARANJA),
            ("Mascotas en el albergue", "SELECT COUNT(*) FROM Mascota WHERE fecha_salida IS NULL", CELESTE),
            ("Donaciones recibidas", "SELECT COUNT(*) FROM Donacion", ROSA),
            ("Cuidados especiales activos",
             "SELECT COUNT(*) FROM Cuidados_Especiales WHERE fecha_fin IS NULL OR fecha_fin>=CURDATE()", VERDE),
            ("Lotes con existencia vigente",
             "SELECT COUNT(*) FROM Lote WHERE cantidad_actual>0 AND (fecha_vencimiento IS NULL OR fecha_vencimiento>=CURDATE())",
             NARANJA),
            ("Movimientos registrados", "SELECT COUNT(*) FROM Movimiento", AZUL),
        ]
        caja = tk.Frame(self.area, bg=FONDO)
        caja.pack(fill="x", padx=30, pady=25)
        try:
            for c in range(3):
                caja.grid_columnconfigure(c, weight=1, uniform="r")
            for i, (titulo, sql, color) in enumerate(consultas):
                cur.execute(sql)
                valor = cur.fetchone()[0]
                tarjeta = tk.Frame(caja, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
                tarjeta.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
                tk.Frame(tarjeta, bg=color, height=6).pack(fill="x")
                tk.Label(tarjeta, text=str(valor), bg=BLANCO, fg=NEGRO, font=(FUENTE, 32, "bold")).pack(pady=(16, 0))
                tk.Label(tarjeta, text=titulo, bg=BLANCO, fg=GRIS, font=(FUENTE, 11)).pack(pady=(0, 18))
        finally:
            cur.close()
            cn.close()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = PeluchinApp(ventana)
    ventana.mainloop()