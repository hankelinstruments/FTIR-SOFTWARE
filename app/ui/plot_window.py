"""Ventana separada con el gráfico matplotlib embebido (espectro, picos, grupos funcionales)."""
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from app.config import APP_ORG, PALETTE, get_assets_path
from app.ui.theme import apply_plot_theme


class PlotWindow(ctk.CTkToplevel):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.title("Gráfico FTIR - Espectro Completo")
        self.geometry("1200x750")
        self.configure(fg_color=PALETTE["bg_primary"])
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        icon_path = get_assets_path("icon.ico")
        if icon_path.exists():
            self.after(200, lambda: self._safe_iconbitmap(icon_path))

        header = ctk.CTkFrame(self, fg_color=PALETTE["bg_primary"], height=40, corner_radius=0)
        header.pack(fill=tk.X, side=tk.TOP)
        ctk.CTkLabel(
            header, text=f"{APP_ORG} — Espectro FTIR",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=PALETTE["text_primary"],
        ).pack(side=tk.LEFT, padx=12, pady=8)
        accent = ctk.CTkFrame(self, height=2, fg_color=PALETTE["accent"], corner_radius=0)
        accent.pack(fill=tk.X, side=tk.TOP)

        plot_frame = ctk.CTkFrame(self, fg_color=PALETTE["bg_surface"])
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fig = Figure(figsize=(12, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)

        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.update()

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        button_frame = ctk.CTkFrame(plot_frame, fg_color="transparent")
        button_frame.pack(fill=tk.X, pady=5)

        ctk.CTkButton(button_frame, text="Seleccionar Pico Manual",
                      command=self.start_manual_selection).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="Actualizar Gráfico",
                      command=self.plot_data).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="Cerrar", fg_color=PALETTE["danger"],
                      hover_color="#b94440", command=self._on_close).pack(side=tk.RIGHT, padx=5)

        self.canvas.mpl_connect("button_press_event", self.on_click)

        self.plot_data()

    def _safe_iconbitmap(self, icon_path):
        try:
            self.iconbitmap(str(icon_path))
        except tk.TclError:
            pass

    def _on_close(self):
        self.controller.on_plot_window_closed()
        self.destroy()

    def plot_data(self):
        c = self.controller
        if c.data is None:
            return

        self.ax.clear()

        self.ax.plot(c.x_data, c.y_data, "-", linewidth=1, alpha=0.9,
                     color=PALETTE["accent"], label="Espectro Principal")

        if c.comparison_data is not None:
            self.ax.plot(c.comparison_x, c.comparison_y, "-", linewidth=1, alpha=0.8,
                         color=PALETTE["warning"], label="Espectro Comparación")

            if c.comparison_peaks is not None:
                self.ax.plot(c.comparison_x[c.comparison_peaks], c.comparison_y[c.comparison_peaks],
                             "s", markersize=6, color=PALETTE["warning"],
                             label="Picos Comparación", alpha=0.8)

        self.ax.set_xlabel("Número de onda (cm⁻¹)")
        self.ax.set_ylabel("Absorbancia (normalizada)")
        self.ax.set_title("Espectro FTIR - Análisis de Polímeros")
        self.ax.invert_xaxis()

        if c.peaks is not None:
            self.ax.plot(c.x_data[c.peaks], c.y_data[c.peaks],
                         "o", markersize=6, color=PALETTE["danger"],
                         label="Picos detectados", alpha=0.85)

            for peak_idx in c.peaks:
                x_val = c.x_data[peak_idx]
                y_val = c.y_data[peak_idx]
                self.ax.annotate(f"{x_val:.0f}", (x_val, y_val),
                                 xytext=(5, 5), textcoords="offset points",
                                 fontsize=8, alpha=0.8, color=PALETTE["text_primary"])

        if c.selected_peaks:
            for peak_x, peak_y in c.selected_peaks:
                self.ax.plot(peak_x, peak_y, "o", markersize=8,
                             markerfacecolor="none", markeredgecolor=PALETTE["success"],
                             markeredgewidth=2, label="Pico manual")
                self.ax.annotate(f"{peak_x:.0f}", (peak_x, peak_y),
                                 xytext=(5, 5), textcoords="offset points",
                                 fontsize=8, alpha=0.8, color=PALETTE["text_primary"])

        if c.functional_group_annotations:
            for annotation in c.functional_group_annotations:
                x_val = annotation["x"]
                y_val = annotation["y"]
                group = annotation["group"]
                color = annotation["color"]

                existing_labels = [a.get_label() for a in self.ax.get_legend_handles_labels()[0]]
                self.ax.plot(x_val, y_val, "s", markersize=8, color=color,
                             label=group if group not in existing_labels else "")

                self.ax.annotate(group, (x_val, y_val),
                                 xytext=(10, 10), textcoords="offset points",
                                 fontsize=8, color=color, weight="bold",
                                 bbox=dict(boxstyle="round,pad=0.3",
                                           facecolor=PALETTE["bg_surface"], alpha=0.9,
                                           edgecolor=PALETTE["border"]))

        handles, labels = self.ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        if by_label:
            self.ax.legend(by_label.values(), by_label.keys(), loc="upper right")

        apply_plot_theme(self.fig, self.ax, mode="dark")
        self.canvas.draw()

    def on_click(self, event):
        c = self.controller
        if event.inaxes == self.ax and event.button == 1:
            if c.data is not None:
                import numpy as np
                idx = np.argmin(np.abs(c.x_data - event.xdata))
                x_val = c.x_data[idx]
                y_val = c.y_data[idx]
                c.add_manual_peak(x_val, y_val)
                self.plot_data()

    def start_manual_selection(self):
        from tkinter import messagebox
        messagebox.showinfo("Selección manual",
                            "Haga clic en el gráfico para seleccionar picos. "
                            "Use zoom para mayor precisión.")

    def highlight_point(self, x_val, y_val, color=None):
        self.ax.plot(x_val, y_val, "o", markersize=12, markerfacecolor="none",
                     markeredgecolor=color or PALETTE["warning"], markeredgewidth=3)
        self.canvas.draw()
