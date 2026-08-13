"""Tema visual sobrio de la app: apariencia CustomTkinter, reskin de ttk.Treeview/Spinbox
y estilo de matplotlib (modo oscuro en vivo, modo claro para reportes impresos)."""
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from app.config import PALETTE


def apply_ctk_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def configure_treeview_style() -> ttk.Style:
    """Reskin oscuro de ttk.Treeview/Spinbox/Scrollbar (CTk no tiene equivalentes nativos)."""
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=PALETTE["bg_surface_alt"],
        fieldbackground=PALETTE["bg_surface_alt"],
        foreground=PALETTE["text_primary"],
        bordercolor=PALETTE["border"],
        borderwidth=0,
        rowheight=24,
    )
    style.map(
        "Treeview",
        background=[("selected", PALETTE["accent"])],
        foreground=[("selected", PALETTE["text_primary"])],
    )
    style.configure(
        "Treeview.Heading",
        background=PALETTE["bg_surface"],
        foreground=PALETTE["text_primary"],
        bordercolor=PALETTE["border"],
        relief="flat",
    )
    style.map(
        "Treeview.Heading",
        background=[("active", PALETTE["accent_hover"])],
    )

    style.configure(
        "TSpinbox",
        fieldbackground=PALETTE["bg_surface_alt"],
        background=PALETTE["bg_surface"],
        foreground=PALETTE["text_primary"],
        arrowcolor=PALETTE["text_primary"],
        bordercolor=PALETTE["border"],
    )

    style.configure(
        "Vertical.TScrollbar",
        background=PALETTE["bg_surface"],
        troughcolor=PALETTE["bg_primary"],
        bordercolor=PALETTE["border"],
        arrowcolor=PALETTE["text_primary"],
    )
    style.configure(
        "Horizontal.TScrollbar",
        background=PALETTE["bg_surface"],
        troughcolor=PALETTE["bg_primary"],
        bordercolor=PALETTE["border"],
        arrowcolor=PALETTE["text_primary"],
    )

    return style


def style_listbox(listbox: tk.Listbox):
    listbox.configure(
        bg=PALETTE["bg_surface_alt"],
        fg=PALETTE["text_primary"],
        selectbackground=PALETTE["accent"],
        selectforeground=PALETTE["text_primary"],
        highlightthickness=1,
        highlightbackground=PALETTE["border"],
        highlightcolor=PALETTE["accent"],
        borderwidth=0,
    )


def apply_plot_theme(fig, ax, mode="dark"):
    """Centraliza el estilo de los gráficos matplotlib. mode='dark' para la ventana
    en vivo, mode='light' para el gráfico embebido en el reporte Word (imprimible)."""
    if mode == "dark":
        fig.patch.set_facecolor(PALETTE["bg_primary"])
        ax.set_facecolor(PALETTE["bg_surface_alt"])
        text_color = PALETTE["text_primary"]
        grid_color = PALETTE["border"]
        legend_face = PALETTE["bg_surface"]
        legend_edge = PALETTE["border"]
    else:
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        text_color = "#1a1a1a"
        grid_color = "#cccccc"
        legend_face = "white"
        legend_edge = "#cccccc"

    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(text_color)
    ax.tick_params(colors=text_color, which="both")
    for spine in ax.spines.values():
        spine.set_color(grid_color)
    ax.grid(True, alpha=0.3, color=grid_color)

    legend = ax.get_legend()
    if legend is not None:
        legend.get_frame().set_facecolor(legend_face)
        legend.get_frame().set_edgecolor(legend_edge)
        for text in legend.get_texts():
            text.set_color(text_color)
