

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 21 15:30:32 2025

@author: drosales
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from scipy.signal import find_peaks, peak_widths
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import docx
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
import os

warnings.filterwarnings('ignore')

class PolymerFTIRAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador FTIR para Polímeros Industriales")
        self.root.geometry("1400x800")
        
        # Variables
        self.data = None
        self.x_data = None
        self.y_data = None
        self.peaks = None
        self.selected_peaks = []
        self.polymer_matches = []
        self.functional_group_annotations = []
        self.identified_groups = []
        
        # Variables para comparativa
        self.comparison_data = None
        self.comparison_x = None
        self.comparison_y = None
        self.comparison_peaks = None
        
        # Ventana de gráfico separado
        self.plot_window = None
        self.fig = None
        self.ax = None
        self.canvas = None
        self.toolbar = None
        
        # Base de datos de polímeros
        self.polymer_db = self.create_polymer_database()
        self.functional_groups_db = self.create_functional_groups_database()
        
        # Crear interfaz
        self.create_widgets()
    
    def create_polymer_database(self):
        """Base de datos de polímeros industriales con sus bandas características"""
        polymers = {
            'PET': {
                'name': 'Polietileno Tereftalato (PET)',
                'characteristic_peaks': [
                    {'wavenumber': 1710, 'intensity': 'muy fuerte', 'description': 'C=O ester'},
                    {'wavenumber': 1240, 'intensity': 'fuerte', 'description': 'C-O ester'},
                    {'wavenumber': 1090, 'intensity': 'fuerte', 'description': 'C-O-C'},
                    {'wavenumber': 725, 'intensity': 'media', 'description': 'Anillo aromático'},
                    {'wavenumber': 1410, 'intensity': 'media', 'description': 'Anillo benceno'}
                ],
                'density': 1.38,
                'applications': 'Botellas, fibras, envases'
            },
            'ABS': {
                'name': 'Acrilonitrilo Butadieno Estireno (ABS)',
                'characteristic_peaks': [
                    {'wavenumber': 2237, 'intensity': 'media', 'description': 'C≡N nitrilo'},
                    {'wavenumber': 1600, 'intensity': 'media', 'description': 'C=C aromático'},
                    {'wavenumber': 1493, 'intensity': 'media', 'description': 'C=C aromático'},
                    {'wavenumber': 1450, 'intensity': 'media', 'description': 'CH2 deformación'},
                    {'wavenumber': 966, 'intensity': 'media', 'description': 'C-H trans butadieno'},
                    {'wavenumber': 910, 'intensity': 'media', 'description': 'C-H vinilo'}
                ],
                'density': 1.04,
                'applications': 'Automotriz, electrónica, juguetes'
            },
            'PLA': {
                'name': 'Ácido Poliláctico (PLA)',
                'characteristic_peaks': [
                    {'wavenumber': 1750, 'intensity': 'muy fuerte', 'description': 'C=O ester'},
                    {'wavenumber': 1180, 'intensity': 'fuerte', 'description': 'C-O ester'},
                    {'wavenumber': 1080, 'intensity': 'fuerte', 'description': 'C-O-C'},
                    {'wavenumber': 1450, 'intensity': 'media', 'description': 'CH3 deformación'},
                    {'wavenumber': 1380, 'intensity': 'media', 'description': 'CH3 deformación'}
                ],
                'density': 1.24,
                'applications': 'Impresión 3D, envases biodegradables'
            },
            'PA': {
                'name': 'Poliamida (Nylon)',
                'characteristic_peaks': [
                    {'wavenumber': 3300, 'intensity': 'fuerte', 'description': 'N-H stretch'},
                    {'wavenumber': 1630, 'intensity': 'muy fuerte', 'description': 'C=O amida I'},
                    {'wavenumber': 1540, 'intensity': 'fuerte', 'description': 'N-H amida II'},
                    {'wavenumber': 1270, 'intensity': 'media', 'description': 'C-N amida III'},
                    {'wavenumber': 690, 'intensity': 'media', 'description': 'N-H amida V'}
                ],
                'density': 1.14,
                'applications': 'Textiles, engranajes, fibras'
            },
            'PMMA': {
                'name': 'Polimetilmetacrilato (PMMA - Acrílico)',
                'characteristic_peaks': [
                    {'wavenumber': 1730, 'intensity': 'muy fuerte', 'description': 'C=O ester'},
                    {'wavenumber': 1150, 'intensity': 'fuerte', 'description': 'C-O ester'},
                    {'wavenumber': 1190, 'intensity': 'fuerte', 'description': 'C-O-C'},
                    {'wavenumber': 1485, 'intensity': 'media', 'description': 'CH2 deformación'},
                    {'wavenumber': 1385, 'intensity': 'media', 'description': 'CH3 deformación'}
                ],
                'density': 1.18,
                'applications': 'Lentes, displays, acuarios'
            },
            'PP': {
                'name': 'Polipropileno (PP)',
                'characteristic_peaks': [
                    {'wavenumber': 2950, 'intensity': 'fuerte', 'description': 'CH3 stretch'},
                    {'wavenumber': 2915, 'intensity': 'fuerte', 'description': 'CH2 stretch'},
                    {'wavenumber': 2835, 'intensity': 'fuerte', 'description': 'CH stretch'},
                    {'wavenumber': 1450, 'intensity': 'media', 'description': 'CH3 deformación'},
                    {'wavenumber': 1375, 'intensity': 'media', 'description': 'CH3 deformación'},
                    {'wavenumber': 1165, 'intensity': 'media', 'description': 'C-C stretch'}
                ],
                'density': 0.90,
                'applications': 'Envases, automotriz, textiles'
            },
            'PE': {
                'name': 'Polietileno (PE)',
                'characteristic_peaks': [
                    {'wavenumber': 2915, 'intensity': 'fuerte', 'description': 'CH2 stretch asimétrico'},
                    {'wavenumber': 2848, 'intensity': 'fuerte', 'description': 'CH2 stretch simétrico'},
                    {'wavenumber': 1470, 'intensity': 'media', 'description': 'CH2 deformación'},
                    {'wavenumber': 1460, 'intensity': 'media', 'description': 'CH2 deformación'},
                    {'wavenumber': 730, 'intensity': 'media', 'description': 'CH2 rocking'}
                ],
                'density': 0.92,
                'applications': 'Bolsas, envases, tuberías'
            },
            'HDPE': {
                'name': 'Polietileno Alta Densidad (HDPE)',
                'characteristic_peaks': [
                    {'wavenumber': 2915, 'intensity': 'fuerte', 'description': 'CH2 stretch asimétrico'},
                    {'wavenumber': 2848, 'intensity': 'fuerte', 'description': 'CH2 stretch simétrico'},
                    {'wavenumber': 1470, 'intensity': 'media', 'description': 'CH2 deformación'},
                    {'wavenumber': 1460, 'intensity': 'media', 'description': 'CH2 deformación'},
                    {'wavenumber': 730, 'intensity': 'media', 'description': 'CH2 rocking'},
                    {'wavenumber': 720, 'intensity': 'media', 'description': 'CH2 rocking cristalino'}
                ],
                'density': 0.95,
                'applications': 'Tuberías, tanques, juguetes'
            },
            'PS': {
                'name': 'Poliestireno (PS)',
                'characteristic_peaks': [
                    {'wavenumber': 3025, 'intensity': 'media', 'description': 'C-H aromático'},
                    {'wavenumber': 2920, 'intensity': 'media', 'description': 'C-H alifático'},
                    {'wavenumber': 1600, 'intensity': 'fuerte', 'description': 'C=C aromático'},
                    {'wavenumber': 1490, 'intensity': 'fuerte', 'description': 'C=C aromático'},
                    {'wavenumber': 1450, 'intensity': 'media', 'description': 'CH2 deformación'},
                    {'wavenumber': 755, 'intensity': 'fuerte', 'description': 'C-H aromático monosustituido'}
                ],
                'density': 1.05,
                'applications': 'Envases, espumas, juguetes'
            },
            'PVC': {
                'name': 'Policloruro de Vinilo (PVC)',
                'characteristic_peaks': [
                    {'wavenumber': 1250, 'intensity': 'fuerte', 'description': 'CHCl deformación'},
                    {'wavenumber': 1330, 'intensity': 'media', 'description': 'CH2 deformación'},
                    {'wavenumber': 1420, 'intensity': 'media', 'description': 'CH2 deformación'},
                    {'wavenumber': 600, 'intensity': 'fuerte', 'description': 'C-Cl stretch'},
                    {'wavenumber': 700, 'intensity': 'fuerte', 'description': 'C-Cl stretch'}
                ],
                'density': 1.38,
                'applications': 'Tuberías, cables, recubrimientos'
            },
       
        'TPO_CaCO3': {
                'name': 'TPO (PP + Carga CaCO3)',
                'characteristic_peaks': [
                    {'wavenumber': 2950, 'intensity': 'fuerte', 'description': 'CH3 (PP)'},
                    {'wavenumber': 2915, 'intensity': 'fuerte', 'description': 'CH2 (PP)'},
                    {'wavenumber': 2835, 'intensity': 'fuerte', 'description': 'CH (PP)'},
                    {'wavenumber': 1450, 'intensity': 'media', 'description': 'CH3 bend (PP)'},
                    {'wavenumber': 1375, 'intensity': 'media', 'description': 'CH3 bend (PP)'},
                    # Picos del Aditivo
                    {'wavenumber': 1415, 'intensity': 'muy fuerte', 'description': 'C-O (CaCO3)'},
                    {'wavenumber': 874, 'intensity': 'fuerte', 'description': 'C-O (CaCO3)'},
                    {'wavenumber': 712, 'intensity': 'media', 'description': 'C-O (CaCO3)'}
                ],
                'density': 1.1, # Más denso que el PP puro (0.90)
                'applications': 'Ruedas, parachoques, perfiles'
            },
        'TPU_ETHER': {
                'name': 'Poliuretano Termoplástico (TPU) - Tipo Éter',
                'characteristic_peaks': [
                    {'wavenumber': 3300, 'intensity': 'fuerte', 'description': 'N-H stretch (uretano)'},
                    {'wavenumber': 2915, 'intensity': 'media', 'description': 'C-H stretch'},
                    {'wavenumber': 1640, 'intensity': 'fuerte', 'description': 'C=O Amida I (uretano)'},
                    {'wavenumber': 1540, 'intensity': 'media', 'description': 'N-H Amida II (uretano)'},
                    {'wavenumber': 1100, 'intensity': 'muy fuerte', 'description': 'C-O-C stretch (poliéter)'},
                    # El pico 1017 es también una variante del C-O-C de poliéter
                    {'wavenumber': 1020, 'intensity': 'muy fuerte', 'description': 'C-O-C stretch (poliéter)'}
                ],
                'density': 1.12,
                'applications': 'Ruedas, suelas de calzado, sellos, mangueras'
            },
        
        'PEVA': {
           'name': 'Polietileno-co-acetato de vinilo (PEVA)',
           'characteristic_peaks': [
               {'wavenumber': 2920, 'intensity': 'fuerte', 'description': 'CH2 stretch asimétrico'},
               {'wavenumber': 2850, 'intensity': 'fuerte', 'description': 'CH2 stretch simétrico'},
               {'wavenumber': 1735, 'intensity': 'muy fuerte', 'description': 'C=O estiramiento (acetato)'},
               {'wavenumber': 1465, 'intensity': 'media', 'description': 'CH2 deformación'},
               {'wavenumber': 1370, 'intensity': 'media', 'description': 'CH3 deformación (acetato)'},
               {'wavenumber': 1240, 'intensity': 'fuerte', 'description': 'C-O estiramiento (acetato)'},
               {'wavenumber': 1020, 'intensity': 'fuerte', 'description': 'C-O-C estiramiento'},
               {'wavenumber': 720, 'intensity': 'media', 'description': 'CH2 rocking'}
           ],
           'density': 0.94,  # típico entre 0.93-0.95
           'applications': 'Películas flexibles, envases, calzado, juguetes'
       },
       'NEOPRENE': {
           'name': 'Policloropreno (Neopreno)',
           'characteristic_peaks': [
               {'wavenumber': 2915, 'intensity': 'fuerte', 'description': 'CH2 stretch asimétrico'},
               {'wavenumber': 2848, 'intensity': 'fuerte', 'description': 'CH2 stretch simétrico'},
               {'wavenumber': 1600, 'intensity': 'media', 'description': 'C=C estiramiento'},
               {'wavenumber': 1450, 'intensity': 'media', 'description': 'CH2 deformación'},
               {'wavenumber': 1380, 'intensity': 'media', 'description': 'CH3 deformación'},
               {'wavenumber': 820, 'intensity': 'fuerte', 'description': 'C-Cl estiramiento (trans)'},
               {'wavenumber': 750, 'intensity': 'media', 'description': 'C-Cl estiramiento (gauche)'}
           ],
           'density': 1.23,
           'applications': 'Trajes de neopreno, juntas, mangueras, adhesivos'
       }
        
        }
        
        
        return polymers
    
    def create_functional_groups_database(self):
        """Base de datos de grupos funcionales para polímeros"""
        groups = [
            # Carbonilos
            {'range_min': 1680, 'range_max': 1750, 'intensity': 'fuerte', 
             'group': 'C=O (ésteres, carbonilos)', 'bond': 'C=O stretch', 'color': 'red'},
            {'range_min': 1630, 'range_max': 1680, 'intensity': 'fuerte', 
             'group': 'C=O (amidas)', 'bond': 'C=O stretch', 'color': 'darkred'},
            
            # Nitrilos
            {'range_min': 2200, 'range_max': 2260, 'intensity': 'media', 
             'group': 'C≡N (nitrilo)', 'bond': 'C≡N stretch', 'color': 'purple'},
            
            # Aromáticos
            {'range_min': 3000, 'range_max': 3100, 'intensity': 'media', 
             'group': 'C-H aromático', 'bond': 'C-H stretch', 'color': 'orange'},
            {'range_min': 1450, 'range_max': 1600, 'intensity': 'fuerte', 
             'group': 'C=C aromático', 'bond': 'C=C stretch', 'color': 'darkorange'},
            
            # Alifáticos
            {'range_min': 2800, 'range_max': 3000, 'intensity': 'fuerte', 
             'group': 'C-H alifático', 'bond': 'C-H stretch', 'color': 'blue'},
            {'range_min': 1350, 'range_max': 1480, 'intensity': 'media', 
             'group': 'CH2/CH3 deformación', 'bond': 'C-H bend', 'color': 'lightblue'},
            
            # Éteres y Esteres
            {'range_min': 1000, 'range_max': 1300, 'intensity': 'fuerte', 
             'group': 'C-O (éteres, ésteres)', 'bond': 'C-O stretch', 'color': 'green'},
            
            # Amidas
            {'range_min': 3200, 'range_max': 3500, 'intensity': 'media', 
             'group': 'N-H (amidas)', 'bond': 'N-H stretch', 'color': 'brown'},
            
            # Halogenuros
            {'range_min': 600, 'range_max': 800, 'intensity': 'fuerte', 
             'group': 'C-Cl (PVC)', 'bond': 'C-Cl stretch', 'color': 'cyan'}
        ]
        return pd.DataFrame(groups)
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame de controles
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Botones
        ttk.Button(control_frame, text="Cargar Espectro", 
                  command=self.load_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Abrir Gráfico", 
                  command=self.open_plot_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Detectar Picos Automáticos", 
                  command=self.auto_detect_peaks).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Identificar Polímero", 
                  command=self.identify_polymer_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Mostrar Grupos Funcionales", 
                  command=self.show_functional_groups).pack(side=tk.LEFT, padx=5)
        
        # Nuevos botones para comparativa
        ttk.Button(control_frame, text="Cargar Comparación", 
                  command=self.load_comparison_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Ejecutar Comparativa", 
                  command=self.run_comparison).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Limpiar Comparación", 
                  command=self.clear_comparison).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Limpiar Análisis", 
                  command=self.clear_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Exportar Reporte", 
                  command=self.export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Exportar Reporte Word",
                  command=self.export_word_report).pack(side=tk.LEFT, padx=5)
        
        # Frame de parámetros
        param_frame = ttk.LabelFrame(main_frame, text="Parámetros de Análisis", padding="5")
        param_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=5, padx=5)
        
        # Umbral de detección
        ttk.Label(param_frame, text="Umbral detección:").grid(row=0, column=0, sticky=tk.W)
        self.threshold_var = tk.DoubleVar(value=0.1)
        ttk.Scale(param_frame, from_=0.01, to=0.5, variable=self.threshold_var,
                 orient=tk.HORIZONTAL, length=150).grid(row=0, column=1, padx=5)
        ttk.Label(param_frame, textvariable=self.threshold_var).grid(row=0, column=2)
        
        # Distancia entre picos
        ttk.Label(param_frame, text="Distancia mínima:").grid(row=1, column=0, sticky=tk.W)
        self.distance_var = tk.IntVar(value=15)
        ttk.Spinbox(param_frame, from_=5, to=50, textvariable=self.distance_var,
                   width=5).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Tolerancia identificación
        ttk.Label(param_frame, text="Tolerancia (cm⁻¹):").grid(row=2, column=0, sticky=tk.W)
        self.tolerance_var = tk.IntVar(value=15)
        ttk.Spinbox(param_frame, from_=5, to=30, textvariable=self.tolerance_var,
                   width=5).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Frame de picos detectados
        peaks_frame = ttk.LabelFrame(main_frame, text="Picos Detectados", padding="5")
        peaks_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        # Lista de picos
        peak_list_frame = ttk.Frame(peaks_frame)
        peak_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.peak_listbox = tk.Listbox(peak_list_frame, height=8, width=50)
        scrollbar = ttk.Scrollbar(peak_list_frame, orient=tk.VERTICAL, command=self.peak_listbox.yview)
        self.peak_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.peak_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de identificación de polímeros
        polymer_frame = ttk.LabelFrame(main_frame, text="Identificación de Polímeros", padding="5")
        polymer_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        # Treeview para resultados de polímeros
        columns = ('polymer', 'score', 'confidence', 'density', 'applications')
        self.polymer_tree = ttk.Treeview(polymer_frame, columns=columns, height=8)
        
        self.polymer_tree.heading('polymer', text='Polímero')
        self.polymer_tree.heading('score', text='Score')
        self.polymer_tree.heading('confidence', text='Confianza')
        self.polymer_tree.heading('density', text='Densidad')
        self.polymer_tree.heading('applications', text='Aplicaciones')
        
        self.polymer_tree.column('polymer', width=200)
        self.polymer_tree.column('score', width=80)
        self.polymer_tree.column('confidence', width=100)
        self.polymer_tree.column('density', width=80)
        self.polymer_tree.column('applications', width=200)
        
        scrollbar_polymer = ttk.Scrollbar(polymer_frame, orient=tk.VERTICAL, command=self.polymer_tree.yview)
        self.polymer_tree.configure(yscrollcommand=scrollbar_polymer.set)
        
        self.polymer_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_polymer.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de grupos funcionales
        groups_frame = ttk.LabelFrame(main_frame, text="Grupos Funcionales Identificados", padding="5")
        groups_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        # Treeview para grupos funcionales
        group_columns = ('wavenumber', 'group', 'bond', 'color')
        self.group_tree = ttk.Treeview(groups_frame, columns=group_columns, height=6)
        
        self.group_tree.heading('wavenumber', text='N° Onda (cm⁻¹)')
        self.group_tree.heading('group', text='Grupo Funcional')
        self.group_tree.heading('bond', text='Tipo de Vibración')
        self.group_tree.heading('color', text='Color')
        
        self.group_tree.column('wavenumber', width=100)
        self.group_tree.column('group', width=200)
        self.group_tree.column('bond', width=150)
        self.group_tree.column('color', width=80)
        
        scrollbar_group = ttk.Scrollbar(groups_frame, orient=tk.VERTICAL, command=self.group_tree.yview)
        self.group_tree.configure(yscrollcommand=scrollbar_group.set)
        
        self.group_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_group.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de detalles del polímero
        detail_frame = ttk.LabelFrame(main_frame, text="Detalles del Polímero Seleccionado", padding="5")
        detail_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        # Text widget para detalles
        self.detail_text = tk.Text(detail_frame, height=8, width=100)
        scrollbar_detail = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=scrollbar_detail.set)
        
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_detail.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar pesos de grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        
        # Conectar eventos
        self.peak_listbox.bind('<<ListboxSelect>>', self.on_peak_select)
        self.polymer_tree.bind('<<TreeviewSelect>>', self.on_polymer_select)
        self.group_tree.bind('<<TreeviewSelect>>', self.on_group_select)
        
    def open_plot_window(self):
        """Abre una ventana separada para el gráfico"""
        if self.data is None:
            messagebox.showwarning("Advertencia", "Primero cargue un espectro")
            return
        
        if self.plot_window is None or not self.plot_window.winfo_exists():
            self.plot_window = tk.Toplevel(self.root)
            self.plot_window.title("Gráfico FTIR - Espectro Completo")
            self.plot_window.geometry("1200x700")
            self.plot_window.protocol("WM_DELETE_WINDOW", self.on_plot_window_close)
            
            # Frame principal del gráfico
            plot_frame = ttk.Frame(self.plot_window)
            plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Crear figura de matplotlib
            self.fig = Figure(figsize=(12, 6), dpi=100)
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
            
            # Barra de herramientas
            self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
            self.toolbar.update()
            
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Botones adicionales en la ventana de gráfico
            button_frame = ttk.Frame(plot_frame)
            button_frame.pack(fill=tk.X, pady=5)
            
            ttk.Button(button_frame, text="Seleccionar Pico Manual", 
                      command=self.start_manual_selection).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Actualizar Gráfico", 
                      command=self.plot_data).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cerrar", 
                      command=self.on_plot_window_close).pack(side=tk.RIGHT, padx=5)
            
            # Conectar eventos del gráfico
            self.canvas.mpl_connect('button_press_event', self.on_click)
            
            # Dibujar el gráfico inicial
            self.plot_data()
        
        else:
            self.plot_window.lift()
            self.plot_window.focus_force()
    
    def on_plot_window_close(self):
        """Maneja el cierre de la ventana de gráfico"""
        if self.plot_window:
            self.plot_window.destroy()
            self.plot_window = None
            self.fig = None
            self.ax = None
            self.canvas = None
            self.toolbar = None
    
    def plot_data(self):
        """Dibuja los datos en el gráfico"""
        if self.data is None or self.ax is None:
            return
            
        self.ax.clear()
        
        # Plotear espectro principal
        self.ax.plot(self.x_data, self.y_data, 'b-', linewidth=1, alpha=0.8, label='Espectro Principal')
        
        # Plotear espectro de comparación si existe
        if self.comparison_data is not None:
            self.ax.plot(self.comparison_x, self.comparison_y, 'r-', linewidth=1, alpha=0.7, label='Espectro Comparación')
            
            # Plotear picos de comparación
            if self.comparison_peaks is not None:
                self.ax.plot(self.comparison_x[self.comparison_peaks], 
                           self.comparison_y[self.comparison_peaks], 
                           'rs', markersize=6, label='Picos Comparación', alpha=0.7)
        
        self.ax.set_xlabel('Número de onda (cm⁻¹)')
        self.ax.set_ylabel('Absorbancia (normalizada)')
        self.ax.set_title('Espectro FTIR - Análisis de Polímeros')
        self.ax.grid(True, alpha=0.3)
        self.ax.invert_xaxis()
        
        # Plotear picos detectados del espectro principal
        if self.peaks is not None:
            self.ax.plot(self.x_data[self.peaks], self.y_data[self.peaks], 
                        'ro', markersize=6, label='Picos detectados', alpha=0.7)
            
            # Anotar números de onda
            for peak_idx in self.peaks:
                x_val = self.x_data[peak_idx]
                y_val = self.y_data[peak_idx]
                self.ax.annotate(f'{x_val:.0f}', (x_val, y_val), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.7)
        
        # Plotear picos seleccionados manualmente
        if self.selected_peaks:
            for peak_x, peak_y in self.selected_peaks:
                self.ax.plot(peak_x, peak_y, 'go', markersize=8, 
                           markerfacecolor='none', markeredgewidth=2, 
                           label='Pico manual')
                self.ax.annotate(f'{peak_x:.0f}', (peak_x, peak_y), 
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=8, alpha=0.7)
        
        # Mostrar grupos funcionales si están activos
        if self.functional_group_annotations:
            for annotation in self.functional_group_annotations:
                x_val = annotation['x']
                y_val = annotation['y']
                group = annotation['group']
                color = annotation['color']
                
                self.ax.plot(x_val, y_val, 's', markersize=8, color=color,
                           label=group if group not in [a.get_label() for a in self.ax.get_legend_handles_labels()[0]] else "")
                
                # Anotar grupo funcional
                self.ax.annotate(group, (x_val, y_val),
                               xytext=(10, 10), textcoords='offset points',
                               fontsize=8, color=color, weight='bold',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        # Leyenda
        handles, labels = self.ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        if by_label:
            self.ax.legend(by_label.values(), by_label.keys(), loc='upper right')
            
        self.canvas.draw()
    
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar espectro FTIR",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Leer datos
                data = np.loadtxt(file_path, delimiter=',')
                self.x_data = data[:, 0]
                self.y_data = data[:, 1]
                self.data = data
                
                # Normalizar datos
                self.y_data = (self.y_data - np.min(self.y_data)) / (np.max(self.y_data) - np.min(self.y_data))
                
                # Si la ventana de gráfico está abierta, actualizarla
                if self.plot_window and self.plot_window.winfo_exists():
                    self.plot_data()
                
                messagebox.showinfo("Éxito", "Archivo cargado correctamente. Use 'Abrir Gráfico' para visualizar.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")
    
    def identify_functional_groups(self, wavenumber):
        """Identifica grupos funcionales para un número de onda específico"""
        matches = []
        for _, group in self.functional_groups_db.iterrows():
            if group['range_min'] <= wavenumber <= group['range_max']:
                range_center = (group['range_min'] + group['range_max']) / 2
                distance = abs(wavenumber - range_center)
                range_width = group['range_max'] - group['range_min']
                score = 1 - (distance / range_width)
                
                matches.append({
                    'group': group['group'],
                    'bond': group['bond'],
                    'color': group['color'],
                    'score': score,
                    'wavenumber': wavenumber
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches
    
    def identify_polymer(self, detected_peaks):
        """Identifica el polímero basado en los picos detectados"""
        polymer_scores = {}
        
        for polymer_code, polymer_data in self.polymer_db.items():
            score = 0
            matched_peaks = []
            
            for expected_peak in polymer_data['characteristic_peaks']:
                expected_wavenumber = expected_peak['wavenumber']
                
                # Buscar pico más cercano
                closest_peak = None
                min_distance = float('inf')
                
                for detected_peak in detected_peaks:
                    distance = abs(detected_peak['wavenumber'] - expected_wavenumber)
                    if distance < min_distance and distance < 20:
                        min_distance = distance
                        closest_peak = detected_peak
                
                if closest_peak:
                    peak_score = 1 - (min_distance / 20)
                    if expected_peak['intensity'] in ['muy fuerte', 'fuerte']:
                        peak_score *= 1.5
                    
                    score += peak_score
                    matched_peaks.append({
                        'expected': expected_peak,
                        'detected': closest_peak,
                        'distance': min_distance,
                        'score': peak_score
                    })
            
            polymer_scores[polymer_code] = {
                'score': score,
                'matched_peaks': matched_peaks,
                'total_expected': len(polymer_data['characteristic_peaks'])
            }
        
        # Ordenar por score
        sorted_polymers = sorted(polymer_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        return sorted_polymers
    
    def show_functional_groups(self):
        """Muestra los grupos funcionales en la gráfica y en la lista"""
        if (self.peaks is None or len(self.peaks) == 0) and len(self.selected_peaks) == 0:
            messagebox.showwarning("Advertencia", "No hay picos para analizar grupos funcionales")
            return
        
        self.functional_group_annotations = []
        self.identified_groups = []
        
        # Analizar picos automáticos
        if self.peaks is not None:
            for peak_idx in self.peaks:
                x_val = self.x_data[peak_idx]
                y_val = self.y_data[peak_idx]
                
                # Identificar grupo funcional
                matches = self.identify_functional_groups(x_val)
                if matches:
                    best_match = matches[0]
                    self.functional_group_annotations.append({
                        'x': x_val,
                        'y': y_val,
                        'group': best_match['group'],
                        'bond': best_match['bond'],
                        'color': best_match['color']
                    })
                    self.identified_groups.append({
                        'wavenumber': x_val,
                        'group': best_match['group'],
                        'bond': best_match['bond'],
                        'color': best_match['color']
                    })
        
        # Analizar picos manuales
        for x_val, y_val in self.selected_peaks:
            matches = self.identify_functional_groups(x_val)
            if matches:
                best_match = matches[0]
                self.functional_group_annotations.append({
                    'x': x_val,
                    'y': y_val,
                    'group': best_match['group'],
                    'bond': best_match['bond'],
                    'color': best_match['color']
                })
                self.identified_groups.append({
                    'wavenumber': x_val,
                    'group': best_match['group'],
                    'bond': best_match['bond'],
                    'color': best_match['color']
                })
        
        # Actualizar lista de grupos funcionales
        self.update_group_list()
        
        # Actualizar gráfico si está abierto
        if self.plot_window and self.plot_window.winfo_exists():
            self.plot_data()
        
        messagebox.showinfo("Grupos Funcionales", 
                          f"Se identificaron {len(self.functional_group_annotations)} grupos funcionales")
    
    def update_group_list(self):
        """Actualiza la lista de grupos funcionales identificados"""
        for item in self.group_tree.get_children():
            self.group_tree.delete(item)
        
        for group_info in self.identified_groups:
            self.group_tree.insert('', 'end', values=(
                f"{group_info['wavenumber']:.1f}",
                group_info['group'],
                group_info['bond'],
                group_info['color']
            ))
    
    def auto_detect_peaks(self):
        if self.data is None:
            messagebox.showwarning("Advertencia", "Primero cargue un espectro")
            return
            
        try:
            threshold = self.threshold_var.get()
            distance = self.distance_var.get()
            
            # Encontrar picos
            self.peaks, properties = find_peaks(
                self.y_data, 
                height=threshold,
                distance=distance,
                prominence=0.05,
                width=2
            )
            
            # Actualizar lista
            self.update_peak_list()
            
            # Actualizar gráfico si está abierto
            if self.plot_window and self.plot_window.winfo_exists():
                self.plot_data()
            
            messagebox.showinfo("Éxito", f"Se detectaron {len(self.peaks)} picos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en detección de picos: {str(e)}")
    
    def update_peak_list(self):
        self.peak_listbox.delete(0, tk.END)
        
        # Agregar picos automáticos
        if self.peaks is not None:
            for i, peak_idx in enumerate(self.peaks):
                x_val = self.x_data[peak_idx]
                y_val = self.y_data[peak_idx]
                self.peak_listbox.insert(tk.END, f"{x_val:.1f} cm⁻¹ - {y_val:.3f}")
        
        # Agregar picos manuales
        for i, (x_val, y_val) in enumerate(self.selected_peaks):
            self.peak_listbox.insert(tk.END, f"{x_val:.1f} cm⁻¹ - {y_val:.3f} (manual)")
    
    def identify_polymer_analysis(self):
        """Análisis completo de identificación de polímero"""
        if (self.peaks is None or len(self.peaks) == 0) and len(self.selected_peaks) == 0:
            messagebox.showwarning("Advertencia", "No hay picos para analizar")
            return
        
        # Preparar picos detectados
        detected_peaks = []
        
        if self.peaks is not None:
            for peak_idx in self.peaks:
                detected_peaks.append({
                    'wavenumber': self.x_data[peak_idx],
                    'intensity': self.y_data[peak_idx]
                })
        
        for x_val, y_val in self.selected_peaks:
            detected_peaks.append({
                'wavenumber': x_val,
                'intensity': y_val
            })
        
        # Identificar polímero
        self.polymer_matches = self.identify_polymer(detected_peaks)
        
        # Actualizar treeview
        for item in self.polymer_tree.get_children():
            self.polymer_tree.delete(item)
        
        for polymer_code, match_data in self.polymer_matches:
            polymer_info = self.polymer_db[polymer_code]
            score = match_data['score']
            total_expected = match_data['total_expected']
            confidence = f"{(score / total_expected) * 100:.1f}%"
            
            self.polymer_tree.insert('', 'end', values=(
                polymer_info['name'],
                f"{score:.2f}",
                confidence,
                polymer_info['density'],
                polymer_info['applications']
            ))
        
        messagebox.showinfo("Análisis completado", 
                          f"Se analizaron {len(detected_peaks)} picos. "
                          f"Revise los resultados de identificación.")
    
    def on_polymer_select(self, event):
        """Cuando se selecciona un polímero en el treeview"""
        selection = self.polymer_tree.selection()
        if selection and self.polymer_matches:
            item = selection[0]
            polymer_code = self.polymer_matches[self.polymer_tree.index(item)][0]
            polymer_info = self.polymer_db[polymer_code]
            match_data = self.polymer_matches[self.polymer_tree.index(item)][1]
            
            # Mostrar detalles
            detail_text = f"POLÍMERO: {polymer_info['name']}\n"
            detail_text += f"Densidad: {polymer_info['density']} g/cm³\n"
            detail_text += f"Aplicaciones: {polymer_info['applications']}\n\n"
            detail_text += "BANDAS CARACTERÍSTICAS:\n"
            detail_text += "-" * 50 + "\n"
            
            for i, peak_match in enumerate(match_data['matched_peaks']):
                detail_text += (f"{i+1}. {peak_match['expected']['wavenumber']} cm⁻¹ "
                              f"({peak_match['expected']['intensity']}) - "
                              f"Detectado: {peak_match['detected']['wavenumber']:.1f} cm⁻¹ "
                              f"(Δ: {peak_match['distance']:.1f} cm⁻¹)\n")
                detail_text += f"   Descripción: {peak_match['expected']['description']}\n\n"
            
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, detail_text)
            
            # Resaltar picos en gráfico si está abierto
            if self.plot_window and self.plot_window.winfo_exists():
                self.plot_data()
                for peak_match in match_data['matched_peaks']:
                    self.ax.plot(peak_match['detected']['wavenumber'], 
                               peak_match['detected']['intensity'],
                               'yo', markersize=10, markerfacecolor='none', 
                               markeredgewidth=2, label='Pico característico')
                self.canvas.draw()
    
    def on_group_select(self, event):
        """Cuando se selecciona un grupo funcional en la lista"""
        selection = self.group_tree.selection()
        if selection:
            item = selection[0]
            values = self.group_tree.item(item)['values']
            wavenumber = float(values[0])
            
            # Resaltar el grupo seleccionado en el gráfico si está abierto
            if self.plot_window and self.plot_window.winfo_exists():
                self.plot_data()
                self.ax.plot(wavenumber, 0.5, 's', markersize=12, color=values[3],
                           markerfacecolor='none', markeredgewidth=3, label='Grupo seleccionado')
                self.canvas.draw()
    
    def on_click(self, event):
        if event.inaxes == self.ax and event.button == 1:
            if self.data is not None:
                idx = np.argmin(np.abs(self.x_data - event.xdata))
                x_val = self.x_data[idx]
                y_val = self.y_data[idx]
                
                self.selected_peaks.append((x_val, y_val))
                self.update_peak_list()
                if self.plot_window and self.plot_window.winfo_exists():
                    self.plot_data()
    
    def on_peak_select(self, event):
        """Cuando se selecciona un pico en la lista"""
        selection = self.peak_listbox.curselection()
        if selection:
            if self.plot_window and self.plot_window.winfo_exists():
                self.plot_data()
                index = selection[0]
                
                if self.peaks is not None and index < len(self.peaks):
                    x_val = self.x_data[self.peaks[index]]
                    y_val = self.y_data[self.peaks[index]]
                else:
                    manual_index = index - (len(self.peaks) if self.peaks is not None else 0)
                    x_val, y_val = self.selected_peaks[manual_index]
                
                self.ax.plot(x_val, y_val, 'yo', markersize=12, 
                           markerfacecolor='none', markeredgewidth=3)
                self.canvas.draw()
    
    def start_manual_selection(self):
        if self.data is None:
            messagebox.showwarning("Advertencia", "Primero cargue un espectro")
            return
            
        if not self.plot_window or not self.plot_window.winfo_exists():
            messagebox.showwarning("Advertencia", "Primero abra la ventana de gráfico")
            return
            
        messagebox.showinfo("Selección manual", 
                          "Haga clic en el gráfico para seleccionar picos. "
                          "Use zoom para mayor precisión.")
    
    def export_word_report(self):
        if not self.polymer_matches and not self.identified_groups:
            messagebox.showwarning("Advertencia", "No hay análisis para exportar en Word")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")])
        
        if not file_path:
            return
            
        try:
            doc = docx.Document()
            doc.add_heading('REPORTE DE ANÁLISIS FTIR', 0)

            # 1. Gráfico
            if self.data is not None:
                # Crea y guarda la imagen del gráfico
                fig, ax = plt.subplots(figsize=(8, 4.5))
                ax.plot(self.x_data, self.y_data, 'b-', linewidth=1, alpha=0.8)
                if self.peaks is not None:
                    ax.plot(self.x_data[self.peaks], self.y_data[self.peaks], 'ro', markersize=6, label='Picos detectados', alpha=0.7)
                
                ax.set_xlabel('Número de onda (cm⁻¹)')
                ax.set_ylabel('Absorbancia (normalizada)')
                ax.set_title('Espectro FTIR')
                ax.grid(True, alpha=0.3)
                ax.invert_xaxis()
                
                # Anotar el polímero de mayor confianza
                if self.polymer_matches:
                    best_match_code = self.polymer_matches[0][0]
                    best_match_info = self.polymer_db[best_match_code]
                    best_match_data = self.polymer_matches[0][1]
                    confidence = (best_match_data['score'] / best_match_data['total_expected']) * 100
                    doc.add_heading(f"Polímero de Mayor Confianza: {best_match_info['name']} ({confidence:.1f}%)", 1)
                    
                    # Resaltar picos del polímero en el gráfico
                    for peak_match in best_match_data['matched_peaks']:
                        ax.plot(peak_match['detected']['wavenumber'], 
                                peak_match['detected']['intensity'],
                                'go', markersize=10, markerfacecolor='none', 
                                markeredgewidth=2)
                
                plt.savefig('ftir_spectrum.png')
                doc.add_picture('ftir_spectrum.png', width=Inches(6.0))
                os.remove('ftir_spectrum.png')
                plt.close(fig)
                doc.add_page_break()
                doc.add_heading('DETALLES DEL ANÁLISIS', 1)

            # 2. Sensibilidad de identificación de picos
            doc.add_paragraph(f"Sensibilidad de detección de picos:")
            doc.add_paragraph(f" - Umbral de altura: {self.threshold_var.get()}")
            doc.add_paragraph(f" - Distancia mínima entre picos: {self.distance_var.get()} cm⁻¹")
            doc.add_paragraph(f" - Tolerancia de identificación: {self.tolerance_var.get()} cm⁻¹")

            doc.add_paragraph()

            # 3. Picos identificados
            doc.add_heading('Picos Detectados', 2)
            if self.peaks is not None or self.selected_peaks:
                table = doc.add_table(rows=1, cols=3)
                hdr_cells = table.rows[0].cells
                hdr_cells[0].text = 'N° de Onda (cm⁻¹)'
                hdr_cells[1].text = 'Absorbancia (Normalizada)'
                hdr_cells[2].text = 'Tipo'
                
                if self.peaks is not None:
                    for peak_idx in self.peaks:
                        cells = table.add_row().cells
                        cells[0].text = f"{self.x_data[peak_idx]:.1f}"
                        cells[1].text = f"{self.y_data[peak_idx]:.3f}"
                        cells[2].text = "Automático"
                
                if self.selected_peaks:
                    for x_val, y_val in self.selected_peaks:
                        cells = table.add_row().cells
                        cells[0].text = f"{x_val:.1f}"
                        cells[1].text = f"{y_val:.3f}"
                        cells[2].text = "Manual"
            else:
                doc.add_paragraph("No se detectaron picos.")

            doc.add_paragraph()

            # 4. Grupos funcionales identificados
            doc.add_heading('Grupos Funcionales Identificados', 2)
            if self.identified_groups:
                table = doc.add_table(rows=1, cols=3)
                hdr_cells = table.rows[0].cells
                hdr_cells[0].text = 'N° de Onda (cm⁻¹)'
                hdr_cells[1].text = 'Grupo Funcional'
                hdr_cells[2].text = 'Vibración'
                
                for group_info in self.identified_groups:
                    cells = table.add_row().cells
                    cells[0].text = f"{group_info['wavenumber']:.1f}"
                    cells[1].text = group_info['group']
                    cells[2].text = group_info['bond']
            else:
                doc.add_paragraph("No se identificaron grupos funcionales.")
            
            doc.add_paragraph()

            # 5. Polímero de mayor grado de confianza
            doc.add_heading('Resultados de Identificación de Polímeros', 2)
            if self.polymer_matches:
                best_match_code = self.polymer_matches[0][0]
                best_match_info = self.polymer_db[best_match_code]
                best_match_data = self.polymer_matches[0][1]
                confidence = (best_match_data['score'] / best_match_data['total_expected']) * 100
                
                doc.add_paragraph(f"El polímero con mayor grado de confianza es: {best_match_info['name']}")
                doc.add_paragraph(f"Confianza: {confidence:.1f}%")
                doc.add_paragraph(f"Densidad: {best_match_info['density']} g/cm³")
                doc.add_paragraph(f"Aplicaciones: {best_match_info['applications']}")
                
                doc.add_paragraph()
                doc.add_heading('Bandas Características Detectadas', 3)
                for peak_match in best_match_data['matched_peaks']:
                    p = doc.add_paragraph()
                    p.add_run(f"N° Onda Esperado: {peak_match['expected']['wavenumber']} cm⁻¹\n").bold = True
                    p.add_run(f"N° Onda Detectado: {peak_match['detected']['wavenumber']:.1f} cm⁻¹\n")
                    p.add_run(f"Descripción: {peak_match['expected']['description']}\n")
                    p.add_run(f"Delta: {peak_match['distance']:.1f} cm⁻¹\n\n")

            doc.save(file_path)
            messagebox.showinfo("Éxito", "Reporte de Word exportado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar a Word: {str(e)}")
    
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
        self.detail_text.delete(1.0, tk.END)
        if self.plot_window and self.plot_window.winfo_exists():
            self.plot_data()
    
    def export_report(self):
        if not self.polymer_matches and not self.identified_groups:
            messagebox.showwarning("Advertencia", "No hay análisis para exportar")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("REPORTE DE ANÁLISIS FTIR - IDENTIFICACIÓN DE POLÍMEROS\n")
                    f.write("=" * 70 + "\n\n")
                    
                    # Resultados de identificación de polímeros
                    if self.polymer_matches:
                        f.write("RESULTADOS DE IDENTIFICACIÓN:\n")
                        f.write("-" * 40 + "\n")
                        
                        for i, (polymer_code, match_data) in enumerate(self.polymer_matches):
                            polymer_info = self.polymer_db[polymer_code]
                            confidence = (match_data['score'] / match_data['total_expected']) * 100
                            
                            f.write(f"{i+1}. {polymer_info['name']}\n")
                            f.write(f"   Score: {match_data['score']:.2f} / {match_data['total_expected']}\n")
                            f.write(f"   Confianza: {confidence:.1f}%\n")
                            f.write(f"   Densidad: {polymer_info['density']} g/cm³\n")
                            f.write(f"   Aplicaciones: {polymer_info['applications']}\n\n")
                    
                    # Grupos funcionales identificados
                    if self.identified_groups:
                        f.write("\nGRUPOS FUNCIONALES IDENTIFICADOS:\n")
                        f.write("-" * 40 + "\n")
                        
                        for i, group_info in enumerate(self.identified_groups):
                            f.write(f"{i+1}: {group_info['wavenumber']:.1f} cm⁻¹ - {group_info['group']}\n")
                            f.write(f"   Vibración: {group_info['bond']}\n\n")
                    
                    # Picos detectados
                    f.write("\nPICOS DETECTADOS:\n")
                    f.write("-" * 30 + "\n")
                    
                    if self.peaks is not None:
                        for i, peak_idx in enumerate(self.peaks):
                            x_val = self.x_data[peak_idx]
                            y_val = self.y_data[peak_idx]
                            f.write(f"{i+1}: {x_val:.1f} cm⁻¹ - {y_val:.3f}\n")
                    
                    if self.selected_peaks:
                        for i, (x_val, y_val) in enumerate(self.selected_peaks):
                            f.write(f"{i+1}: {x_val:.1f} cm⁻¹ - {y_val:.3f} (manual)\n")
                
                messagebox.showinfo("Éxito", "Reporte exportado correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    # ===== NUEVOS MÉTODOS PARA COMPARATIVA ENTRE ESPECTROS =====
    
    def load_comparison_file(self):
        """Cargar archivo CSV para comparación"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar espectro FTIR para comparación",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Leer datos de comparación
                data = np.loadtxt(file_path, delimiter=',')
                self.comparison_x = data[:, 0]
                self.comparison_y = data[:, 1]
                self.comparison_data = data
                
                # Normalizar datos
                self.comparison_y = (self.comparison_y - np.min(self.comparison_y)) / (np.max(self.comparison_y) - np.min(self.comparison_y))
                
                # Detectar picos automáticamente
                threshold = self.threshold_var.get()
                distance = self.distance_var.get()
                self.comparison_peaks, _ = find_peaks(
                    self.comparison_y, 
                    height=threshold,
                    distance=distance,
                    prominence=0.05,
                    width=2
                )
                
                messagebox.showinfo("Éxito", f"Espectro de comparación cargado. Se detectaron {len(self.comparison_peaks)} picos.")
                if self.plot_window and self.plot_window.winfo_exists():
                    self.plot_data()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo de comparación: {str(e)}")

    def run_comparison(self):
        """Ejecutar comparativa entre los dos espectros"""
        if self.data is None or self.comparison_data is None:
            messagebox.showwarning("Advertencia", "Debe cargar ambos espectros (principal y comparación)")
            return
        
        try:
            # Calcular similitud de coseno
            # Interpolar ambos espectros a la misma escala
            common_x = np.linspace(max(self.x_data.min(), self.comparison_x.min()),
                                 min(self.x_data.max(), self.comparison_x.max()), 1000)
            
            y1_interp = np.interp(common_x, self.x_data, self.y_data)
            y2_interp = np.interp(common_x, self.comparison_x, self.comparison_y)
            
            # Calcular similitud de coseno
            similarity = cosine_similarity([y1_interp], [y2_interp])[0][0]
            
            # Comparar picos principales
            main_peaks = []
            if self.peaks is not None:
                for peak_idx in self.peaks:
                    main_peaks.append({
                        'wavenumber': self.x_data[peak_idx],
                        'intensity': self.y_data[peak_idx]
                    })
            
            comp_peaks = []
            if self.comparison_peaks is not None:
                for peak_idx in self.comparison_peaks:
                    comp_peaks.append({
                        'wavenumber': self.comparison_x[peak_idx],
                        'intensity': self.comparison_y[peak_idx]
                    })
            
            # Encontrar picos comunes
            common_peaks = []
            tolerance = self.tolerance_var.get()
            
            for main_peak in main_peaks:
                for comp_peak in comp_peaks:
                    if abs(main_peak['wavenumber'] - comp_peak['wavenumber']) <= tolerance:
                        common_peaks.append({
                            'wavenumber': main_peak['wavenumber'],
                            'main_intensity': main_peak['intensity'],
                            'comp_intensity': comp_peak['intensity'],
                            'difference': abs(main_peak['intensity'] - comp_peak['intensity'])
                        })
                        break
            
            # Calcular diferencia promedio de intensidades
            avg_intensity_diff = np.mean([peak['difference'] for peak in common_peaks]) if common_peaks else 0
            
            # Mostrar resultados
            result_text = f"RESULTADOS DE COMPARATIVA\n"
            result_text += "=" * 40 + "\n"
            result_text += f"Similitud de coseno: {similarity:.4f}\n"
            result_text += f"Picos en espectro principal: {len(main_peaks)}\n"
            result_text += f"Picos en espectro comparación: {len(comp_peaks)}\n"
            result_text += f"Picos comunes: {len(common_peaks)}\n"
            result_text += f"Diferencia promedio de intensidad: {avg_intensity_diff:.4f}\n\n"
            
            if common_peaks:
                result_text += "PICOS COMUNES:\n"
                result_text += "-" * 30 + "\n"
                for i, peak in enumerate(common_peaks[:10]):  # Mostrar solo los primeros 10
                    result_text += f"{i+1}. {peak['wavenumber']:.1f} cm⁻¹ "
                    result_text += f"(ΔInt: {peak['difference']:.3f})\n"
            
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, result_text)
            
            # Actualizar gráfico para mostrar ambos espectros
            if self.plot_window and self.plot_window.winfo_exists():
                self.plot_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en comparativa: {str(e)}")

    def clear_comparison(self):
        """Limpiar datos de comparación"""
        self.comparison_data = None
        self.comparison_x = None
        self.comparison_y = None
        self.comparison_peaks = None
        if self.plot_window and self.plot_window.winfo_exists():
            self.plot_data()
        messagebox.showinfo("Éxito", "Datos de comparación limpiados")

def main():
    root = tk.Tk()
    app = PolymerFTIRAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()