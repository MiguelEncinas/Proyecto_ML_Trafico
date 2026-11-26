
import csv
from collections import defaultdict
from pathlib import Path

import traci
from sumolib import checkBinary

carpeta = Path(__file__).resolve().parents[2]
config = carpeta / "01_simulacion_sumo" / "configuracion" / "simulacion.sumocfg"

salida = carpeta /  "03_datos" / "02_procesados" / "conteo_tipos_sensores_PRUEBA.csv"

tipos = [
    "auto",
    "camioneta",
    "moto",
    "corredor",
    "bus_aviacion"
]

intervalo = 300
duracion = 3600

conteos = defaultdict(int)
vistos = defaultdict(set)

comando = [
    checkBinary("sumo"),
    "-c", str(config),
    "--output-prefix", "../../04_resultados/pruebas/conteo_tipos_sensores_",
    "--no-step-log", "true"
]

try:
    traci.start(comando)

    sensores = sorted(traci.lanearea.getIDList())

    print("\nCONTEO VEHICULAR POR SENSOR E2")
    print("=" * 55)
    print("Sensores encontrados:", len(sensores))

    while traci.simulation.getTime() < duracion:
        traci.simulationStep()

        tiempo = traci.simulation.getTime()

        bloque = min(
            int(max(0, tiempo - 0.000001) // intervalo),
            duracion // intervalo - 1
        )

        for sensor in sensores:

            vehiculos = traci.lanearea.getLastStepVehicleIDs(
                sensor
            )

            for vehiculo in vehiculos:

                # Evita contar repetidamente un mismo
                # vehiculo dentro del mismo detector.
                if vehiculo in vistos[sensor]:
                    continue

                vistos[sensor].add(vehiculo)

                tipo = traci.vehicle.getTypeID(vehiculo)

                conteos[(bloque, sensor, tipo)] += 1

finally:
    if traci.isLoaded():
        traci.close()

with salida.open(
    "w",
    newline="",
    encoding="utf-8-sig"
) as archivo:

    escritor = csv.writer(archivo)

    escritor.writerow([
        "inicio_s",
        "fin_s",
        "sensor",
        "tipo_vehiculo",
        "cantidad"
    ])

    for bloque in range(duracion // intervalo):
        for sensor in sensores:
            for tipo in tipos:

                escritor.writerow([
                    bloque * intervalo,
                    (bloque + 1) * intervalo,
                    sensor,
                    tipo,
                    conteos[(bloque, sensor, tipo)]
                ])

print("\nCONTEO COMPLETADO")
print("Archivo:", salida.name)
print("Intervalos:", duracion // intervalo)
print("Tipos vehiculares:", len(tipos))
print("Registros:", 12 * len(sensores) * len(tipos))
print("Detecciones:", sum(conteos.values()))
