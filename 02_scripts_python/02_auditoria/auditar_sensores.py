
from pathlib import Path
import xml.etree.ElementTree as ET

carpeta = Path(__file__).resolve().parents[2]
archivo = carpeta / "01_simulacion_sumo/configuracion/adicionales.add.xml"

if not archivo.exists():
    print("ERROR: No se encontro adicionales.add.xml")
    raise SystemExit

raiz = ET.parse(archivo).getroot()

# Vias que contabilizamos anteriormente con TraCI
accesos = {
    "jp_sube_sur": "Javier Prado subida",
    "jp_baja_norte_1": "Javier Prado bajada",
    "avi_izq_in": "Aviacion izquierda",
    "avi_der_in": "Aviacion derecha",
    "salida_tunel_teatro": "Tunel norte",
    "entrada_tunel_bnp": "Tunel BNP"
}

detectores = [
    elemento
    for elemento in raiz.iter()
    if elemento.tag in (
        "laneAreaDetector",
        "multiLaneAreaDetector"
    )
]

print("\nAUDITORIA DE SENSORES E2")
print("=" * 60)
print("Sensores E2 encontrados:", len(detectores))

for detector in detectores:
    identificador = detector.get("id", "")
    carriles = detector.get("lanes")

    if carriles is None:
        carriles = detector.get("lane", "")

    print("\nSensor:", identificador)
    print("Carril(es):", carriles)
    print("Posicion:", detector.get("pos", "No indicada"))
    print("Longitud:", detector.get("length", "No indicada"))
    print("Frecuencia:", detector.get("freq", "No indicada"))

    for carril in carriles.split():
        # En SUMO, el identificador del carril
        # termina normalmente en _0, _1, etc.
        via = carril.rsplit("_", 1)[0]

        print("  Via:", via)

        if via in accesos:
            print("  Acceso TraCI:", accesos[via])
            print("  Coincidencia directa: SI")
        else:
            print("  Coincidencia directa: NO")
            print("  Requiere revisar la ruta")

print("\nAUDITORIA FINALIZADA")
