
from pathlib import Path
import xml.etree.ElementTree as ET

carpeta_proyecto = Path(__file__).resolve().parents[2]

archivos = {
    "original": (
        carpeta_proyecto
        / "04_resultados"
        / "02_repeticiones"
        / "rep_s43_punta_jp_salidas_sensores.xml"
    ),
    "traci": (
        carpeta_proyecto
        / "04_resultados"
        / "pruebas"
        / "prueba_conteos_salidas_sensores.xml"
    )
}
def leer_sensores(archivo):
    if not archivo.exists():
        raise FileNotFoundError(archivo.name)

    raiz = ET.parse(archivo).getroot()
    datos = {}

    for elemento in raiz.iter("interval"):
        clave = (
            elemento.get("id"),
            elemento.get("begin"),
            elemento.get("end")
        )

        datos[clave] = {
            "nVehEntered": elemento.get("nVehEntered"),
            "meanSpeed": elemento.get("meanSpeed"),
            "meanOccupancy": elemento.get("meanOccupancy"),
            "maxJamLengthInMeters": elemento.get(
                "maxJamLengthInMeters"
            )
        }

    return datos

original = leer_sensores(archivos["original"])
traci = leer_sensores(archivos["traci"])

print("\nVALIDACION DE REPRODUCIBILIDAD")
print("=" * 60)

print("Registros originales:", len(original))
print("Registros TraCI:", len(traci))

claves = set(original) | set(traci)

diferencias = []

for clave in sorted(claves):
    if original.get(clave) != traci.get(clave):
        diferencias.append(clave)

print("Registros diferentes:", len(diferencias))

if not diferencias:
    print("\nRESULTADO: COINCIDENCIA COMPLETA")
    print("Las mediciones seleccionadas son iguales.")
else:
    print("\nRESULTADO: EXISTEN DIFERENCIAS")

    for clave in diferencias[:5]:
        print("\nSensor e intervalo:", clave)
        print("Original:", original.get(clave))
        print("TraCI:", traci.get(clave))

print("\nVALIDACION FINALIZADA")
