
from pathlib import Path
import xml.etree.ElementTree as ET

carpeta_proyecto = Path(__file__).resolve().parents[2]

original = (
    carpeta_proyecto
    / "01_simulacion_sumo"
    / "escenarios"
    / "trafico_prueba.rou.xml"
)

carpeta = (
    carpeta_proyecto
    / "01_simulacion_sumo"
    / "pruebas_generacion"
    / "escenarios_variados"
)

carpeta.mkdir(parents=True, exist_ok=True)

# Primer tramo de cada ruta: acceso de origen
accesos = [
    "jp_sube_sur",
    "jp_baja_norte_1",
    "salida_tunel_teatro",
    "avi_izq_in",
    "avi_der_in",
    "entrada_tunel_bnp"
]

# Factores experimentales por acceso
escenarios = {
    "punta_jp": [1.60, 1.60, 1.00, 0.90, 0.90, 1.00],
    "punta_avi": [0.90, 0.90, 1.00, 1.60, 1.60, 1.00],
    "punta_tuneles": [1.00, 1.00, 1.80, 1.00, 1.00, 1.80],
    "punta_combinada": [1.40, 1.40, 1.40, 1.40, 1.40, 1.40],
    "asimetrico_1": [1.70, 0.80, 1.00, 1.00, 1.00, 1.00],
    "asimetrico_2": [1.00, 1.00, 1.00, 1.70, 0.80, 1.00]
}

arbol_base = ET.parse(original)
raiz_base = arbol_base.getroot()

# Asociar cada ruta con su primer tramo
origen_ruta = {}

for ruta in raiz_base.findall("route"):
    tramos = ruta.get("edges", "").split()
    if tramos:
        origen_ruta[ruta.get("id")] = tramos[0]

print("\nGENERACION DE ESCENARIOS VARIADOS")
print("=" * 60)

for nombre, factores in escenarios.items():

    arbol = ET.parse(original)
    raiz = arbol.getroot()

    multiplicadores = dict(zip(accesos, factores))
    total = 0
    modificados = 0

    for flujo in raiz.findall("flow"):

        ruta_id = flujo.get("route")
        origen = origen_ruta.get(ruta_id)

        if origen not in multiplicadores:
            raise ValueError(
                f"Origen no reconocido: {ruta_id}"
            )

        tasa_original = float(
            flujo.get("vehsPerHour")
        )

        tasa_nueva = (
            tasa_original * multiplicadores[origen]
        )

        flujo.set(
            "vehsPerHour",
            f"{tasa_nueva:.3f}"
        )

        total += tasa_nueva
        modificados += 1

    salida = carpeta / f"trafico_{nombre}.rou.xml"

    arbol.write(
        salida,
        encoding="utf-8",
        xml_declaration=True
    )

    print(f"\nEscenario: {nombre}")
    print("Flujos modificados:", modificados)
    print(f"Demanda programada: {total:.1f} veh/h")
    print("Archivo:", salida.name)

print("\nESCENARIOS VARIADOS GENERADOS")
