
import csv
from collections import defaultdict
from pathlib import Path

import traci
from sumolib import checkBinary

carpeta = Path(__file__).resolve().parents[2]
config = carpeta / "01_simulacion_sumo" / "configuracion" / "simulacion.sumocfg"
salida = carpeta / "03_datos" / "02_procesados" / "conteo_por_tipo_PRUEBA.csv"
# Vias de entrada a la red simulada
accesos = {
    "jp_sube_sur": "Javier Prado subida",
    "jp_baja_norte_1": "Javier Prado bajada",
    "avi_izq_in": "Aviacion izquierda",
    "avi_der_in": "Aviacion derecha",
    "salida_tunel_teatro": "Tunel norte",
    "entrada_tunel_bnp": "Tunel BNP"
}

tipos = [
    "auto", "camioneta", "moto",
    "corredor", "bus_aviacion"
]

# Almacenar vehiculos ya registrados por acceso
vistos = {via: set() for via in accesos}
conteos = defaultdict(int)

intervalo = 300
duracion = 3600

comando = [
    checkBinary("sumo"),
    "-c", str(config),
    "--output-prefix", "../../04_resultados/pruebas/conteo_tipos_vehiculos_",
    "--no-step-log", "true"
]

try:
    traci.start(comando)

    while traci.simulation.getTime() < duracion:
        traci.simulationStep()
        tiempo = traci.simulation.getTime()

        for via in accesos:
            vehiculos = traci.edge.getLastStepVehicleIDs(via)

            for vehiculo in vehiculos:
                if vehiculo in vistos[via]:
                    continue

                vistos[via].add(vehiculo)
                tipo = traci.vehicle.getTypeID(vehiculo)

                # Asignar la observacion al intervalo
                bloque = min(
                    int(max(0, tiempo - 0.000001) // intervalo),
                    duracion // intervalo - 1
                )

                conteos[(bloque, via, tipo)] += 1

finally:
    if traci.isLoaded():
        traci.close()

with salida.open(
    "w", newline="", encoding="utf-8-sig"
) as archivo:

    escritor = csv.writer(archivo)
    escritor.writerow([
        "inicio_s", "fin_s", "acceso",
        "tipo_vehiculo", "cantidad"
    ])

    for bloque in range(duracion // intervalo):
        for via, nombre in accesos.items():
            for tipo in tipos:
                escritor.writerow([
                    bloque * intervalo,
                    (bloque + 1) * intervalo,
                    nombre,
                    tipo,
                    conteos[(bloque, via, tipo)]
                ])

print("\nCONTEO COMPLETADO")
print("Archivo:", salida.name)
print("Accesos:", len(accesos))
print("Tipos vehiculares:", len(tipos))
print("Intervalos:", duracion // intervalo)
print("Total de registros:", 360)
print("Vehiculos contabilizados:", sum(conteos.values()))
