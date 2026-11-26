
from pathlib import Path
from collections import defaultdict
import csv
import xml.etree.ElementTree as ET

import traci
from sumolib import checkBinary

carpeta = Path(__file__).resolve().parents[2]
config = carpeta / "01_simulacion_sumo" / "configuracion" / "simulacion.sumocfg"
carpeta_escenarios = carpeta / "01_simulacion_sumo" / "escenarios"

carpeta_originales = carpeta / "04_resultados" / "01_simulaciones_originales"

carpeta_repeticiones = carpeta / "04_resultados" / "02_repeticiones"

carpeta_pruebas = carpeta / "04_resultados" / "pruebas" 

salida = carpeta / "03_datos" / "02_procesados" / "conteos_24_ejecuciones_PRUEBA.csv"
escenarios = [
    "baja", "media", "alta",
    "punta_jp", "punta_avi",
    "punta_tuneles",
    "asimetrico_1", "asimetrico_2"
]

semillas = [42, 43, 44]

zonas = {
    "jp_sube": [
        "e2_jp_sube_bus", "e2_jp_sube_priv"
    ],
    "jp_baja": [
        "e2_jp_baja_bus", "e2_jp_baja_priv"
    ],
    "tunel_norte": [
        "e2_tunel_norte_0"
    ],
    "avi_izq": [
        "e2_avi_izq_0", "e2_avi_izq_1"
    ],
    "avi_der": [
        "e2_avi_der_0", "e2_avi_der_1"
    ],
    "rampa_bnp": [
        "e2_rampa_0"
    ]
}

tipos = [
    "auto", "camioneta", "moto",
    "corredor", "bus_aviacion"
]

duracion = 3600
intervalo = 300

filas = []
ejecuciones_validadas = 0

def leer_mediciones(archivo):
    datos = {}

    for _, elemento in ET.iterparse(
        archivo, events=("end",)
    ):
        if elemento.tag != "interval":
            continue

        clave = (
            elemento.get("id"),
            elemento.get("begin"),
            elemento.get("end")
        )

        datos[clave] = (
            elemento.get("nVehEntered"),
            elemento.get("meanSpeed"),
            elemento.get("meanOccupancy"),
            elemento.get("maxJamLengthInMeters")
        )

        elemento.clear()

    return datos

for escenario in escenarios:
    for semilla in semillas:

        rutas = carpeta_escenarios / f"trafico_{escenario}.rou.xml"

        if semilla == 42:
            referencia = f"{escenario}_"
            carpeta_referencia = carpeta_originales
        else:
            referencia = f"rep_s{semilla}_{escenario}_"
            carpeta_referencia = carpeta_repeticiones

        archivo_referencia = carpeta_referencia/ (
            referencia + "salidas_sensores.xml"
        )

        prefijo = f"extr_s{semilla}_{escenario}_"
        archivo_nuevo = carpeta_pruebas / (
            prefijo + "salidas_sensores.xml"
        )

        if not rutas.exists():
            raise FileNotFoundError(rutas.name)

        if not archivo_referencia.exists():
            raise FileNotFoundError(
                archivo_referencia.name
            )

        vistos = {
            zona: set()
            for zona in zonas
        }

        conteos = defaultdict(int)

        comando = [
            checkBinary("sumo"),
            "-c", str(config),
            "--route-files", str(rutas),
            "--begin", "0",
            "--end", str(duracion),
            "--seed", str(semilla),
            "--output-prefix", f"../../04_resultados/pruebas/{prefijo}",
            "--no-step-log", "true"
        ]

        print(
            f"Procesando {escenario}, semilla {semilla}",
            flush=True
        )

        try:
            traci.start(comando)

            disponibles = set(
                traci.lanearea.getIDList()
            )

            for sensores in zonas.values():
                for sensor in sensores:
                    if sensor not in disponibles:
                        raise ValueError(
                            f"Sensor inexistente: {sensor}"
                        )

            while traci.simulation.getTime() < duracion:

                traci.simulationStep()

                tiempo = traci.simulation.getTime()

                bloque = min(
                    int(
                        max(0, tiempo - 0.000001)
                        // intervalo
                    ),
                    duracion // intervalo - 1
                )

                for zona, sensores in zonas.items():

                    detectados = set()

                    for sensor in sensores:
                        detectados.update(
                            traci.lanearea.getLastStepVehicleIDs(
                                sensor
                            )
                        )

                    nuevos = detectados - vistos[zona]

                    for vehiculo in nuevos:

                        tipo = traci.vehicle.getTypeID(
                            vehiculo
                        )

                        if tipo not in tipos:
                            raise ValueError(
                                f"Tipo inesperado: {tipo}"
                            )

                        conteos[
                            (bloque, zona, tipo)
                        ] += 1

                    vistos[zona].update(nuevos)

        finally:
            if traci.isLoaded():
                traci.close()

        # Comprobar que esta ejecucion coincide
        # con los sensores originales guardados.
        original = leer_mediciones(
            archivo_referencia
        )
        nuevo = leer_mediciones(
            archivo_nuevo
        )

        if len(original) != 120 or original != nuevo:
            raise RuntimeError(
                "Diferencias en sensores: "
                f"{escenario}, semilla {semilla}"
            )

        # Solo aceptar los conteos si la
        # reproduccion fue validada.
        for bloque in range(duracion // intervalo):
            for zona in zonas:
                for tipo in tipos:

                    filas.append({
                        "escenario": escenario,
                        "semilla": semilla,
                        "inicio_s": bloque * intervalo,
                        "fin_s": (bloque + 1) * intervalo,
                        "zona": zona,
                        "tipo_vehiculo": tipo,
                        "cantidad": conteos[
                            (bloque, zona, tipo)
                        ]
                    })

        ejecuciones_validadas += 1

        print("  Validacion E2: OK", flush=True)

# Guardar la base solamente si todas
# las ejecuciones se validaron.
campos = [
    "escenario", "semilla",
    "inicio_s", "fin_s",
    "zona", "tipo_vehiculo", "cantidad"
]

with salida.open(
    "w", newline="", encoding="utf-8-sig"
) as archivo:

    escritor = csv.DictWriter(
        archivo, fieldnames=campos
    )

    escritor.writeheader()
    escritor.writerows(filas)

print("\nEXTRACCION FINALIZADA")
print("=" * 55)
print("Ejecuciones validadas:", ejecuciones_validadas)
print("Registros generados:", len(filas))
print("Archivo:", salida.name)
print(
    "Observaciones por zona:",
    sum(fila["cantidad"] for fila in filas)
)
