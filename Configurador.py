import tkinter as tk
from tkinter import ttk, messagebox
import conexion

# --- COLORES Y FUENTES DE LA ESTÉTICA ---
BG_HEADER      = "#1565C0"
BG_BUTTON_BAR  = "#F3F3F3"
BG_MAIN        = "#FFFFFF"
FG_WHITE       = "#FFFFFF"
FG_BLUE_LABEL  = "#00479E"
BORDER_COLOR   = "#000000"
FONT_HEAD      = ("Segoe UI", 18, "bold")
FONT_SUBHEAD   = ("Segoe UI", 10)
FONT_LABEL     = ("Segoe UI", 8, "bold")
FONT_MONO      = ("Consolas", 10)
FONT_BTN       = ("Segoe UI", 9, "bold")


def apply_theme():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Light.TCombobox",
                    fieldbackground=BG_MAIN,
                    background=BG_MAIN,
                    foreground="black",
                    selectbackground="#E0E0E0",
                    selectforeground="black",
                    bordercolor=BORDER_COLOR,
                    arrowcolor="black",
                    relief="flat",
                    padding=5)


class ConfiguradorUI:
    """Configurador de items para ST40 - 9 campos (Tabla 2.2 del PDF TLA_E34_ST40)."""

    def __init__(self, root):
        self.root = root
        self.root.title("Configuración")
        self.root.geometry("580x620")
        self.root.minsize(580, 600)
        self.root.configure(bg=BG_MAIN)
        self.root.focus_force()
        self.root.attributes("-topmost", False)

        apply_theme()
        self._build_ui()
        self.cargar()

    def _build_ui(self):
        try:
            self.root.iconbitmap("favicon.ico")
        except:
            pass

        # --- HEADER ---
        header = tk.Frame(self.root, bg=BG_HEADER)
        header.pack(fill="x")

        tk.Label(header, text="⚙ Configurador", font=FONT_HEAD,
                 bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(20, 5))

        self.subtitle_var = tk.StringVar(value="Todos los campos son obligatorios.")
        tk.Label(header, textvariable=self.subtitle_var, font=FONT_SUBHEAD,
                 bg=BG_HEADER, fg=FG_WHITE).pack(anchor="w", padx=24, pady=(0, 20))

        # --- BARRA DE BOTONES ---
        btn_frame = tk.Frame(self.root, bg=BG_BUTTON_BAR)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="💾 Guardar Cambios", command=self.guardar,
                  bg=BG_HEADER, fg=FG_WHITE, font=FONT_BTN, relief="flat",
                  cursor="hand2", padx=15, pady=6).pack(side="right", padx=(10, 24), pady=10)

        tk.Button(btn_frame, text="✕ Cancelar", command=self.cancelar,
                  bg=BG_MAIN, fg="black", font=FONT_BTN, relief="solid", bd=1,
                  cursor="hand2", padx=15, pady=5).pack(side="right", pady=10)

        # --- CONTENIDO PRINCIPAL ---
        inner = tk.Frame(self.root, bg=BG_MAIN)
        inner.pack(fill="both", expand=True, padx=24, pady=20)
        
        # IMPORTANTE: Configurar columnas con uniform para que sean del mismo tamaño
        inner.columnconfigure(0, weight=1, uniform="col")
        inner.columnconfigure(1, weight=1, uniform="col")

        entry_kwargs = {"bg": BG_MAIN, "fg": "black", "relief": "flat", "font": FONT_MONO,
                        "highlightthickness": 1, "highlightbackground": BORDER_COLOR,
                        "highlightcolor": BG_HEADER}

        # Campos en el orden de la Tabla 2.2.
        self.campos = [
            ("STATION",  "machine_name"),
            ("OPERATOR",   "id_operator"),
            ("PASSWORD",      "password"),
            ("PROCESS NAME",  "process_name"),
            ("PROGRAM NAME+VERSION",     "program_name_version"),
            ("CLIENT ID",     "client_id"),
            ("PRINT MACRO",   "print_macro"),
            ("CONTAINER", "qty_pcba"),
        ]

        self.entries = {}
        self.container_var = tk.StringVar(value="64")
        self.radio_var = tk.StringVar(value="fixed")

        # ANCHO FIJO para todos los campos
        ENTRY_WIDTH = 30

        for idx, (label, attr) in enumerate(self.campos):
            col = idx % 2
            fila_label = (idx // 2) * 2
            fila_entry = fila_label + 1
            padx_l = (15, 5) if col == 1 else (5, 15)  # Padding simétrico

            # Label
            tk.Label(inner, text=label, bg=BG_MAIN, fg=FG_BLUE_LABEL,
                     font=FONT_LABEL).grid(row=fila_label, column=col, sticky="w", padx=padx_l, pady=(0, 2))

            # Entry o Container
            if attr == "qty_pcba":
                # Frame para container
                container_frame = tk.Frame(inner, bg=BG_MAIN)
                container_frame.grid(row=fila_entry, column=col, sticky="w", padx=padx_l, pady=(2, 15))
                
                # Usar grid para organizar los radiobuttons
                # Fila 0: Radio buttons
                rb_fixed = tk.Radiobutton(container_frame, text="64 PCBA's", variable=self.radio_var,
                                         value="fixed", bg=BG_MAIN, font=FONT_MONO,
                                         command=self.on_radio_select)
                rb_fixed.grid(row=0, column=0, sticky="w", padx=(0, 10))
                
                rb_custom = tk.Radiobutton(container_frame, text="PARCIAL PCBA's:", variable=self.radio_var,
                                          value="custom", bg=BG_MAIN, font=FONT_MONO,
                                          command=self.on_radio_select)
                rb_custom.grid(row=0, column=1, sticky="w")
                
                # Fila 1: Entry para personalizado (debajo del radio button personalizado)
                self.container_entry = tk.Entry(container_frame, width=10, **entry_kwargs)
                self.container_entry.grid(row=1, column=1, sticky="w", padx=(0, 0), pady=(5, 0))
                self.container_entry.bind('<KeyRelease>', self.validate_numeric_input)
                self.container_entry.config(state='disabled')
                
                # Configurar columnas del container_frame
                container_frame.grid_columnconfigure(0, weight=0)  # Radio fijo
                container_frame.grid_columnconfigure(1, weight=1)  # Radio personalizado y entry
                
                self.entries[attr] = self.container_entry
            else:
                entry = tk.Entry(inner, width=ENTRY_WIDTH, **entry_kwargs)
                entry.grid(row=fila_entry, column=col, sticky="w", padx=padx_l, ipady=5, pady=(2, 15))
                self.entries[attr] = entry

        # --- STATUS BAR ---
        self.status_var = tk.StringVar(value="Listo")
        tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 8),
                 bg=BG_MAIN, fg="#888888").pack(side="bottom", anchor="w", padx=24, pady=5)

    def on_radio_select(self):
        """Maneja la selección de los radiobuttons"""
        if self.radio_var.get() == "fixed":
            self.container_entry.config(state='disabled')
            self.container_var.set("64")
        else:
            self.container_entry.config(state='normal')
            self.container_entry.focus()
            if not self.container_entry.get():
                self.container_entry.insert(0, "0")
            self.validate_numeric_input()

    def validate_numeric_input(self, event=None):
        """Valida que solo se ingresen números en el campo personalizado"""
        current_value = self.container_entry.get()
        
        if current_value == "" or current_value == ".":
            return
        
        if current_value.replace('.', '', 1).isdigit():
            if current_value.count('.') <= 1:
                self.container_var.set(current_value)
                self.container_entry.config(fg="black")
            else:
                self.container_entry.config(fg="red")
        else:
            self.container_entry.config(fg="red")
            self.status_var.set("Solo se permiten números en el campo personalizado")
            
            if current_value:
                self.container_entry.delete(len(current_value)-1, tk.END)
                self.container_entry.config(fg="black")
                self.status_var.set("Listo")

    def get_container_value(self):
        """Obtiene el valor actual del container basado en la selección del radiobutton"""
        if self.radio_var.get() == "fixed":
            return "64"
        else:
            value = self.container_entry.get().strip()
            if not value:
                return "0"
            if value.replace('.', '', 1).isdigit():
                return value
            else:
                return "0"

    def cargar(self):
        """Precarga los 9 valores desde configurador_st40()."""
        try:
            datos = conexion.configurador_st40()
            if datos and datos != "FAILED":
                orden = ["machine_name", "id_operator", "password",
                         "process_name", "program_name_version", "client_id", "print_macro", "qty_pcba"]
                for i, attr in enumerate(orden):
                    if i < len(datos):
                        valor = datos[i]
                        if valor and str(valor).strip() not in ["(NULL)", "None", ""]:
                            if attr == "qty_pcba":
                                valor_str = str(valor).strip()
                                self.container_var.set(valor_str)
                                if valor_str == "64":
                                    self.radio_var.set("fixed")
                                    self.container_entry.config(state='disabled')
                                else:
                                    self.radio_var.set("custom")
                                    self.container_entry.config(state='normal')
                                    self.container_entry.delete(0, tk.END)
                                    self.container_entry.insert(0, valor_str)
                                    self.validate_numeric_input()
                            else:
                                e = self.entries[attr]
                                e.delete(0, tk.END)
                                e.insert(0, str(valor).strip())
        except Exception as e:
            print(f"Error interno al cargar datos: {e}")

    def guardar(self):
        v = {attr: self.entries[attr].get().strip() if attr != "qty_pcba" else self.get_container_value() 
             for attr in self.entries}
        
        try:
            datos_actuales = conexion.configurador_st40()
            vacio = (datos_actuales == "FAILED"
                     or datos_actuales == ("", "", "", "", "", "", "", ""))

            args = (v["machine_name"], v["id_operator"], v["password"],
                    v["process_name"], v["program_name_version"], v["client_id"], v["print_macro"], v["qty_pcba"])

            if vacio:
                exito = conexion.insert_configurador_st40(*args)
                mensaje = "Configuración inicial creada con éxito."
            else:
                exito = conexion.update_configurador_st40(*args)
                mensaje = "Configuración actualizada correctamente."

            if exito:
                messagebox.showinfo("Éxito", mensaje, parent=self.root)
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error DB", str(e), parent=self.root)

    def cancelar(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguradorUI(root)
    root.mainloop()