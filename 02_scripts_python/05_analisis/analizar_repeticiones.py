
from pathlib import Path
import csv
import statistics as stats
import xml.etree.ElementTree as ET

carpeta_proyecto = Path(__file__).resolve().parents[2]

carpeta_originales = (
    carpeta_proyecto
    / "04_resultados"
    / "01_simulaciones_originales"
)

carpeta_repeticiones = (
    carpeta_proyecto
    / "04_resultados"
    / "02_repeticiones"
)

carpeta = (
    carpeta_proyecto
    / "04_resultados"
    / "pruebas"
)

carpeta.mkdir(parents=True, exist_ok=True)

escenarios = [
    "baja", "media", "alta",
    "punta_jp", "punta_avi",
    "punta_tuneles",
    "asimetrico_1", "asimetrico_2"
]

semillas = [42, 43, 44]

resultados = []

def promedio(valores):
    return stats.mean(valores) if valores else None

for escenario in escenarios:
    for semilla in semillas:

        if semilla == 42:
            prefijo = f"{escenario}_"
            carpeta_entrada = carpeta_originales
        else:
            prefijo = f"rep_s{semilla}_{escenario}_"
            carpeta_entrada = carpeta_repeticiones

        archivo_viajes = carpeta_entrada / (
            f"{prefijo}tripinfo.xml"
        )
        archivo_resumen = carpeta_entrada / (
            f"{prefijo}resumen.xml"
        )

        if not archivo_viajes.exists():
            raise FileNotFoundError(archivo_viajes)

        if not archivo_resumen.exists():
            raise FileNotFoundError(archivo_resumen)

        viajes = ET.parse(
            archivo_viajes
        ).getroot().findall("tripinfo")

        esperas = [
            float(v.get("waitingTime"))
            for v in viajes
            if v.get("waitingTime") is not None
        ]

        perdidas = [
            float(v.get("timeLoss"))
            for v in viajes
            if v.get("timeLoss") is not None
        ]

        duraciones = [
            float(v.get("duration"))
            for v in viajes
            if v.get("duration") is not None
        ]

        pasos = ET.parse(
            archivo_resumen
        ).getroot().findall("step")

        if not pasos:
            raise ValueError(
                f"Resumen vacio: {archivo_resumen.name}"
            )

        ultimo = pasos[-1]

        circulando = int(
            ultimo.get("running", "0")
        )
        esperando = int(
            ultimo.get("waiting", "0")
        )

        resultados.append({
            "escenario": escenario,
            "semilla": semilla,
            "viajes_completados": len(viajes),
            "espera_media_s": promedio(esperas),
            "tiempo_perdido_medio_s": promedio(perdidas),
            "duracion_media_s": promedio(duraciones),
            "pendientes": circulando + esperando
        })

# Guardar cada una de las 24 ejecuciones
archivo_detalle = carpeta / "resultados_24_ejecuciones_PRUEBA.csv"

campos = [
    "escenario", "semilla", "viajes_completados",
    "espera_media_s", "tiempo_perdido_medio_s",
    "duracion_media_s", "pendientes"
]

with archivo_detalle.open(
    "w", newline="", encoding="utf-8-sig"
) as f:
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultados)

# Resumen agrupado por escenario
resumen = []

for escenario in escenarios:

    filas = [
        r for r in resultados
        if r["escenario"] == escenario
    ]

    esperas = [
        r["espera_media_s"] for r in filas
        if r["espera_media_s"] is not None
    ]

    perdidas = [
        r["tiempo_perdido_medio_s"] for r in filas
        if r["tiempo_perdido_medio_s"] is not None
    ]

    pendientes = [r["pendientes"] for r in filas]

    resumen.append({
        "escenario": escenario,
        "espera_promedio_s": round(stats.mean(esperas), 2),
        "desviacion_espera_s": round(
            stats.stdev(esperas), 2
        ),
        "perdida_promedio_s": round(
            stats.mean(perdidas), 2
        ),
        "pendientes_promedio": round(
            stats.mean(pendientes), 2
        )
    })

archivo_resumen = carpeta / "resumen_8_escenarios_PRUEBA.csv"

with archivo_resumen.open(
    "w", newline="", encoding="utf-8-sig"
) as f:
    escritor = csv.DictWriter(
        f, fieldnames=resumen[0].keys()
    )
    escritor.writeheader()
    escritor.writerows(resumen)

print("\nANALISIS DE 24 EJECUCIONES")
print("=" * 65)

for fila in resumen:
    print(f'\nEscenario: {fila["escenario"]}')
    print(
        "Espera promedio:",
        fila["espera_promedio_s"], "s"
    )
    print(
        "Desviacion de espera:",
        fila["desviacion_espera_s"], "s"
    )
    print(
        "Tiempo perdido promedio:",
        fila["perdida_promedio_s"], "s"
    )
    print(
        "Pendientes promedio:",
        fila["pendientes_promedio"]
    )

print("\nARCHIVOS GENERADOS:")
print(archivo_detalle.name)
print(archivo_resumen.name)
print("Ejecuciones analizadas:", len(resultados))
print("\nANALISIS FINALIZADO")
