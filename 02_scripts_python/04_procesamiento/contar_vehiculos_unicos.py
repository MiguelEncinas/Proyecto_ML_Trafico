
import csv
from pathlib import Path
from collections import defaultdict

import traci
from sumolib import checkBinary

carpeta = Path(__file__).resolve().parents[2]
config = carpeta / "01_simulacion_sumo" / "configuracion" / "simulacion.sumocfg"

salida = carpeta / "03_datos" / "02_procesados" / "conteo_unico_por_zona_PRUEBA.csv"

# Agrupar los sensores de un mismo tramo
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
    "auto", "camioneta", "moto",
    "corredor", "bus_aviacion"
]

intervalo = 300
duracion = 3600

conteos = defaultdict(int)

# Cada vehiculo se cuenta una sola vez por zona
vistos = {
    zona: set()
    for zona in zonas
}

comando = [
    checkBinary("sumo"),
    "-c", str(config),
    "--output-prefix", "../../04_resultados/pruebas/conteo_unico_por_zona_",
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

            # Union de IDs de todos los sensores
            # pertenecientes a la misma zona.
            vehiculos_zona = set()

            for sensor in sensores:
                vehiculos_zona.update(
                    traci.lanearea.getLastStepVehicleIDs(
                        sensor
                    )
                )

            nuevos = vehiculos_zona - vistos[zona]

            for vehiculo in nuevos:
                tipo = traci.vehicle.getTypeID(vehiculo)
                conteos[(bloque, zona, tipo)] += 1

            vistos[zona].update(nuevos)

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
        "inicio_s", "fin_s",
        "zona", "tipo_vehiculo", "cantidad"
    ])

    for bloque in range(duracion // intervalo):
        for zona in zonas:
            for tipo in tipos:
                escritor.writerow([
                    bloque * intervalo,
                    (bloque + 1) * intervalo,
                    zona,
                    tipo,
                    conteos[(bloque, zona, tipo)]
                ])

print("\nCONTEO UNICO POR ZONA COMPLETADO")
print("=" * 55)

for zona in zonas:
    total = sum(
        cantidad
        for (bloque, nombre, tipo), cantidad
        in conteos.items()
        if nombre == zona
    )
    print(f"{zona}: {total}")

print("\nArchivo:", salida.name)
print("Registros:", 12 * len(zonas) * len(tipos))
print("Observaciones por zona:", sum(conteos.values()))
