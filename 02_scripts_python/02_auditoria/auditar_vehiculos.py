
from pathlib import Path
import xml.etree.ElementTree as ET

carpeta = Path(__file__).resolve().parents[2]
archivo = carpeta / "01_simulacion_sumo/escenarios/trafico_prueba.rou.xml"

raiz = ET.parse(archivo).getroot()

print("\nAUDITORIA DE VEHICULOS")
print("=" * 55)

# Identificar tipos de vehiculos
tipos = raiz.findall("vType")

print("\n1. TIPOS DE VEHICULOS")
print("Tipos definidos:", len(tipos))

for vehiculo in tipos:
    print(
        "ID:", vehiculo.get("id"),
        "| Clase:", vehiculo.get("vClass"),
        "| Longitud:", vehiculo.get("length"),
        "| Velocidad maxima:", vehiculo.get("maxSpeed")
    )

# Identificar rutas
rutas = raiz.findall("route")

print("\n2. RUTAS CONFIGURADAS")
print("Rutas definidas:", len(rutas))

for ruta in rutas:
    print(
        "Ruta:", ruta.get("id"),
        "| Tramos:", ruta.get("edges")
    )

# Identificar flujos vehiculares
flujos = raiz.findall("flow")

print("\n3. FLUJOS VEHICULARES")
print("Flujos definidos:", len(flujos))

for flujo in flujos:
    print(
        "Flujo:", flujo.get("id"),
        "| Tipo:", flujo.get("type"),
        "| Ruta:", flujo.get("route"),
        "| Vehiculos/hora:", flujo.get("vehsPerHour"),
        "| Periodo:", flujo.get("period"),
        "| Probabilidad:", flujo.get("probability"),
        "| Numero:", flujo.get("number")
    )

print("\nAUDITORIA FINALIZADA")
