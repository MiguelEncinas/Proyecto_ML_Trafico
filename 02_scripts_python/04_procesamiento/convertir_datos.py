
import csv
import re
from pathlib import Path
from xml.etree import ElementTree as ET

# Archivos de entrada y salida
carpeta = Path(__file__).resolve().parents[2]
archivo_xml = carpeta /  "04_resultados" / "01_simulaciones_originales" / "media_salidas_sensores.xml"
archivo_csv = carpeta / "03_datos" / "01_originales" / "datos_trafico_PRUEBA_COMPLETA.csv"

# Leer los datos generados por SUMO
contenido = archivo_xml.read_text(encoding="utf-8")

# Extraer los registros de los sensores E2
etiquetas = re.findall(r"<interval\b[^>]*?/>", contenido)
registros = [ET.fromstring(etiqueta).attrib for etiqueta in etiquetas]

if not registros:
    raise ValueError("No se encontraron registros de sensores.")

# Obtener los nombres de las columnas
columnas = list(registros[0].keys())

# Crear archivo CSV compatible con Excel
with archivo_csv.open("w", newline="", encoding="utf-8-sig") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=columnas)
    escritor.writeheader()
    escritor.writerows(registros)

# Mostrar resultados
sensores = {registro["id"] for registro in registros}
intervalos = {(r["begin"], r["end"]) for r in registros}

print("CONVERSION COMPLETADA")
print("Registros:", len(registros))
print("Sensores:", len(sensores))
print("Intervalos:", len(intervalos))
print("Archivo generado:", archivo_csv.name)
