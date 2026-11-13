import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- Datos de ejemplo ----------------
ACTIVIDAD = [
    ("11/11/2026", "Donación", 'Se han donado croquetas al albergue "Casa de los Gatos"', "10Kg."),
    ("02/11/2026", "Donación", 'Se recibió una donación de croquetas de parte de la empresa "Purina"', "20Kg."),
    ("10/10/2026", "Inventario", "Se han utilizado 18Kg. de croquetas para perro de 20Kg. disponibles", "20Kg."),
]

# id: (nombre, categoría, stock, unidad, estado, stock mínimo, lote/caducidad, ubicación, notas)
PRODUCTOS = {
    101: ("Croquetas adulto (20Kg)", "Comida Perro", 50, "Kg", "En stock", "-", "-", "-", "-"),
    102: ("Comida adulto (15Kg)", "Comida Gato", 80, "Kg", "En stock", "-", "-", "-", "-"),
    103: ("Medicamento X (Caja)", "Medicina", 5, "CAJA", "Crítico", 5,
          "Lote 456 / 30/11/2026", "Estante B-4", "Suministro para tratamiento post-operatorio"),
    104: ("Arnés Grande (Unidad)", "Accesorios", 25, "UND", "En stock", "-", "-", "-", "-"),
    105: ("Manta Polar (Paquete)", "Equipo", 12, "PAQ", "En stock", "-", "-", "-", "-"),
}

BOTONES_MENU = [
    "Inicio", "Productos", "Categoría", "Inventario", "Entradas", "Salidas",
    "Donaciones", "Donantes", "Beneficiarios", "Programas", "Entregas", "Reportes",
]


def pendiente(nombre):
    messagebox.showinfo("Pendiente", f'"{nombre}" todavía no está implementado.')


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Albergue de Mascotas Peluchín")
        self.geometry("720x620")

        # Encabezado común a todas las pantallas
        tk.Label(self, text="ALBERGUE DE MASCOTAS PELUCHÍN", font=("Courier", 16, "bold")).pack(pady=(10, 0))
        tk.Label(self, text="SISTEMA DE INVENTARIO Y SUMINISTROS", font=("Courier", 11, "bold")).pack(pady=(0, 10))
        ttk.Separator(self).pack(fill="x")

        # Contenedor donde se apilan las pantallas
        contenedor = tk.Frame(self)
        contenedor.pack(fill="both", expand=True)
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        self.pantallas = {}
        for Pantalla in (Menu, Inicio, Productos):
            frame = Pantalla(contenedor, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.pantallas[Pantalla.__name__] = frame

        self.mostrar("Menu")

    def mostrar(self, nombre):
        self.pantallas[nombre].tkraise()


class Menu(tk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre)
        cuadro = tk.Frame(self)
        cuadro.pack(expand=True)

        for i, nombre in enumerate(BOTONES_MENU):
            if nombre in ("Inicio", "Productos"):
                accion = lambda n=nombre: app.mostrar(n)
            else:
                accion = lambda n=nombre: pendiente(n)
            tk.Button(cuadro, text=nombre, width=20, height=2, command=accion).grid(
                row=i // 2, column=i % 2, padx=20, pady=10)


class Inicio(tk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre)
        barra = tk.Frame(self)
        barra.pack(fill="x")
        tk.Label(barra, text="Inicio", bg="#444", fg="white", width=12, pady=6).pack(side="left")
        tk.Button(barra, text="← Menú", command=lambda: app.mostrar("Menu")).pack(side="right", padx=5)

        # Tarjetas
        tarjetas = tk.Frame(self)
        tarjetas.pack(pady=20)
        for texto in ("MASCOTAS", "PRODUCTOS\nBAJOS", "TOTAL DE\nDONACIONES", "ENTREGAS"):
            tk.Label(tarjetas, text=texto, width=16, height=6, relief="solid", bd=1).pack(side="left", padx=8)

        # Actividad reciente
        tk.Label(self, text="Actividad Reciente:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20)
        columnas = ("Fecha", "Tipo", "Descripción", "Cantidad")
        tabla = ttk.Treeview(self, columns=columnas, show="headings", height=5)
        for col, ancho in zip(columnas, (90, 90, 380, 80)):
            tabla.heading(col, text=col)
            tabla.column(col, width=ancho, anchor="center")
        for fila in ACTIVIDAD:
            tabla.insert("", "end", values=fila)
        tabla.pack(padx=20, pady=10, fill="x")


class Productos(tk.Frame):
    def __init__(self, padre, app):
        super().__init__(padre)
        barra = tk.Frame(self)
        barra.pack(fill="x")
        tk.Label(barra, text="Productos", bg="#444", fg="white", width=12, pady=6).pack(side="left")
        tk.Button(barra, text="← Menú", command=lambda: app.mostrar("Menu")).pack(side="right", padx=5)

        # Tabla de productos
        tk.Label(self, text="Filtros de Búsqueda", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        columnas = ("ID", "Nombre", "Categoría", "Stock", "Unidad", "Estado")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", height=5)
        for col, ancho in zip(columnas, (50, 200, 120, 70, 70, 90)):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")
        for pid, p in PRODUCTOS.items():
            self.tabla.insert("", "end", iid=str(pid), values=(pid, *p[:5]))
        self.tabla.pack(padx=20, pady=5, fill="x")
        self.tabla.bind("<<TreeviewSelect>>", self.ver_detalle)

        # Acciones sobre la fila seleccionada (los íconos de lápiz y papelera del boceto)
        acciones = tk.Frame(self)
        acciones.pack(anchor="e", padx=20)
        tk.Button(acciones, text="Editar", command=lambda: pendiente("Editar")).pack(side="left", padx=3)
        tk.Button(acciones, text="Eliminar", command=lambda: pendiente("Eliminar")).pack(side="left", padx=3)

        # Detalle
        tk.Label(self, text="DETALLE", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.detalle = tk.Label(self, text="Seleccione un producto de la tabla.", justify="left",
                                anchor="nw", relief="solid", bd=1, padx=15, pady=10, height=8)
        self.detalle.pack(padx=20, pady=5, fill="x")

        # Botones inferiores
        botones = tk.Frame(self)
        botones.pack(pady=10)
        nombres = ("Registrar nuevo producto", "Ajustar stock mínimo",
                   "Generar reporte de Stock", "Verificar caducidades")
        for i, nombre in enumerate(nombres):
            tk.Button(botones, text=nombre, width=30, command=lambda n=nombre: pendiente(n)).grid(
                row=i // 2, column=i % 2, padx=15, pady=5)

        self.tabla.selection_set("103")  # igual que en el boceto

    def ver_detalle(self, _evento=None):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        pid = int(seleccion[0])
        nombre, categoria, stock, _unidad, _estado, minimo, lote, ubicacion, notas = PRODUCTOS[pid]
        self.detalle.config(text=(
            f"ID: {pid}\n"
            f"Nombre: {nombre}\n"
            f"Categoría: {categoria}\n"
            f"Lote / Caducidad: {lote}\n"
            f"Ubicación: {ubicacion}\n"
            f"Notas: {notas}\n"
            f"Stock Mínimo: {minimo}        Stock Actual: {stock}"
        ))


if __name__ == "__main__":
    App().mainloop()
