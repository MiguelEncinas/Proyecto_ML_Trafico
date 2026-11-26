
from pathlib import Path
import xml.etree.ElementTree as ET

# Leer la red generada por SUMO
carpeta_proyecto = Path(__file__).resolve().parents[2]
archivo = carpeta_proyecto / "01_simulacion_sumo" / "red_vial" / "jp_aviacion.net.xml"

raiz = ET.parse(archivo).getroot()

semaforos = raiz.findall("tlLogic")

print("\nAUDITORIA DE SEMAFOROS")
print("=" * 55)
print("Programas semaforicos encontrados:", len(semaforos))

for semaforo in semaforos:
    identificador = semaforo.get("id")
    programa = semaforo.get("programID")
    tipo = semaforo.get("type")

    print("\nSemaforo:", identificador)
    print("Programa:", programa)
    print("Tipo:", tipo)

    fases = semaforo.findall("phase")
    ciclo = 0

    for numero, fase in enumerate(fases, start=1):
        duracion = float(fase.get("duration", "0"))
        estado = fase.get("state", "")
        ciclo += duracion

        print(
            f"Fase {numero}: "
            f"{duracion:.1f} segundos | "
            f"Estado: {estado}"
        )

    print(f"Duracion total del ciclo: {ciclo:.1f} s")

    print("\nMovimientos controlados:")
    for conexion in raiz.findall("connection"):
        if conexion.get("tl") == identificador:
            print(
                f"  {conexion.get('from')} -> "
                f"{conexion.get('to')} | "
                f"indice {conexion.get('linkIndex')}"
            )

print("\nAUDITORIA FINALIZADA")
