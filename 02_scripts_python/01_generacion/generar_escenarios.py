
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
    / "escenarios_basicos"
)
carpeta.mkdir(parents=True, exist_ok=True)
escenarios = {
    "baja": 0.65,
    "media": 1.00,
    "alta": 1.40
}

if not original.exists():
    raise FileNotFoundError(
        "No se encontro trafico_prueba.rou.xml"
    )

print("\nGENERACION DE ESCENARIOS")
print("=" * 55)

for nombre, factor in escenarios.items():

    arbol = ET.parse(original)
    raiz = arbol.getroot()

    total_base = 0
    total_nuevo = 0
    cantidad_flujos = 0

    for flujo in raiz.findall("flow"):

        tasa = flujo.get("vehsPerHour")

        if tasa is None:
            raise ValueError(
                "Flujo sin vehsPerHour: "
                + str(flujo.get("id"))
            )

        tasa_original = float(tasa)
        tasa_nueva = tasa_original * factor

        flujo.set(
            "vehsPerHour",
            f"{tasa_nueva:.3f}"
        )

        total_base += tasa_original
        total_nuevo += tasa_nueva
        cantidad_flujos += 1

    salida = carpeta / f"trafico_{nombre}.rou.xml"

    arbol.write(
        salida,
        encoding="utf-8",
        xml_declaration=True
    )

    print(f"\nEscenario: {nombre}")
    print(f"Factor: {factor}")
    print(f"Flujos modificados: {cantidad_flujos}")
    print(f"Tasa base total: {total_base:.1f} veh/h")
    print(f"Tasa nueva total: {total_nuevo:.1f} veh/h")
    print(f"Archivo: {salida.name}")

print("\nESCENARIOS GENERADOS")
