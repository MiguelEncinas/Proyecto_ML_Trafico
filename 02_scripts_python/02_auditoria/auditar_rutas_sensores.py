
from pathlib import Path
import xml.etree.ElementTree as ET

carpeta = Path(__file__).resolve().parents[2]

rutas_xml = ET.parse(
    carpeta / "01_simulacion_sumo/escenarios/trafico_prueba.rou.xml"
).getroot()

sensores_xml = ET.parse(
    carpeta / "01_simulacion_sumo/configuracion/adicionales.add.xml"
).getroot()

rutas = {}

for ruta in rutas_xml.findall("route"):
    rutas[ruta.get("id")] = ruta.get(
        "edges", ""
    ).split()

print("\nRUTAS QUE ATRAVIESAN CADA SENSOR")
print("=" * 60)

detectores = [
    elemento
    for elemento in sensores_xml.iter()
    if elemento.tag in (
        "laneAreaDetector",
        "multiLaneAreaDetector"
    )
]

for sensor in detectores:

    identificador = sensor.get("id")

    carriles = sensor.get("lanes")
    if carriles is None:
        carriles = sensor.get("lane", "")

    vias = {
        carril.rsplit("_", 1)[0]
        for carril in carriles.split()
    }

    print(f"\nSENSOR: {identificador}")
    print("Vias:", ", ".join(sorted(vias)))

    encontradas = []

    for ruta_id, tramos in rutas.items():
        if any(via in tramos for via in vias):
            encontradas.append(ruta_id)

    print("Rutas asociadas:", len(encontradas))

    for ruta_id in encontradas:
        print("  -", ruta_id)

print("\nAUDITORIA FINALIZADA")
