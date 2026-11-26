
from pathlib import Path
import csv
import xml.etree.ElementTree as ET

carpeta_proyecto = Path(__file__).resolve().parents[2]

carpeta = (
    carpeta_proyecto
    / "04_resultados"
    / "01_simulaciones_originales"
)

carpeta_pruebas = (
    carpeta_proyecto
    / "04_resultados"
    / "pruebas"
)

carpeta_pruebas.mkdir(parents=True, exist_ok=True)

escenarios = [
    "baja",
    "media",
    "alta",
    "punta_jp",
    "punta_avi",
    "punta_tuneles",
    "asimetrico_1",
    "asimetrico_2"
]

resultados = []

def promedio(valores):
    return sum(valores) / len(valores) if valores else None

for nombre in escenarios:

    archivo_viajes = carpeta / f"{nombre}_tripinfo.xml"
    archivo_resumen = carpeta / f"{nombre}_resumen.xml"

    if not archivo_viajes.exists():
        raise FileNotFoundError(archivo_viajes.name)

    if not archivo_resumen.exists():
        raise FileNotFoundError(archivo_resumen.name)

    raiz_viajes = ET.parse(archivo_viajes).getroot()
    viajes = raiz_viajes.findall("tripinfo")

    duraciones = []
    esperas = []
    perdidas = []

    for viaje in viajes:
        duraciones.append(float(viaje.get("duration", 0)))
        esperas.append(float(viaje.get("waitingTime", 0)))
        perdidas.append(float(viaje.get("timeLoss", 0)))

    raiz_resumen = ET.parse(archivo_resumen).getroot()
    pasos = raiz_resumen.findall("step")

    if not pasos:
        raise ValueError(
            f"El resumen de {nombre} no contiene pasos"
        )

    ultimo = pasos[-1]

    completados = int(ultimo.get("arrived", 0))
    circulando = int(ultimo.get("running", 0))
    esperando = int(ultimo.get("waiting", 0))

    resultados.append({
        "escenario": nombre,
        "viajes_completados": completados,
        "duracion_media_s": round(promedio(duraciones), 2),
        "espera_media_s": round(promedio(esperas), 2),
        "tiempo_perdido_medio_s": round(promedio(perdidas), 2),
        "circulando_al_final": circulando,
        "esperando_ingresar": esperando,
        "pendientes_total": circulando + esperando
    })

salida = carpeta_pruebas / "comparacion_8_escenarios_PRUEBA.csv"
with salida.open(
    "w", newline="", encoding="utf-8-sig"
) as archivo:

    escritor = csv.DictWriter(
        archivo,
        fieldnames=resultados[0].keys()
    )

    escritor.writeheader()
    escritor.writerows(resultados)

print("\nCOMPARACION DE LOS 8 ESCENARIOS")
print("=" * 75)

for fila in resultados:
    print(f'\nEscenario: {fila["escenario"]}')
    print("Viajes completados:", fila["viajes_completados"])
    print("Duracion media:", fila["duracion_media_s"], "s")
    print("Espera media:", fila["espera_media_s"], "s")
    print(
        "Tiempo perdido medio:",
        fila["tiempo_perdido_medio_s"], "s"
    )
    print("Pendientes al final:", fila["pendientes_total"])

print("\nARCHIVO GENERADO:", salida.name)
print("ESCENARIOS ANALIZADOS:", len(resultados))
print("\nCOMPARACION FINALIZADA")
