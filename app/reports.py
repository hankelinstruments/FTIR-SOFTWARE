"""Exportación de reportes de análisis a texto plano y Word (.docx)."""
import os
import tempfile

import docx
import matplotlib.pyplot as plt
from docx.shared import Inches

from app.ui.theme import apply_plot_theme


def export_text_report(file_path, polymer_matches, polymer_db, identified_groups, peaks, x_data, y_data, selected_peaks):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("REPORTE DE ANÁLISIS FTIR - IDENTIFICACIÓN DE POLÍMEROS\n")
        f.write("=" * 70 + "\n\n")

        if polymer_matches:
            f.write("RESULTADOS DE IDENTIFICACIÓN:\n")
            f.write("-" * 40 + "\n")

            for i, (polymer_code, match_data) in enumerate(polymer_matches):
                polymer_info = polymer_db[polymer_code]
                confidence = (match_data["score"] / match_data["total_expected"]) * 100

                f.write(f"{i+1}. {polymer_info['name']}\n")
                f.write(f"   Score: {match_data['score']:.2f} / {match_data['total_expected']}\n")
                f.write(f"   Confianza: {confidence:.1f}%\n")
                f.write(f"   Densidad: {polymer_info['density']} g/cm³\n")
                f.write(f"   Aplicaciones: {polymer_info['applications']}\n\n")

        if identified_groups:
            f.write("\nGRUPOS FUNCIONALES IDENTIFICADOS:\n")
            f.write("-" * 40 + "\n")

            for i, group_info in enumerate(identified_groups):
                f.write(f"{i+1}: {group_info['wavenumber']:.1f} cm⁻¹ - {group_info['group']}\n")
                f.write(f"   Vibración: {group_info['bond']}\n\n")

        f.write("\nPICOS DETECTADOS:\n")
        f.write("-" * 30 + "\n")

        if peaks is not None:
            for i, peak_idx in enumerate(peaks):
                x_val = x_data[peak_idx]
                y_val = y_data[peak_idx]
                f.write(f"{i+1}: {x_val:.1f} cm⁻¹ - {y_val:.3f}\n")

        if selected_peaks:
            for i, (x_val, y_val) in enumerate(selected_peaks):
                f.write(f"{i+1}: {x_val:.1f} cm⁻¹ - {y_val:.3f} (manual)\n")


def export_word_report(file_path, x_data, y_data, peaks, polymer_matches, polymer_db,
                        identified_groups, selected_peaks, threshold, distance, tolerance):
    doc = docx.Document()
    doc.add_heading("REPORTE DE ANÁLISIS FTIR", 0)

    if x_data is not None:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(x_data, y_data, "-", linewidth=1, alpha=0.9, color="#1f6f8b", label="Espectro")
        if peaks is not None:
            ax.plot(x_data[peaks], y_data[peaks], "o", markersize=6, color="#d9534f",
                    label="Picos detectados", alpha=0.8)

        ax.set_xlabel("Número de onda (cm⁻¹)")
        ax.set_ylabel("Absorbancia (normalizada)")
        ax.set_title("Espectro FTIR")
        ax.invert_xaxis()

        if polymer_matches:
            best_match_code = polymer_matches[0][0]
            best_match_info = polymer_db[best_match_code]
            best_match_data = polymer_matches[0][1]
            confidence = (best_match_data["score"] / best_match_data["total_expected"]) * 100
            doc.add_heading(
                f"Polímero de Mayor Confianza: {best_match_info['name']} ({confidence:.1f}%)", 1
            )

            for peak_match in best_match_data["matched_peaks"]:
                ax.plot(peak_match["detected"]["wavenumber"], peak_match["detected"]["intensity"],
                        "o", markersize=10, markerfacecolor="none", markeredgecolor="#4CAF6D",
                        markeredgewidth=2)

        ax.legend(loc="upper right")
        apply_plot_theme(fig, ax, mode="light")

        tmp_png = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_png.close()
        try:
            plt.savefig(tmp_png.name, facecolor=fig.get_facecolor())
            doc.add_picture(tmp_png.name, width=Inches(6.0))
        finally:
            plt.close(fig)
            os.remove(tmp_png.name)

        doc.add_page_break()
        doc.add_heading("DETALLES DEL ANÁLISIS", 1)

    doc.add_paragraph("Sensibilidad de detección de picos:")
    doc.add_paragraph(f" - Umbral de altura: {threshold}")
    doc.add_paragraph(f" - Distancia mínima entre picos: {distance} cm⁻¹")
    doc.add_paragraph(f" - Tolerancia de identificación: {tolerance} cm⁻¹")
    doc.add_paragraph()

    doc.add_heading("Picos Detectados", 2)
    if peaks is not None or selected_peaks:
        table = doc.add_table(rows=1, cols=3)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "N° de Onda (cm⁻¹)"
        hdr_cells[1].text = "Absorbancia (Normalizada)"
        hdr_cells[2].text = "Tipo"

        if peaks is not None:
            for peak_idx in peaks:
                cells = table.add_row().cells
                cells[0].text = f"{x_data[peak_idx]:.1f}"
                cells[1].text = f"{y_data[peak_idx]:.3f}"
                cells[2].text = "Automático"

        if selected_peaks:
            for x_val, y_val in selected_peaks:
                cells = table.add_row().cells
                cells[0].text = f"{x_val:.1f}"
                cells[1].text = f"{y_val:.3f}"
                cells[2].text = "Manual"
    else:
        doc.add_paragraph("No se detectaron picos.")

    doc.add_paragraph()

    doc.add_heading("Grupos Funcionales Identificados", 2)
    if identified_groups:
        table = doc.add_table(rows=1, cols=3)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "N° de Onda (cm⁻¹)"
        hdr_cells[1].text = "Grupo Funcional"
        hdr_cells[2].text = "Vibración"

        for group_info in identified_groups:
            cells = table.add_row().cells
            cells[0].text = f"{group_info['wavenumber']:.1f}"
            cells[1].text = group_info["group"]
            cells[2].text = group_info["bond"]
    else:
        doc.add_paragraph("No se identificaron grupos funcionales.")

    doc.add_paragraph()

    doc.add_heading("Resultados de Identificación de Polímeros", 2)
    if polymer_matches:
        best_match_code = polymer_matches[0][0]
        best_match_info = polymer_db[best_match_code]
        best_match_data = polymer_matches[0][1]
        confidence = (best_match_data["score"] / best_match_data["total_expected"]) * 100

        doc.add_paragraph(f"El polímero con mayor grado de confianza es: {best_match_info['name']}")
        doc.add_paragraph(f"Confianza: {confidence:.1f}%")
        doc.add_paragraph(f"Densidad: {best_match_info['density']} g/cm³")
        doc.add_paragraph(f"Aplicaciones: {best_match_info['applications']}")

        doc.add_paragraph()
        doc.add_heading("Bandas Características Detectadas", 3)
        for peak_match in best_match_data["matched_peaks"]:
            p = doc.add_paragraph()
            p.add_run(f"N° Onda Esperado: {peak_match['expected']['wavenumber']} cm⁻¹\n").bold = True
            p.add_run(f"N° Onda Detectado: {peak_match['detected']['wavenumber']:.1f} cm⁻¹\n")
            p.add_run(f"Descripción: {peak_match['expected']['description']}\n")
            p.add_run(f"Delta: {peak_match['distance']:.1f} cm⁻¹\n\n")

    doc.save(file_path)
