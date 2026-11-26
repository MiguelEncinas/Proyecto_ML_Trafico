from pathlib import Path
import xml.etree.ElementTree as ET

carpeta_proyecto = Path(__file__).resolve().parents[2]

carpeta = (
    carpeta_proyecto
    / "04_resultados"
    / "01_simulaciones_originales"
)

escenarios = ["baja", "media", "alta"]

def promedio(valores):
    if not valores:
        return None
    return sum(valores) / len(valores)

def mostrar(numero, unidad=""):
    if numero is None:
        return "No disponible"
    return f"{numero:.2f} {unidad}".strip()

print("\nCOMPARACION DE ESCENARIOS SUMO")
print("=" * 60)

for nombre in escenarios:

    archivo = carpeta / f"{nombre}_tripinfo.xml"

    if not archivo.exists():
        print(f"\nERROR: Falta {archivo.name}")
        continue

    raiz = ET.parse(archivo).getroot()
    viajes = raiz.findall("tripinfo")

    duraciones = []
    esperas = []
    tiempos_perdidos = []

    for viaje in viajes:

        if viaje.get("duration") is not None:
            duraciones.append(
                float(viaje.get("duration"))
            )

        if viaje.get("waitingTime") is not None:
            esperas.append(
                float(viaje.get("waitingTime"))
            )

        if viaje.get("timeLoss") is not None:
            tiempos_perdidos.append(
                float(viaje.get("timeLoss"))
            )

    print(f"\nESCENARIO: {nombre.upper()}")
    print("-" * 40)

    print("Viajes registrados:", len(viajes))
    print(
        "Duracion media:",
        mostrar(promedio(duraciones), "s")
    )
    print(
        "Espera media:",
        mostrar(promedio(esperas), "s")
    )
    print(
        "Tiempo perdido medio:",
        mostrar(promedio(tiempos_perdidos), "s")
    )

    resumen = carpeta / f"{nombre}_resumen.xml"

    if resumen.exists():

        raiz_resumen = ET.parse(resumen).getroot()
        pasos = raiz_resumen.findall("step")

        if pasos:
            ultimo = pasos[-1]

            print(
                "Vehiculos llegados acumulados:",
                ultimo.get("arrived", "No disponible")
            )
            print(
                "Vehiculos circulando al final:",
                ultimo.get("running", "No disponible")
            )
            print(
                "Vehiculos esperando ingresar:",
                ultimo.get("waiting", "No disponible")
            )

print("\nCOMPARACION FINALIZADA")
