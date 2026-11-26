
from pathlib import Path
import xml.etree.ElementTree as ET

carpeta = Path(__file__).resolve().parents[2]
archivo = carpeta / "01_simulacion_sumo/red_vial/jp_aviacion.net.xml"

raiz = ET.parse(archivo).getroot()

print("\nAUDITORIA DE CONFLICTOS - SUMO")
print("=" * 60)

for semaforo_id in ["J_IZQ", "J_DER"]:

    nodo = raiz.find(f".//junction[@id='{semaforo_id}']")

    print(f"\nINTERSECCION: {semaforo_id}")

    if nodo is None:
        print("No se encontro la interseccion.")
        continue

    solicitudes = nodo.findall("request")

    print("Movimientos en matriz:", len(solicitudes))

    for solicitud in solicitudes:

        indice = solicitud.get("index")
        foes = solicitud.get("foes", "")
        response = solicitud.get("response", "")

        # Los bits se leen de derecha a izquierda.
        conflictos = [
            i for i, valor in enumerate(reversed(foes))
            if valor == "1"
        ]

        prioridades = [
            i for i, valor in enumerate(reversed(response))
            if valor == "1"
        ]

        print(f"\nMovimiento interno {indice}")
        print("  Conflictos:", conflictos)
        print("  Debe ceder ante:", prioridades)

    if not solicitudes:
        print("No se encontraron matrices de conflictos.")

print("\nAUDITORIA FINALIZADA")
