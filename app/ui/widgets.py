"""Widgets compuestos reutilizables: LabeledFrame (reemplazo de ttk.LabelFrame) y HeaderBar."""
import customtkinter as ctk
from PIL import Image

from app.config import APP_ORG, PALETTE, get_assets_path


class LabeledFrame(ctk.CTkFrame):
    """CTkFrame con un título en negrita y una línea separadora, a modo de ttk.LabelFrame."""

    def __init__(self, master, text, **kwargs):
        kwargs.setdefault("fg_color", PALETTE["bg_surface"])
        kwargs.setdefault("corner_radius", 8)
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self, text=text, font=ctk.CTkFont(size=13, weight="bold"),
            text_color=PALETTE["text_primary"], anchor="w",
        )
        title.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

        separator = ctk.CTkFrame(self, height=1, fg_color=PALETTE["border"])
        separator.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))


class HeaderBar(ctk.CTkFrame):
    """Franja superior con logo IIS + título de la app y una línea de acento inferior."""

    def __init__(self, master, subtitle, height=72, **kwargs):
        kwargs.setdefault("fg_color", PALETTE["bg_primary"])
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("height", height)
        super().__init__(master, **kwargs)
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        logo_path = get_assets_path("logo_iis.png")
        self._logo_image = None
        if logo_path.exists():
            pil_img = Image.open(logo_path)
            w, h = pil_img.size
            target_h = height - 24
            target_w = int(w * (target_h / h))
            self._logo_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img,
                                             size=(target_w, target_h))
            logo_label = ctk.CTkLabel(self, image=self._logo_image, text="")
            logo_label.grid(row=0, column=0, padx=(16, 12), pady=12, sticky="w")

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=1, sticky="w", pady=12)

        ctk.CTkLabel(
            text_frame, text=APP_ORG, font=ctk.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["text_primary"], anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_frame, text=subtitle, font=ctk.CTkFont(size=12),
            text_color=PALETTE["text_secondary"], anchor="w",
        ).pack(anchor="w")

        accent_strip = ctk.CTkFrame(master, height=2, fg_color=PALETTE["accent"], corner_radius=0)
        self._accent_strip = accent_strip

    def grid(self, **kwargs):
        super().grid(**kwargs)
        row = kwargs.get("row", 0)
        column = kwargs.get("column", 0)
        columnspan = kwargs.get("columnspan", 1)
        sticky = kwargs.get("sticky", "ew")
        self._accent_strip.grid(row=row + 1, column=column, columnspan=columnspan, sticky=sticky)
