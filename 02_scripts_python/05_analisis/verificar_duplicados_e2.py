
from pathlib import Path

import traci
from sumolib import checkBinary

carpeta_proyecto = Path(__file__).resolve().parents[2]

config = (
    carpeta_proyecto
    / "01_simulacion_sumo"
    / "configuracion"
    / "simulacion.sumocfg"
)

parejas = {
    "Aviacion izquierda": (
        "e2_avi_izq_0",
        "e2_avi_izq_1"
    ),
    "Aviacion derecha": (
        "e2_avi_der_0",
        "e2_avi_der_1"
    )
}

vistos = {
    sensor: set()
    for par in parejas.values()
    for sensor in par
}

carpeta_pruebas = (
    carpeta_proyecto
    / "04_resultados"
    / "pruebas"
)

carpeta_pruebas.mkdir(parents=True, exist_ok=True)

prefijo_salida = "../../04_resultados/pruebas/verificacion_e2_"

comando = [
    checkBinary("sumo"),
    "-c", str(config),
    "--output-prefix", prefijo_salida,
    "--no-step-log", "true"
]

try:
    traci.start(comando)

    while traci.simulation.getTime() < 3600:
        traci.simulationStep()

        for sensor in vistos:
            vehiculos = (
                traci.lanearea.getLastStepVehicleIDs(
                    sensor
                )
            )

            vistos[sensor].update(vehiculos)

finally:
    if traci.isLoaded():
        traci.close()

print("\nVERIFICACION DE DUPLICADOS E2")
print("=" * 55)

for nombre, (sensor_a, sensor_b) in parejas.items():

    a = vistos[sensor_a]
    b = vistos[sensor_b]

    repetidos = a & b
    unicos = a | b

    print(f"\nAcceso: {nombre}")
    print(f"Sensor 0: {len(a)}")
    print(f"Sensor 1: {len(b)}")
    print(f"Suma individual: {len(a) + len(b)}")
    print(f"Vehiculos en ambos: {len(repetidos)}")
    print(f"Vehiculos distintos: {len(unicos)}")

print("\nVERIFICACION FINALIZADA")
