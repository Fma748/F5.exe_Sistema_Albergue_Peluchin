"""
Cálculo de las alertas, paso a paso (modelo matemático del Subproducto P2).

Es la pantalla del archivo modelo_matematico_peluchin.py integrada al sistema:
en vez de escribir los datos a mano, se toman de la base de datos, y cada
resultado coincide con la pantalla «Alertas».

    (1)  F = I + E - D                      balance de inventario (vectores)
    (3)  D_i <= I_i + E_i  <=>  F_i >= 0    no se puede sacar más de lo que hay
    (4)  A_i = 1 si m_i > 0 y (F_i - X_i) <= m_i   alerta de stock mínimo
             (X_i = lo vencido: el sistema solo cuenta el stock vigente)
    (5)  V_l = 1 si q_l > 0 y (fv_l - t) <= k      alerta de vencimiento (k = 30 días)
"""
import tkinter as tk
from decimal import Decimal

FUENTE = "Segoe UI"
NEGRO, FONDO, BLANCO = "#000000", "#FFF8EE", "#FFFFFF"
NARANJA, VERDE, AZUL, ROJO, GRIS = "#F2994A", "#23874B", "#2563C9", "#C93B3B", "#6B7280"
BORDE, TEXTO, AYUDA_BG = "#E5D9C8", "#222222", "#FFF1CC"
# Un color fijo para cada variable del modelo
C_I, C_E, C_D, C_F, C_M = "#2563C9", "#23874B", "#D9731A", "#7C4DC4", "#6B7280"

ANCHO, ALTO = 700, 390
MAX_PRODUCTOS = 5        # lo que cabe en el dibujo
MAX_LOTES = 5
K_DIAS = 30              # mismo aviso que la pantalla «Alertas»


# ======================================================================
# Modelo matemático (sin interfaz)
# ======================================================================
def calcular(productos, lotes, hoy, k):
    """productos: [(nombre, unidad, I, E, D, m, X)]   lotes: [(producto, q, fv, codigo, unidad)]"""
    F = [i + e - d for _n, _u, i, e, d, _m, _x in productos]                          # (1)
    cumple = [d <= i + e for _n, _u, i, e, d, _m, _x in productos]                   # (3)
    vigente = [f - p[6] for f, p in zip(F, productos)]
    A = [1 if p[5] > 0 and fv <= p[5] else 0 for fv, p in zip(vigente, productos)]   # (4)
    V = []
    for nombre, q, fv, codigo, unidad in lotes:                                      # (5)
        dias = (fv - hoy).days
        V.append(dict(producto=nombre, q=q, fv=fv, dias=dias, codigo=codigo, unidad=unidad,
                      alerta=1 if q > 0 and dias <= k else 0))
    return dict(F=F, vigente=vigente, cumple=cumple, A=A, V=V)


def fmt(x):
    x = Decimal(x).quantize(Decimal("0.01"))
    s = format(x, "f")
    return s.rstrip("0").rstrip(".") if "." in s else s


def corto(texto, n=16):
    return texto if len(texto) <= n else texto[:n - 1] + "…"


# ======================================================================
# Panel de pasos (dibujo)
# ======================================================================
class PasoAPaso:
    def __init__(self, padre, root, boton):
        self.root, self.boton = root, boton
        self.pasos, self.paso, self.modelo, self.datos = [], 0, None, None
        der = tk.Frame(padre, bg=FONDO)
        der.pack(side="left", fill="both", expand=True)
        self.nav = tk.Canvas(der, height=40, bg=FONDO, highlightthickness=0)
        self.nav.pack(fill="x")
        self.titulo = tk.Label(der, text="", bg=FONDO, fg=NEGRO, font=(FUENTE, 13, "bold"), anchor="w")
        self.titulo.pack(fill="x", pady=(0, 2))
        marco = tk.Frame(der, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        marco.pack(anchor="w")
        self.c = tk.Canvas(marco, width=ANCHO, height=ALTO, bg=BLANCO, highlightthickness=0)
        self.c.pack()
        self.texto = tk.Label(der, text="", bg=AYUDA_BG, fg="#5B4A00", justify="left", anchor="nw",
                              wraplength=ANCHO - 24, font=(FUENTE, 9), padx=10, pady=6, height=4)
        self.texto.pack(anchor="w", fill="x", pady=(4, 4))
        bt = tk.Frame(der, bg=FONDO)
        bt.pack(anchor="w", fill="x")
        self.b_ini = boton(bt, "⏮  Inicio", lambda: self.ir(0), bg=GRIS, size=9, pady=6)
        self.b_ant = boton(bt, "◀  Anterior", lambda: self.ir(self.paso - 1), bg=AZUL, pady=6)
        self.b_sig = boton(bt, "Siguiente  ▶", lambda: self.ir(self.paso + 1), bg=VERDE, pady=6)
        self.b_fin = boton(bt, "Ver resultado  ⏭", lambda: self.ir(len(self.pasos) - 1), bg=GRIS, size=9, pady=6)
        self.bases = {self.b_ini: GRIS, self.b_ant: AZUL, self.b_sig: VERDE, self.b_fin: GRIS}
        for b in (self.b_ini, self.b_ant):
            b.pack(side="left", padx=(0, 6))
        for b in (self.b_fin, self.b_sig):
            b.pack(side="right", padx=(6, 0))
        # Flechas del teclado (app.limpiar() las desactiva al salir de la pantalla)
        root.bind("<Right>", lambda e: self.ir(self.paso + 1))
        root.bind("<Left>", lambda e: self.ir(self.paso - 1))
        self.dibujar_inicio()

    # ------------------------------------------------------------------
    def dibujar_inicio(self, aviso=None):
        self.pasos = []
        self.c.delete("all")
        self.nav.delete("all")
        self.titulo.configure(text="Cálculo de las alertas")
        self.c.create_text(ANCHO // 2, 100, text="F = I + E − D", font=(FUENTE, 40, "bold"), fill=C_F)
        self.c.create_text(ANCHO // 2, 175, text="Así calcula el sistema cada alerta",
                           font=(FUENTE, 14), fill=TEXTO)
        self.c.create_text(ANCHO // 2, 245, justify="center", font=(FUENTE, 11), fill=GRIS,
                           text=aviso or "1. Elige el período y de 1 a 5 productos a la izquierda.\n"
                                         "2. Presiona «Resolver paso a paso».\n"
                                         "3. Avanza con «Siguiente» o con las flechas del teclado.")
        self.texto.configure(text="Los datos salen de la base del albergue. Se resuelve el balance de inventario (1), "
                                  "la restricción de no negatividad (3), la alerta de stock mínimo (4) y la alerta de "
                                  "vencimiento (5): son las mismas alertas que muestra la pantalla «Alertas».")
        for b in self.bases:
            b.configure(state="disabled", bg="#999999")

    def mostrar(self, datos):
        """datos: dict(productos, lotes, hoy, k, desde, lotes_ocultos)"""
        self.datos = datos
        self.modelo = calcular(datos["productos"], datos["lotes"], datos["hoy"], datos["k"])
        self.armar_pasos()
        self.ir(0)

    def armar_pasos(self):
        P = self.datos["productos"]
        self.pasos = [("Identificar las variables", self.p_variables, self.t_variables()),
                      ("Plantear el balance  F = I + E − D", self.p_plantear, self.t_plantear())]
        for i in range(len(P)):
            self.pasos.append((f"Calcular la fila {i + 1}: {P[i][0]}",
                               lambda i=i: self.p_fila(i), self.t_fila(i)))
        self.pasos += [("Resultado: inventario final F", self.p_resultado, self.t_resultado()),
                       ("Restricción de no negatividad (3)", self.p_restriccion, self.t_restriccion()),
                       ("Alerta de stock mínimo (4)", self.p_stock, self.t_stock()),
                       ("Alerta de vencimiento (5)", self.p_venc, self.t_venc()),
                       ("Conclusión", self.p_conclusion, self.t_conclusion())]

    def ir(self, n):
        if not self.pasos or not self.c.winfo_exists():
            return
        self.paso = max(0, min(n, len(self.pasos) - 1))
        titulo, dibujo, texto = self.pasos[self.paso]
        self.titulo.configure(text=f"Paso {self.paso + 1} de {len(self.pasos)}  ·  {titulo}")
        self.c.delete("all")
        dibujo()
        self.texto.configure(text=texto)
        self.dibujar_nav()
        ult = len(self.pasos) - 1
        for b, ok in ((self.b_ini, self.paso > 0), (self.b_ant, self.paso > 0),
                      (self.b_sig, self.paso < ult), (self.b_fin, self.paso < ult)):
            b.configure(state="normal" if ok else "disabled", bg=self.bases[b] if ok else "#999999")

    def dibujar_nav(self):
        self.nav.delete("all")
        n = len(self.pasos)
        ancho = max(self.nav.winfo_width(), ANCHO)
        sep = min(50, (ancho - 40) / max(n - 1, 1))
        x0 = 20
        self.nav.create_line(x0, 20, x0 + sep * (n - 1), 20, fill=BORDE, width=3)
        for i in range(n):
            x = x0 + sep * i
            hecho, actual = i < self.paso, i == self.paso
            color = NARANJA if actual else (VERDE if hecho else BLANCO)
            self.nav.create_oval(x - 12, 8, x + 12, 32, fill=color, outline=NARANJA if actual else BORDE, width=2,
                                 tags=(f"p{i}",))
            self.nav.create_text(x, 20, text=str(i + 1), font=(FUENTE, 9, "bold"),
                                 fill=NEGRO if actual else (BLANCO if hecho else GRIS), tags=(f"p{i}",))
            self.nav.tag_bind(f"p{i}", "<Button-1>", lambda e, i=i: self.ir(i))
        self.nav.configure(cursor="hand2")

    # ------------------------------------------------------------------
    # Dibujo: piezas comunes
    # ------------------------------------------------------------------
    def corchetes(self, x, y, w, alto, color=NEGRO):
        for sx, dx in ((x, 8), (x + w, -8)):
            self.c.create_line(sx + dx, y, sx, y, sx, y + alto, sx + dx, y + alto, fill=color, width=2)

    def matriz(self, x, y, valores, color, w=80, rh=34, tam=14):
        alto = rh * len(valores)
        self.corchetes(x, y, w, alto)
        for r, v in enumerate(valores):
            self.c.create_text(x + w / 2, y + rh * r + rh / 2, text=v, fill=color if v != "?" else "#BBBBBB",
                               font=(FUENTE, tam, "bold"))
        return alto

    def ecuacion(self, F=None, fila_resaltada=None, y0=72):
        """Dibuja F = I + E − D con vectores columna. F: lista de textos ('?' si aún no se conoce)."""
        P, n = self.datos["productos"], len(self.datos["productos"])
        rh = 34
        xs = [180, 305, 430, 555]
        letras = [("F", "final", C_F), ("I", "inicial", C_I), ("E", "entradas", C_E), ("D", "salidas", C_D)]
        if fila_resaltada is not None:
            self.c.create_rectangle(10, y0 + rh * fila_resaltada, 640, y0 + rh * (fila_resaltada + 1),
                                    fill="#FFF3B0", outline="#E8C547")
        for x, (l, desc, col) in zip(xs, letras):
            self.c.create_text(x + 40, y0 - 30, text=l, font=(FUENTE, 20, "bold"), fill=col)
            self.c.create_text(x + 40, y0 - 10, text=desc, font=(FUENTE, 9), fill=GRIS)
        F = F or ["?"] * n
        vals = [F, [fmt(p[2]) for p in P], [fmt(p[3]) for p in P], [fmt(p[4]) for p in P]]
        for x, v, (_l, _d, col) in zip(xs, vals, letras):
            self.matriz(x, y0, v, col, rh=rh)
        medio = y0 + rh * n / 2
        for x, op in zip([xs[0] + 80, xs[1] + 80, xs[2] + 80], ["=", "+", "−"]):
            self.c.create_text(x + 22, medio, text=op, font=(FUENTE, 24, "bold"), fill=TEXTO)
        for i, p in enumerate(P):
            self.c.create_text(12, y0 + rh * i + rh / 2, anchor="w", text=corto(p[0], 17),
                               font=(FUENTE, 9), fill=GRIS)
            self.c.create_text(642, y0 + rh * i + rh / 2, anchor="w", text=p[1], font=(FUENTE, 9), fill=GRIS)
        return y0 + rh * n

    def barras_fila(self, y, i):
        """Dos barras: arriba I + E; abajo lo que queda (F) y lo que salió (D)."""
        p = self.datos["productos"][i]
        I, E, D = p[2], p[3], p[4]
        F = I + E - D
        total = max(I + E, D, Decimal("0.01"))
        x0, ancho = 150, 520
        esc = lambda v: float(max(v, 0)) / float(total) * ancho
        c = self.c
        c.create_text(12, y + 12, anchor="w", text="Había + entró", font=(FUENTE, 9), fill=GRIS)
        c.create_rectangle(x0, y, x0 + esc(I), y + 24, fill=C_I, outline="")
        c.create_rectangle(x0 + esc(I), y, x0 + esc(I + E), y + 24, fill=C_E, outline="")
        if esc(I) > 40:
            c.create_text(x0 + esc(I) / 2, y + 12, text=f"I = {fmt(I)}", fill=BLANCO, font=(FUENTE, 9, "bold"))
        if esc(E) > 40:
            c.create_text(x0 + esc(I) + esc(E) / 2, y + 12, text=f"E = {fmt(E)}", fill=BLANCO,
                          font=(FUENTE, 9, "bold"))
        y2 = y + 40
        c.create_text(12, y2 + 12, anchor="w", text="Queda + salió", font=(FUENTE, 9), fill=GRIS)
        if F >= 0:
            c.create_rectangle(x0, y2, x0 + esc(F), y2 + 24, fill=C_F, outline="")
            c.create_rectangle(x0 + esc(F), y2, x0 + esc(F + D), y2 + 24, fill=C_D, outline="")
            if esc(F) > 40:
                c.create_text(x0 + esc(F) / 2, y2 + 12, text=f"F = {fmt(F)}", fill=BLANCO, font=(FUENTE, 9, "bold"))
            if esc(D) > 40:
                c.create_text(x0 + esc(F) + esc(D) / 2, y2 + 12, text=f"D = {fmt(D)}", fill=BLANCO,
                              font=(FUENTE, 9, "bold"))
        else:
            c.create_rectangle(x0, y2, x0 + esc(I + E), y2 + 24, fill=C_D, outline="")
            c.create_rectangle(x0 + esc(I + E), y2, x0 + esc(D), y2 + 24, fill=ROJO, outline="")
            c.create_text(x0 + esc(D) / 2, y2 + 12, text=f"D = {fmt(D)}  (más de lo disponible)", fill=BLANCO,
                          font=(FUENTE, 9, "bold"))
        if I + E == 0 and D == 0:
            c.create_text(x0, y2 + 40, anchor="w", text="Este producto no tuvo existencia ni movimientos.",
                          font=(FUENTE, 9), fill=GRIS)

    # ------------------------------------------------------------------
    # Dibujo: cada paso
    # ------------------------------------------------------------------
    def p_variables(self):
        P, c = self.datos["productos"], self.c
        cab = [("Producto", 18, TEXTO), ("Unidad", 190, TEXTO), ("I inicial", 270, C_I), ("E entradas", 360, C_E),
               ("D salidas", 465, C_D), ("m mínimo", 565, C_M)]
        c.create_rectangle(8, 14, ANCHO - 8, 46, fill="#F5EFE6", outline="")
        for t, x, col in cab:
            c.create_text(x, 30, anchor="w", text=t, font=(FUENTE, 11, "bold"), fill=col)
        for i, p in enumerate(P):
            y = 62 + i * 38
            if i % 2:
                c.create_rectangle(8, y - 6, ANCHO - 8, y + 30, fill="#FFFAF3", outline="")
            c.create_text(18, y + 12, anchor="w", text=corto(p[0], 22), font=(FUENTE, 11))
            c.create_text(190, y + 12, anchor="w", text=p[1], font=(FUENTE, 11), fill=GRIS)
            for v, x, col in zip(p[2:6], [270, 360, 465, 565], [C_I, C_E, C_D, C_M]):
                c.create_text(x, y + 12, anchor="w", text=fmt(v), font=(FUENTE, 12, "bold"), fill=col)
        y = 62 + len(P) * 38 + 14
        leyenda = [("I", "Existencia al iniciar el período", C_I), ("E", "Entradas del período", C_E),
                   ("D", "Salidas del período", C_D), ("F", "Inventario final (se calcula)", C_F),
                   ("m", "Stock mínimo (lo define el administrador)", C_M)]
        for k, (l, t, col) in enumerate(leyenda):
            xx, yy = 18 + (k % 2) * 335, y + (k // 2) * 30
            c.create_oval(xx, yy, xx + 24, yy + 24, fill=col, outline="")
            c.create_text(xx + 12, yy + 12, text=l, fill=BLANCO, font=(FUENTE, 10, "bold"))
            c.create_text(xx + 32, yy + 12, anchor="w", text=t, font=(FUENTE, 10), fill=TEXTO)

    def p_plantear(self):
        self.ecuacion()
        self.c.create_text(ANCHO / 2, 300, font=(FUENTE, 15, "bold"), fill=TEXTO,
                           text="final  =  lo que había  +  lo que entró  −  lo que salió")
        self.c.create_text(ANCHO / 2, 340, font=(FUENTE, 10), fill=GRIS,
                           text="Cada vector tiene una componente por producto (una fila por producto).")

    def p_fila(self, i):
        P = self.datos["productos"]
        F = [fmt(self.modelo["F"][j]) if j <= i else "?" for j in range(len(P))]
        fin = self.ecuacion(F, fila_resaltada=i)
        p = P[i]
        self.c.create_text(ANCHO / 2, fin + 24, font=(FUENTE, 15, "bold"), fill=TEXTO,
                           text=f"{fmt(p[2])} + {fmt(p[3])} − {fmt(p[4])} = {fmt(self.modelo['F'][i])}")
        self.barras_fila(fin + 48, i)

    def p_resultado(self):
        c, P, F = self.c, self.datos["productos"], self.modelo["F"]
        c.create_text(20, 22, anchor="w", font=(FUENTE, 16, "bold"), fill=C_F,
                      text=corto("F = (" + ",  ".join(fmt(f) for f in F) + ")", 46))
        series = [("I", C_I, [p[2] for p in P]), ("E", C_E, [p[3] for p in P]),
                  ("D", C_D, [p[4] for p in P]), ("F", C_F, F)]
        self.grafico_barras(series, [p[0] for p in P], 50, 355, 60, ANCHO - 20)

    def grafico_barras(self, series, nombres, ytop, ybase, x0, x1):
        c = self.c
        maximo = max([abs(v) for _l, _c, vs in series for v in vs] + [Decimal(1)])
        alto = ybase - ytop - 25
        esc = lambda v: float(v) / float(maximo) * alto
        c.create_line(x0, ybase, x1, ybase, fill=GRIS)
        c.create_line(x0, ytop, x0, ybase, fill=GRIS)
        for frac in (0.5, 1):
            yy = ybase - alto * frac
            c.create_line(x0, yy, x1, yy, fill="#EEE5D8", dash=(3, 3))
            c.create_text(x0 - 6, yy, anchor="e", text=fmt(maximo * Decimal(str(frac))), font=(FUENTE, 8), fill=GRIS)
        n = len(nombres)
        grupo = (x1 - x0) / n
        ancho_b = min(30, (grupo - 30) / len(series))
        for g in range(n):
            gx = x0 + grupo * g + (grupo - ancho_b * len(series)) / 2
            for s, (_l, col, vs) in enumerate(series):
                v = vs[g]
                h = esc(abs(v))
                bx = gx + s * ancho_b
                c.create_rectangle(bx + 2, ybase - h, bx + ancho_b - 2, ybase, fill=ROJO if v < 0 else col, outline="")
                c.create_text(bx + ancho_b / 2, ybase - h - 8, text=fmt(v), font=(FUENTE, 8, "bold"), fill=TEXTO)
            c.create_text(x0 + grupo * g + grupo / 2, ybase + 14, text=corto(nombres[g], 18), font=(FUENTE, 9),
                          fill=TEXTO)
        for k, (l, col, _v) in enumerate(series):
            c.create_rectangle(ANCHO - 170 + k * 40, 22, ANCHO - 156 + k * 40, 36, fill=col, outline="")
            c.create_text(ANCHO - 152 + k * 40, 29, anchor="w", text=l, font=(FUENTE, 10, "bold"))

    def p_restriccion(self):
        c, P, ok = self.c, self.datos["productos"], self.modelo["cumple"]
        c.create_text(ANCHO / 2, 24, text="Dᵢ ≤ Iᵢ + Eᵢ   ⇔   Fᵢ ≥ 0", font=(FUENTE, 16, "bold"), fill=TEXTO)
        x0, ancho = 160, 270
        for i, p in enumerate(P):
            y = 62 + i * 62
            disp, d = p[2] + p[3], p[4]
            maximo = max(disp, d, Decimal("0.01"))      # cada fila usa su propia escala
            esc = lambda v: float(max(v, 0)) / float(maximo) * ancho
            c.create_text(12, y + 16, anchor="w", text=corto(p[0], 19), font=(FUENTE, 10, "bold"))
            c.create_rectangle(x0, y, x0 + esc(disp), y + 32, fill="#D6E2F7", outline=C_I)
            c.create_text(x0 + max(esc(disp), 120) / 2, y + 16, text=f"I + E = {fmt(disp)}",
                          font=(FUENTE, 9), fill=C_I)
            xd = x0 + esc(d)
            c.create_line(xd, y - 6, xd, y + 38, fill=C_D if ok[i] else ROJO, width=3)
            c.create_text(xd, y + 50, text=f"D = {fmt(d)}", font=(FUENTE, 9, "bold"), fill=C_D if ok[i] else ROJO)
            col = VERDE if ok[i] else ROJO
            c.create_text(x0 + ancho + 24, y + 16, anchor="w", font=(FUENTE, 11, "bold"), fill=col,
                          text=f"{fmt(d)} ≤ {fmt(disp)}   {'✔ cumple' if ok[i] else '✘ NO cumple'}")

    def p_stock(self):
        c, P = self.c, self.datos["productos"]
        Fv, A = self.modelo["vigente"], self.modelo["A"]
        c.create_text(ANCHO / 2, 20, text="Aᵢ = 1  si  mᵢ > 0  y  Fᵢ − Xᵢ ≤ mᵢ",
                      font=(FUENTE, 15, "bold"))
        c.create_text(ANCHO / 2, 42, text="X = lo que está vencido (no se puede usar)      m = 0: sin aviso",
                      font=(FUENTE, 9), fill=GRIS)
        x0, ancho = 160, 250
        for i, p in enumerate(P):
            y = 68 + i * 62
            m, X, fv = p[5], p[6], Fv[i]
            maximo = max(fv, m, Decimal("0.01"))   # cada fila usa su propia escala
            esc = lambda v: float(max(v, 0)) / float(maximo) * ancho
            c.create_text(12, y + 16, anchor="w", text=corto(p[0], 19), font=(FUENTE, 10, "bold"))
            if X > 0:
                c.create_text(12, y + 34, anchor="w", text=f"F = {fmt(self.modelo['F'][i])}, X = {fmt(X)}",
                              font=(FUENTE, 8), fill=GRIS)
            c.create_rectangle(x0, y, x0 + esc(fv), y + 32, fill=ROJO if A[i] else C_F, outline="")
            ancho_f = esc(fv)
            etiqueta = f"F−X = {fmt(fv)}" if X > 0 else f"F = {fmt(fv)}"
            if ancho_f >= 90:                        # cabe dentro de la barra
                c.create_text(x0 + 6, y + 16, anchor="w", text=etiqueta, fill=BLANCO, font=(FUENTE, 10, "bold"))
            elif m <= 0 or esc(m) - ancho_f > 100:   # cabe entre la barra y la línea de m
                c.create_text(x0 + ancho_f + 6, y + 16, anchor="w", text=etiqueta,
                              fill=ROJO if A[i] else C_F, font=(FUENTE, 10, "bold"))
            else:                                    # debajo de la barra, a la izquierda
                c.create_text(x0, y + 48, anchor="w", text=etiqueta,
                              fill=ROJO if A[i] else C_F, font=(FUENTE, 10, "bold"))
            if m > 0:
                xm = x0 + esc(m)
                c.create_line(xm, y - 6, xm, y + 38, fill=NEGRO, width=2, dash=(4, 3))
                c.create_text(xm, y + 48, text=f"m = {fmt(m)}", font=(FUENTE, 9, "bold"))
            col = ROJO if A[i] else VERDE
            if m <= 0:
                linea1, linea2, col = "m = 0 → A = 0", "sin stock mínimo definido", GRIS
            else:
                signo = "≤" if fv <= m else ">"
                linea1 = f"{fmt(fv)} {signo} {fmt(m)} → A = {A[i]}"
                linea2 = "⚠ ALERTA: reponer" if A[i] else "✔ stock suficiente"
            c.create_text(x0 + ancho + 40, y + 8, anchor="w", font=(FUENTE, 11, "bold"), fill=col, text=linea1)
            c.create_text(x0 + ancho + 40, y + 28, anchor="w", font=(FUENTE, 10, "bold"), fill=col, text=linea2)

    def p_venc(self):
        c, V, k = self.c, self.modelo["V"], self.datos["k"]
        c.create_text(ANCHO / 2, 24, text=f"Vₗ = 1  si  qₗ > 0  y  (fvₗ − t) ≤ k        k = {k} días",
                      font=(FUENTE, 15, "bold"))
        if not V:
            c.create_text(ANCHO / 2, 190, justify="center", font=(FUENTE, 13), fill=GRIS,
                          text="Estos productos no tienen lotes con existencia\ny fecha de vencimiento: "
                               "no hay nada que evaluar.")
            return
        dmin = min([0] + [v["dias"] for v in V])
        dmax = max([k] + [v["dias"] for v in V]) + 10
        x0, x1 = 180, 540
        esc = lambda d: x0 + (d - dmin) / (dmax - dmin) * (x1 - x0)
        for i, v in enumerate(V):
            y = 80 + i * 56
            col = ROJO if v["alerta"] else VERDE
            c.create_text(12, y + 12, anchor="w", text=corto(v["producto"], 19), font=(FUENTE, 10, "bold"))
            c.create_text(12, y + 30, anchor="w", text=f"{v['codigo']}  q = {fmt(v['q'])} {v['unidad']}",
                          font=(FUENTE, 8), fill=GRIS)
            c.create_text(12, y + 43, anchor="w", text=f"vence {v['fv']}", font=(FUENTE, 8), fill=GRIS)
            a, b = sorted((esc(0), esc(v["dias"])))
            c.create_rectangle(a, y + 4, max(b, a + 3), y + 30, fill=col, outline="")
            c.create_text(max(b, esc(0), esc(k)) + 8, y + 17, anchor="w", font=(FUENTE, 10, "bold"), fill=col,
                          text=f"{v['dias']} días" if v["dias"] >= 0 else f"vencido hace {-v['dias']} días")
            c.create_text(x1 + 50, y + 6, anchor="w", font=(FUENTE, 10, "bold"), fill=col, text=f"V = {v['alerta']}")
            c.create_text(x1 + 50, y + 26, anchor="w", font=(FUENTE, 9, "bold"), fill=col,
                          text=("⚠ VENCIDO" if v["dias"] < 0 else "⚠ POR VENCER") if v["alerta"] else "✔ vigente")
        fin = 80 + len(V) * 56
        c.create_line(esc(0), 62, esc(0), fin, fill=NEGRO, width=2)
        c.create_text(esc(0), 54, text="hoy (t)", font=(FUENTE, 9, "bold"))
        c.create_line(esc(k), 62, esc(k), fin, fill=C_D, width=2, dash=(5, 3))
        c.create_text(esc(k), 54, text=f"k = {k}", font=(FUENTE, 9, "bold"), fill=C_D)
        c.create_text(esc(k) + 10, fin + 10, anchor="w", font=(FUENTE, 9), fill=GRIS,
                      text="a la izquierda de k: faltan k días o menos → alerta")

    def p_conclusion(self):
        c, m, d = self.c, self.modelo, self.datos
        P = d["productos"]
        tarjetas = [("F  inventario final", C_F, [f"{corto(p[0], 14)}: {fmt(f)} {p[1]}" for p, f in zip(P, m["F"])]),
                    ("A  stock mínimo", C_M, [f"{corto(p[0], 14)}: {a}" + ("  ⚠" if a else "")
                                              for p, a in zip(P, m["A"])]),
                    ("V  vencimiento", C_D, [f"{corto(v['producto'], 14)}: {v['alerta']}" + ("  ⚠" if v["alerta"] else "")
                                             for v in m["V"]] or ["(sin lotes)"])]
        for k, (t, col, lineas) in enumerate(tarjetas):
            x = 12 + k * 228
            c.create_rectangle(x, 20, x + 216, 250, fill="#FFFDF8", outline=BORDE)
            c.create_rectangle(x, 20, x + 216, 52, fill=col, outline="")
            c.create_text(x + 12, 36, anchor="w", text=t, fill=BLANCO, font=(FUENTE, 11, "bold"))
            for j, linea in enumerate(lineas[:7]):
                c.create_text(x + 12, 72 + j * 24, anchor="w", text=linea, font=(FUENTE, 10), fill=TEXTO)
        todo_ok = all(m["cumple"])
        c.create_rectangle(14, 272, ANCHO - 14, 360, fill="#E6F4EA" if todo_ok else "#FBE3E3", outline="")
        c.create_text(ANCHO / 2, 316, justify="center", font=(FUENTE, 12, "bold"), fill=VERDE if todo_ok else ROJO,
                      text=("✔ Todas las salidas cumplen la restricción (3)." if todo_ok else
                            "✘ Hay salidas que NO cumplen la restricción (3).") +
                           f"\nProductos con alerta de stock: {sum(m['A'])}    Lotes con alerta de vencimiento: "
                           f"{sum(v['alerta'] for v in m['V'])}")

    # ------------------------------------------------------------------
    # Textos explicativos
    # ------------------------------------------------------------------
    def t_variables(self):
        d = self.datos
        return (f"Período: desde {d['desde']} hasta hoy (t = {d['hoy']}). Para cada producto i, la base da Eᵢ (lo que "
                "entró en el período: compras y donaciones), Dᵢ (lo que salió: alimentación, tratamientos...) y mᵢ (stock "
                "mínimo). Iᵢ, lo que había al empezar, se obtiene de lo que hay hoy: Iᵢ = hoy − Eᵢ + Dᵢ. "
                f"Las alertas de vencimiento avisan con k = {d['k']} días de anticipación.")

    def t_plantear(self):
        return ("Cada vector tiene una componente por producto. El inventario final F es lo que había (I), más lo que "
                "entró (E), menos lo que salió (D). Es la ecuación (1): F = I + E − D. Se resuelve en una sola "
                "operación para todos los productos; todavía no conocemos F, así que se muestra con «?».")

    def t_fila(self, i):
        p = self.datos["productos"][i]
        f = self.modelo["F"][i]
        extra = (" ¡Atención! El resultado es negativo: se sacó más de lo que había."
                 if f < 0 else " La barra de abajo muestra que lo que queda (F) más lo que salió (D) suma lo que había "
                               "y entró (I + E).")
        return (f"Fila {i + 1} · {p[0]}: se reemplazan los valores de la fila y se hace la suma y la resta de ese "
                f"producto por separado: {fmt(p[2])} + {fmt(p[3])} − {fmt(p[4])} = {fmt(f)} {p[1]}"
                f"{'' if p[1].endswith('.') else '.'}" + extra)

    def t_resultado(self):
        P, F = self.datos["productos"], self.modelo["F"]
        partes = ", ".join(f"{fmt(f)} {p[1]} de {p[0].lower()}" for p, f in zip(P, F))
        return (f"Con todas las filas resueltas, el inventario final es F = ({', '.join(fmt(f) for f in F)}): quedan "
                f"{partes}. Es la existencia que muestra hoy la pantalla «Existencias» (stock total).")

    def t_restriccion(self):
        P, ok = self.datos["productos"], self.modelo["cumple"]
        malos = [p[0] for p, o in zip(P, ok) if not o]
        base = "Regla (3): no se puede sacar más de lo que hay. Dᵢ ≤ Iᵢ + Eᵢ es lo mismo que Fᵢ ≥ 0. "
        if malos:
            return base + (f"No cumplen: {', '.join(malos)}. Revisa los movimientos de esos productos: el sistema "
                           "bloquea las salidas sin stock suficiente.")
        return base + ("Todos los productos cumplen: la marca de cada salida (D) queda dentro de la barra de lo "
                       "disponible (I + E). El sistema lo garantiza: al registrar una salida sin stock suficiente "
                       "muestra «No hay stock vigente suficiente».")

    def t_stock(self):
        P, A = self.datos["productos"], self.modelo["A"]
        con = [p[0] for p, a in zip(P, A) if a]
        res = f"Activan la alerta: {', '.join(con)}." if con else "Ningún producto elegido activa la alerta."
        return ("Regla (4): Aᵢ vale 1 cuando lo que se puede usar no supera el stock mínimo. Como lo vencido (Xᵢ) no se "
                "puede entregar, el sistema compara Fᵢ − Xᵢ con mᵢ; y si mᵢ = 0 el producto no tiene aviso. " + res +
                " Son los «STOCK BAJO» de la pantalla «Alertas».")

    def t_venc(self):
        V, k = self.modelo["V"], self.datos["k"]
        if not V:
            return ("Regla (5): solo se evalúan los lotes con existencia y fecha de vencimiento. Los productos elegidos "
                    "no tienen ninguno.")
        con = [f"{v['producto']} {v['codigo']} ({v['dias']} días)" for v in V if v["alerta"]]
        res = f"Alertan: {', '.join(con)}." if con else "Ningún lote está por vencer."
        oculto = self.datos.get("lotes_ocultos", 0)
        extra = f" (Se muestran los {MAX_LOTES} que vencen primero; hay {oculto} más.)" if oculto else ""
        return (f"Regla (5): el lote l avisa (Vₗ = 1) cuando todavía tiene existencia (qₗ > 0) y faltan k = {k} días o "
                "menos para su vencimiento: (fvₗ − t) ≤ k. Un lote ya vencido también avisa. " + res +
                " Son los «POR VENCER» y «VENCIDO» de la pantalla «Alertas»." + extra)

    def t_conclusion(self):
        return ("Resumen: F dice cuánto queda de cada producto, A cuáles hay que reponer y V qué lotes se deben usar "
                "pronto. El sistema aplica estas reglas en cada entrada y salida y en las alertas del inicio.")
