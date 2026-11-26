
from pathlib import Path
from collections import defaultdict
import csv

import traci
from sumolib import checkBinary

carpeta = Path(__file__).resolve().parents[2]

escenario = "punta_jp"  
semilla = 43
intervalo = 300
duracion = 3600

config = carpeta / "01_simulacion_sumo" / "configuracion" / "simulacion.sumocfg"
rutas = carpeta / "01_simulacion_sumo" / "escenarios" / f"trafico_{escenario}.rou.xml"

salida = carpeta / "03_datos" / "02_procesados" / "prueba_conteos_punta_jp_s43_PRUEBA.csv"

if not config.is_file():
    raise FileNotFoundError(f"Configuracion no encontrada: {config}")

if not rutas.is_file():
    raise FileNotFoundError(f"Escenario no encontrado: {rutas}")
zonas = {
    "jp_sube": [
        "e2_jp_sube_bus",
        "e2_jp_sube_priv"
    ],
    "jp_baja": [
        "e2_jp_baja_bus",
        "e2_jp_baja_priv"
    ],
    "tunel_norte": [
        "e2_tunel_norte_0"
    ],
    "avi_izq": [
        "e2_avi_izq_0",
        "e2_avi_izq_1"
    ],
    "avi_der": [
        "e2_avi_der_0",
        "e2_avi_der_1"
    ],
    "rampa_bnp": [
        "e2_rampa_0"
    ]
}

tipos = [
    "auto",
    "camioneta",
    "moto",
    "corredor",
    "bus_aviacion"
]

vistos = {zona: set() for zona in zonas}
conteos = defaultdict(int)

comando = [
    checkBinary("sumo"),
    "-c", str(config),
    "--route-files", str(rutas),
    "--begin", "0",
    "--end", str(duracion),
    "--seed", str(semilla),
    "--output-prefix", "../../04_resultados/pruebas/probar_conteos_escenario_",
    "--no-step-log", "true"
]

try:
    traci.start(comando)

    disponibles = set(traci.lanearea.getIDList())

    for zona, sensores in zonas.items():
        for sensor in sensores:
            if sensor not in disponibles:
                raise ValueError(
                    f"Sensor no encontrado: {sensor}"
                )

    while traci.simulation.getTime() < duracion:

        traci.simulationStep()
        tiempo = traci.simulation.getTime()

        bloque = min(
            int(max(0, tiempo - 0.000001) // intervalo),
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
                tipo = traci.vehicle.getTypeID(vehiculo)

                if tipo not in tipos:
                    raise ValueError(
                        f"Tipo inesperado: {tipo}"
                    )

                conteos[(bloque, zona, tipo)] += 1

            vistos[zona].update(nuevos)

finally:
    if traci.isLoaded():
        traci.close()

with salida.open(
    "w", newline="", encoding="utf-8-sig"
) as archivo:

    escritor = csv.writer(archivo)

    escritor.writerow([
        "escenario",
        "semilla",
        "inicio_s",
        "fin_s",
        "zona",
        "tipo_vehiculo",
        "cantidad"
    ])

    for bloque in range(duracion // intervalo):
        for zona in zonas:
            for tipo in tipos:

                escritor.writerow([
                    escenario,
                    semilla,
                    bloque * intervalo,
                    (bloque + 1) * intervalo,
                    zona,
                    tipo,
                    conteos[(bloque, zona, tipo)]
                ])

print("\nPRUEBA DE CONTEOS POR ESCENARIO")
print("=" * 55)
print("Escenario:", escenario)
print("Semilla:", semilla)
print("Archivo:", salida.name)
print("Registros:", 12 * len(zonas) * len(tipos))

for zona in zonas:
    print(
        zona + ":",
        sum(
            cantidad
            for (bloque, nombre, tipo), cantidad
            in conteos.items()
            if nombre == zona
        )
    )

print("PRUEBA FINALIZADA")
