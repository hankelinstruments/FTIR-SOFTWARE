"""Lógica de análisis pura (sin tkinter/matplotlib): detección de picos,
identificación de polímeros, grupos funcionales y comparación de espectros.

Puerto 1:1 de la lógica de la versión original de un solo archivo — sin cambios
de comportamiento, solo separación de responsabilidades.
"""
import numpy as np
from scipy.signal import find_peaks
from sklearn.metrics.pairwise import cosine_similarity


def detect_peaks(y_data, threshold, distance):
    """Envoltorio de scipy.signal.find_peaks con los mismos parámetros que la versión original."""
    peaks, properties = find_peaks(
        y_data,
        height=threshold,
        distance=distance,
        prominence=0.05,
        width=2,
    )
    return peaks, properties


def identify_functional_groups(wavenumber, functional_groups_db):
    """Identifica grupos funcionales para un número de onda específico."""
    matches = []
    for _, group in functional_groups_db.iterrows():
        if group["range_min"] <= wavenumber <= group["range_max"]:
            range_center = (group["range_min"] + group["range_max"]) / 2
            distance = abs(wavenumber - range_center)
            range_width = group["range_max"] - group["range_min"]
            score = 1 - (distance / range_width)

            matches.append({
                "group": group["group"],
                "bond": group["bond"],
                "color": group["color"],
                "score": score,
                "wavenumber": wavenumber,
            })

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches


def identify_polymer(detected_peaks, polymer_db):
    """Identifica el polímero basado en los picos detectados."""
    polymer_scores = {}

    for polymer_code, polymer_data in polymer_db.items():
        score = 0
        matched_peaks = []

        for expected_peak in polymer_data["characteristic_peaks"]:
            expected_wavenumber = expected_peak["wavenumber"]

            closest_peak = None
            min_distance = float("inf")

            for detected_peak in detected_peaks:
                distance = abs(detected_peak["wavenumber"] - expected_wavenumber)
                if distance < min_distance and distance < 20:
                    min_distance = distance
                    closest_peak = detected_peak

            if closest_peak:
                peak_score = 1 - (min_distance / 20)
                if expected_peak["intensity"] in ["muy fuerte", "fuerte"]:
                    peak_score *= 1.5

                score += peak_score
                matched_peaks.append({
                    "expected": expected_peak,
                    "detected": closest_peak,
                    "distance": min_distance,
                    "score": peak_score,
                })

        polymer_scores[polymer_code] = {
            "score": score,
            "matched_peaks": matched_peaks,
            "total_expected": len(polymer_data["characteristic_peaks"]),
        }

    sorted_polymers = sorted(polymer_scores.items(), key=lambda x: x[1]["score"], reverse=True)
    return sorted_polymers


def compare_spectra(x1, y1, x2, y2, tolerance):
    """Compara dos espectros: similitud de coseno + picos comunes dentro de la tolerancia."""
    common_x = np.linspace(max(x1.min(), x2.min()), min(x1.max(), x2.max()), 1000)

    y1_interp = np.interp(common_x, x1, y1)
    y2_interp = np.interp(common_x, x2, y2)

    similarity = cosine_similarity([y1_interp], [y2_interp])[0][0]

    return similarity


def find_common_peaks(main_peaks, comp_peaks, tolerance):
    """main_peaks/comp_peaks: listas de {'wavenumber', 'intensity'}."""
    common_peaks = []
    for main_peak in main_peaks:
        for comp_peak in comp_peaks:
            if abs(main_peak["wavenumber"] - comp_peak["wavenumber"]) <= tolerance:
                common_peaks.append({
                    "wavenumber": main_peak["wavenumber"],
                    "main_intensity": main_peak["intensity"],
                    "comp_intensity": comp_peak["intensity"],
                    "difference": abs(main_peak["intensity"] - comp_peak["intensity"]),
                })
                break
    return common_peaks
