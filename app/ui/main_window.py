"""Ventana principal de la aplicación: controles, listas de picos, tablas de resultados."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
import numpy as np

from app import analysis, reports
from app.config import APP_NAME, PALETTE, get_assets_path
from app.database import (
    DataLoadError,
    load_functional_groups_db,
    load_functional_groups_db_defaults,
    load_polymer_db,
    load_polymer_db_defaults,
)
from app.ui.plot_window import PlotWindow
from app.ui.theme import apply_ctk_theme, configure_treeview_style, style_listbox
from app.ui.widgets import HeaderBar, LabeledFrame


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        apply_ctk_theme()
        self.configure(fg_color=PALETTE["bg_primary"])
        self.title(f"{APP_NAME} — Industrial Inspection Service")
        self.geometry("1500x860")

        icon_path = get_assets_path("icon.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except tk.TclError:
                pass

        # Estado
        self.data = None
        self.x_data = None
        self.y_data = None
        self.peaks = None
        self.selected_peaks = []
        self.polymer_matches = []
        self.functional_group_annotations = []
        self.identified_groups = []

        self.comparison_data = None
        self.comparison_x = None
        self.comparison_y = None
        self.comparison_peaks = None

        self.plot_window = None

        self.polymer_db = self._load_polymer_db_safe()
        self.functional_groups_db = self._load_functional_groups_db_safe()

        self.treeview_style = configure_treeview_style()
        self._create_widgets()

    # ---------- Carga de bases de datos ----------

    def _load_polymer_db_safe(self):
        try:
            return load_polymer_db()
        except DataLoadError as e:
            messagebox.showerror(
                "Error en base de datos de polímeros",
                f"{e}\n\nSe cargarán los valores de fábrica (solo lectura) para esta sesión. "
                f"Corrija el archivo en la carpeta 'data' y reinicie la aplicación.",
            )
            return load_polymer_db_defaults()

    def _load_functional_groups_db_safe(self):
        try:
            return load_functional_groups_db()
        except DataLoadError as e:
            messagebox.showerror(
                "Error en base de datos de grupos funcionales",
                f"{e}\n\nSe cargarán los valores de fábrica (solo lectura) para esta sesión. "
                f"Corrija el archivo en la carpeta 'data' y reinicie la aplicación.",
            )
            return load_functional_groups_db_defaults()

    # ---------- Construcción de la interfaz ----------

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = HeaderBar(self, subtitle="Analizador FTIR de Polímeros Industriales")
        header.grid(row=0, column=0, sticky="ew")

        main_frame = ctk.CTkFrame(self, fg_color=PALETTE["bg_primary"])
        main_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        main_frame.grid_columnconfigure((0, 1, 2), weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)

        self._build_controls(main_frame)
        self._build_params(main_frame)
        self._build_peaks_panel(main_frame)
        self._build_polymer_panel(main_frame)
        self._build_groups_panel(main_frame)
        self._build_detail_panel(main_frame)

    def _build_controls(self, parent):
        control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        control_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))

        buttons = [
            ("Cargar Espectro", self.load_file),
            ("Abrir Gráfico", self.open_plot_window),
            ("Detectar Picos Automáticos", self.auto_detect_peaks),
            ("Identificar Polímero", self.identify_polymer_analysis),
            ("Mostrar Grupos Funcionales", self.show_functional_groups),
            ("Cargar Comparación", self.load_comparison_file),
            ("Ejecutar Comparativa", self.run_comparison),
            ("Limpiar Comparación", self.clear_comparison),
            ("Limpiar Análisis", self.clear_analysis),
            ("Exportar Reporte", self.export_report),
            ("Exportar Reporte Word", self.export_word_report),
        ]
        for text, cmd in buttons:
            ctk.CTkButton(control_frame, text=text, command=cmd, height=30,
                         fg_color=PALETTE["accent"], hover_color=PALETTE["accent_hover"],
                         ).pack(side=tk.LEFT, padx=4, pady=2)

    def _build_params(self, parent):
        frame = LabeledFrame(parent, text="Parámetros de Análisis")
        frame.grid(row=1, column=0, sticky="new", pady=6, padx=(0, 6))
        body = frame.body

        ctk.CTkLabel(body, text="Umbral detección:", text_color=PALETTE["text_secondary"]).grid(
            row=0, column=0, sticky="w", pady=4)
        self.threshold_var = tk.DoubleVar(value=0.1)
        self.threshold_label = ctk.CTkLabel(body, text="0.10", text_color=PALETTE["text_primary"], width=40)
        slider = ctk.CTkSlider(body, from_=0.01, to=0.5, variable=self.threshold_var,
                               command=self._on_threshold_change, width=140)
        slider.grid(row=0, column=1, padx=6)
        self.threshold_label.grid(row=0, column=2)

        ctk.CTkLabel(body, text="Distancia mínima:", text_color=PALETTE["text_secondary"]).grid(
            row=1, column=0, sticky="w", pady=4)
        self.distance_var = tk.IntVar(value=15)
        ttk.Spinbox(body, from_=5, to=50, textvariable=self.distance_var, width=6).grid(
            row=1, column=1, sticky="w", padx=6)

        ctk.CTkLabel(body, text="Tolerancia (cm⁻¹):", text_color=PALETTE["text_secondary"]).grid(
            row=2, column=0, sticky="w", pady=4)
        self.tolerance_var = tk.IntVar(value=15)
        ttk.Spinbox(body, from_=5, to=30, textvariable=self.tolerance_var, width=6).grid(
            row=2, column=1, sticky="w", padx=6)

    def _on_threshold_change(self, value):
        self.threshold_label.configure(text=f"{float(value):.2f}")

    def _build_peaks_panel(self, parent):
        frame = LabeledFrame(parent, text="Picos Detectados")
        frame.grid(row=1, column=1, sticky="nsew", pady=6, padx=6)
        body = frame.body
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        list_frame = tk.Frame(body, bg=PALETTE["bg_surface"])
        list_frame.grid(row=0, column=0, sticky="nsew")

        self.peak_listbox = tk.Listbox(list_frame, height=8, width=45)
        style_listbox(self.peak_listbox)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.peak_listbox.yview)
        self.peak_listbox.configure(yscrollcommand=scrollbar.set)

        self.peak_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.peak_listbox.bind("<<ListboxSelect>>", self.on_peak_select)

    def _build_polymer_panel(self, parent):
        frame = LabeledFrame(parent, text="Identificación de Polímeros")
        frame.grid(row=1, column=2, sticky="nsew", pady=6, padx=(6, 0))
        body = frame.body
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        columns = ("polymer", "score", "confidence", "density", "applications")
        self.polymer_tree = ttk.Treeview(body, columns=columns, show="headings", height=8)
        self.polymer_tree.heading("polymer", text="Polímero")
        self.polymer_tree.heading("score", text="Score")
        self.polymer_tree.heading("confidence", text="Confianza")
        self.polymer_tree.heading("density", text="Densidad")
        self.polymer_tree.heading("applications", text="Aplicaciones")
        self.polymer_tree.column("polymer", width=180)
        self.polymer_tree.column("score", width=60)
        self.polymer_tree.column("confidence", width=80)
        self.polymer_tree.column("density", width=70)
        self.polymer_tree.column("applications", width=180)

        scrollbar = ttk.Scrollbar(body, orient=tk.VERTICAL, command=self.polymer_tree.yview)
        self.polymer_tree.configure(yscrollcommand=scrollbar.set)
        self.polymer_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.polymer_tree.bind("<<TreeviewSelect>>", self.on_polymer_select)

    def _build_groups_panel(self, parent):
        frame = LabeledFrame(parent, text="Grupos Funcionales Identificados")
        frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=6)
        body = frame.body
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        columns = ("wavenumber", "group", "bond", "color")
        self.group_tree = ttk.Treeview(body, columns=columns, show="headings", height=6)
        self.group_tree.heading("wavenumber", text="N° Onda (cm⁻¹)")
        self.group_tree.heading("group", text="Grupo Funcional")
        self.group_tree.heading("bond", text="Tipo de Vibración")
        self.group_tree.heading("color", text="Color")
        self.group_tree.column("wavenumber", width=110)
        self.group_tree.column("group", width=220)
        self.group_tree.column("bond", width=160)
        self.group_tree.column("color", width=90)

        scrollbar = ttk.Scrollbar(body, orient=tk.VERTICAL, command=self.group_tree.yview)
        self.group_tree.configure(yscrollcommand=scrollbar.set)
        self.group_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.group_tree.bind("<<TreeviewSelect>>", self.on_group_select)

    def _build_detail_panel(self, parent):
        frame = LabeledFrame(parent, text="Detalles del Polímero Seleccionado")
        frame.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=6)
        body = frame.body
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        self.detail_text = ctk.CTkTextbox(body, height=140, fg_color=PALETTE["bg_surface_alt"],
                                          text_color=PALETTE["text_primary"], wrap="word")
        self.detail_text.grid(row=0, column=0, sticky="nsew")

    # ---------- Ventana de gráfico ----------

    def open_plot_window(self):
        if self.data is None:
            messagebox.showwarning("Advertencia", "Primero cargue un espectro")
            return

        if self.plot_window is None or not self.plot_window.winfo_exists():
            self.plot_window = PlotWindow(self, self)
        else:
            self.plot_window.lift()
            self.plot_window.focus_force()

    def on_plot_window_closed(self):
        self.plot_window = None

    def _refresh_plot(self):
        if self.plot_window is not None and self.plot_window.winfo_exists():
            self.plot_window.plot_data()

    def add_manual_peak(self, x_val, y_val):
        self.selected_peaks.append((x_val, y_val))
        self.update_peak_list()

    # ---------- Carga de archivos ----------

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar espectro FTIR",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return
        try:
            data = np.loadtxt(file_path, delimiter=",")
            self.x_data = data[:, 0]
            self.y_data = data[:, 1]
            self.data = data
            self.y_data = (self.y_data - np.min(self.y_data)) / (np.max(self.y_data) - np.min(self.y_data))

            self._refresh_plot()
            messagebox.showinfo("Éxito", "Archivo cargado correctamente. Use 'Abrir Gráfico' para visualizar.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")

    def load_comparison_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar espectro FTIR para comparación",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return
        try:
            data = np.loadtxt(file_path, delimiter=",")
            self.comparison_x = data[:, 0]
            self.comparison_y = data[:, 1]
            self.comparison_data = data
            self.comparison_y = (self.comparison_y - np.min(self.comparison_y)) / (
                np.max(self.comparison_y) - np.min(self.comparison_y))

            threshold = self.threshold_var.get()
            distance = self.distance_var.get()
            self.comparison_peaks, _ = analysis.detect_peaks(self.comparison_y, threshold, distance)

            messagebox.showinfo("Éxito", f"Espectro de comparación cargado. Se detectaron "
                                         f"{len(self.comparison_peaks)} picos.")
            self._refresh_plot()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo de comparación: {str(e)}")

    # ---------- Detección y análisis ----------

    def auto_detect_peaks(self):
        if self.data is None:
            messagebox.showwarning("Advertencia", "Primero cargue un espectro")
            return
        try:
            threshold = self.threshold_var.get()
            distance = self.distance_var.get()
            self.peaks, _ = analysis.detect_peaks(self.y_data, threshold, distance)

            self.update_peak_list()
            self._refresh_plot()
            messagebox.showinfo("Éxito", f"Se detectaron {len(self.peaks)} picos")
        except Exception as e:
            messagebox.showerror("Error", f"Error en detección de picos: {str(e)}")

    def update_peak_list(self):
        self.peak_listbox.delete(0, tk.END)
        if self.peaks is not None:
            for peak_idx in self.peaks:
                x_val = self.x_data[peak_idx]
                y_val = self.y_data[peak_idx]
                self.peak_listbox.insert(tk.END, f"{x_val:.1f} cm⁻¹ - {y_val:.3f}")
        for x_val, y_val in self.selected_peaks:
            self.peak_listbox.insert(tk.END, f"{x_val:.1f} cm⁻¹ - {y_val:.3f} (manual)")

    def identify_polymer_analysis(self):
        if (self.peaks is None or len(self.peaks) == 0) and len(self.selected_peaks) == 0:
            messagebox.showwarning("Advertencia", "No hay picos para analizar")
            return

        detected_peaks = []
        if self.peaks is not None:
            for peak_idx in self.peaks:
                detected_peaks.append({"wavenumber": self.x_data[peak_idx], "intensity": self.y_data[peak_idx]})
        for x_val, y_val in self.selected_peaks:
            detected_peaks.append({"wavenumber": x_val, "intensity": y_val})

        self.polymer_matches = analysis.identify_polymer(detected_peaks, self.polymer_db)

        for item in self.polymer_tree.get_children():
            self.polymer_tree.delete(item)

        for polymer_code, match_data in self.polymer_matches:
            polymer_info = self.polymer_db[polymer_code]
            score = match_data["score"]
            total_expected = match_data["total_expected"]
            confidence = f"{(score / total_expected) * 100:.1f}%"

            self.polymer_tree.insert("", "end", values=(
                polymer_info["name"], f"{score:.2f}", confidence,
                polymer_info["density"], polymer_info["applications"],
            ))

        messagebox.showinfo("Análisis completado",
                            f"Se analizaron {len(detected_peaks)} picos. "
                            f"Revise los resultados de identificación.")

    def show_functional_groups(self):
        if (self.peaks is None or len(self.peaks) == 0) and len(self.selected_peaks) == 0:
            messagebox.showwarning("Advertencia", "No hay picos para analizar grupos funcionales")
            return

        self.functional_group_annotations = []
        self.identified_groups = []

        if self.peaks is not None:
            for peak_idx in self.peaks:
                x_val = self.x_data[peak_idx]
                y_val = self.y_data[peak_idx]
                matches = analysis.identify_functional_groups(x_val, self.functional_groups_db)
                if matches:
                    self._register_group_match(x_val, y_val, matches[0])

        for x_val, y_val in self.selected_peaks:
            matches = analysis.identify_functional_groups(x_val, self.functional_groups_db)
            if matches:
                self._register_group_match(x_val, y_val, matches[0])

        self.update_group_list()
        self._refresh_plot()
        messagebox.showinfo("Grupos Funcionales",
                            f"Se identificaron {len(self.functional_group_annotations)} grupos funcionales")

    def _register_group_match(self, x_val, y_val, best_match):
        self.functional_group_annotations.append({
            "x": x_val, "y": y_val, "group": best_match["group"],
            "bond": best_match["bond"], "color": best_match["color"],
        })
        self.identified_groups.append({
            "wavenumber": x_val, "group": best_match["group"],
            "bond": best_match["bond"], "color": best_match["color"],
        })

    def update_group_list(self):
        for item in self.group_tree.get_children():
            self.group_tree.delete(item)
        for group_info in self.identified_groups:
            self.group_tree.insert("", "end", values=(
                f"{group_info['wavenumber']:.1f}", group_info["group"],
                group_info["bond"], group_info["color"],
            ))

    def run_comparison(self):
        if self.data is None or self.comparison_data is None:
            messagebox.showwarning("Advertencia", "Debe cargar ambos espectros (principal y comparación)")
            return
        try:
            similarity = analysis.compare_spectra(self.x_data, self.y_data,
                                                   self.comparison_x, self.comparison_y,
                                                   self.tolerance_var.get())

            main_peaks = []
            if self.peaks is not None:
                for peak_idx in self.peaks:
                    main_peaks.append({"wavenumber": self.x_data[peak_idx], "intensity": self.y_data[peak_idx]})

            comp_peaks = []
            if self.comparison_peaks is not None:
                for peak_idx in self.comparison_peaks:
                    comp_peaks.append({"wavenumber": self.comparison_x[peak_idx],
                                       "intensity": self.comparison_y[peak_idx]})

            tolerance = self.tolerance_var.get()
            common_peaks = analysis.find_common_peaks(main_peaks, comp_peaks, tolerance)
            avg_intensity_diff = (np.mean([p["difference"] for p in common_peaks])
                                  if common_peaks else 0)

            result_text = "RESULTADOS DE COMPARATIVA\n" + "=" * 40 + "\n"
            result_text += f"Similitud de coseno: {similarity:.4f}\n"
            result_text += f"Picos en espectro principal: {len(main_peaks)}\n"
            result_text += f"Picos en espectro comparación: {len(comp_peaks)}\n"
            result_text += f"Picos comunes: {len(common_peaks)}\n"
            result_text += f"Diferencia promedio de intensidad: {avg_intensity_diff:.4f}\n\n"

            if common_peaks:
                result_text += "PICOS COMUNES:\n" + "-" * 30 + "\n"
                for i, peak in enumerate(common_peaks[:10]):
                    result_text += f"{i+1}. {peak['wavenumber']:.1f} cm⁻¹ (ΔInt: {peak['difference']:.3f})\n"

            self.detail_text.delete("1.0", tk.END)
            self.detail_text.insert("1.0", result_text)

            self._refresh_plot()
        except Exception as e:
            messagebox.showerror("Error", f"Error en comparativa: {str(e)}")

    def clear_comparison(self):
        self.comparison_data = None
        self.comparison_x = None
        self.comparison_y = None
        self.comparison_peaks = None
        self._refresh_plot()
        messagebox.showinfo("Éxito", "Datos de comparación limpiados")

    def clear_analysis(self):
        self.selected_peaks = []
        self.peaks = None
        self.polymer_matches = []
        self.functional_group_annotations = []
        self.identified_groups = []
        self.update_peak_list()
        for item in self.polymer_tree.get_children():
            self.polymer_tree.delete(item)
        for item in self.group_tree.get_children():
            self.group_tree.delete(item)
        self.detail_text.delete("1.0", tk.END)
        self._refresh_plot()

    # ---------- Selección en listas/tablas ----------

    def on_polymer_select(self, event):
        selection = self.polymer_tree.selection()
        if not (selection and self.polymer_matches):
            return
        item = selection[0]
        index = self.polymer_tree.index(item)
        polymer_code, match_data = self.polymer_matches[index]
        polymer_info = self.polymer_db[polymer_code]

        detail_text = f"POLÍMERO: {polymer_info['name']}\n"
        detail_text += f"Densidad: {polymer_info['density']} g/cm³\n"
        detail_text += f"Aplicaciones: {polymer_info['applications']}\n\n"
        detail_text += "BANDAS CARACTERÍSTICAS:\n" + "-" * 50 + "\n"

        for i, peak_match in enumerate(match_data["matched_peaks"]):
            detail_text += (f"{i+1}. {peak_match['expected']['wavenumber']} cm⁻¹ "
                            f"({peak_match['expected']['intensity']}) - "
                            f"Detectado: {peak_match['detected']['wavenumber']:.1f} cm⁻¹ "
                            f"(Δ: {peak_match['distance']:.1f} cm⁻¹)\n")
            detail_text += f"   Descripción: {peak_match['expected']['description']}\n\n"

        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert("1.0", detail_text)

        if self.plot_window is not None and self.plot_window.winfo_exists():
            self.plot_window.plot_data()
            for peak_match in match_data["matched_peaks"]:
                self.plot_window.highlight_point(
                    peak_match["detected"]["wavenumber"], peak_match["detected"]["intensity"],
                    color=PALETTE["success"])

    def on_group_select(self, event):
        selection = self.group_tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.group_tree.item(item)["values"]
        wavenumber = float(values[0])
        if self.plot_window is not None and self.plot_window.winfo_exists():
            self.plot_window.plot_data()
            self.plot_window.highlight_point(wavenumber, 0.5, color=values[3])

    def on_peak_select(self, event):
        selection = self.peak_listbox.curselection()
        if not selection:
            return
        if not (self.plot_window is not None and self.plot_window.winfo_exists()):
            return
        self.plot_window.plot_data()
        index = selection[0]

        if self.peaks is not None and index < len(self.peaks):
            x_val = self.x_data[self.peaks[index]]
            y_val = self.y_data[self.peaks[index]]
        else:
            manual_index = index - (len(self.peaks) if self.peaks is not None else 0)
            x_val, y_val = self.selected_peaks[manual_index]

        self.plot_window.highlight_point(x_val, y_val, color=PALETTE["warning"])

    # ---------- Exportación ----------

    def export_report(self):
        if not self.polymer_matches and not self.identified_groups:
            messagebox.showwarning("Advertencia", "No hay análisis para exportar")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")])
        if not file_path:
            return
        try:
            reports.export_text_report(file_path, self.polymer_matches, self.polymer_db,
                                       self.identified_groups, self.peaks, self.x_data,
                                       self.y_data, self.selected_peaks)
            messagebox.showinfo("Éxito", "Reporte exportado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def export_word_report(self):
        if not self.polymer_matches and not self.identified_groups:
            messagebox.showwarning("Advertencia", "No hay análisis para exportar en Word")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx", filetypes=[("Word Document", "*.docx")])
        if not file_path:
            return
        try:
            reports.export_word_report(
                file_path, self.x_data, self.y_data, self.peaks, self.polymer_matches,
                self.polymer_db, self.identified_groups, self.selected_peaks,
                self.threshold_var.get(), self.distance_var.get(), self.tolerance_var.get(),
            )
            messagebox.showinfo("Éxito", "Reporte de Word exportado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Word: {str(e)}")
