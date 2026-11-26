
from pathlib import Path
from collections import defaultdict
import csv
import xml.etree.ElementTree as ET

carpeta = Path(__file__).resolve().parents[2]

escenarios = [
    "baja", "media", "alta",
    "punta_jp", "punta_avi", "punta_tuneles",
    "asimetrico_1", "asimetrico_2"
]
semillas = [42, 43, 44]

zonas = {
    "e2_jp_sube_bus": "jp_sube",
    "e2_jp_sube_priv": "jp_sube",
    "e2_jp_baja_bus": "jp_baja",
    "e2_jp_baja_priv": "jp_baja",
    "e2_tunel_norte_0": "tunel_norte",
    "e2_avi_izq_0": "avi_izq",
    "e2_avi_izq_1": "avi_izq",
    "e2_avi_der_0": "avi_der",
    "e2_avi_der_1": "avi_der",
    "e2_rampa_0": "rampa_bnp"
}

tipos = [
    "auto", "camioneta", "moto",
    "corredor", "bus_aviacion"
]

entrada = carpeta / "03_datos" / "02_procesados" / "conteos_24_ejecuciones.csv"
salida = carpeta / "03_datos" / "03_base_ml" / "base_ampliada_ML_PRUEBA.csv"

# 1. Leer y agrupar los conteos por tipo
conteos = defaultdict(lambda: defaultdict(int))
claves_conteo = set()

with entrada.open(
    "r", encoding="utf-8-sig", newline=""
) as archivo:

    lector = csv.DictReader(archivo)

    for fila in lector:
        clave_detalle = (
            fila["escenario"],
            int(fila["semilla"]),
            int(fila["inicio_s"]),
            int(fila["fin_s"]),
            fila["zona"],
            fila["tipo_vehiculo"]
        )

        if clave_detalle in claves_conteo:
            raise ValueError(
                f"Conteo duplicado: {clave_detalle}"
            )

        claves_conteo.add(clave_detalle)

        clave = clave_detalle[:5]
        tipo = clave_detalle[5]

        if tipo not in tipos:
            raise ValueError(f"Tipo desconocido: {tipo}")

        conteos[clave][tipo] = int(fila["cantidad"])

if len(claves_conteo) != 8640:
    raise ValueError(
        f"Se esperaban 8640 conteos, hay "
        f"{len(claves_conteo)}"
    )

# 2. Integrar con los sensores E2
resultados = []
claves_sensores = set()

for escenario in escenarios:
    for semilla in semillas:

        if semilla == 42:
            prefijo = f"{escenario}_"
            carpeta_xml = carpeta / "04_resultados" / "01_simulaciones_originales"
        else:
            prefijo = f"rep_s{semilla}_{escenario}_"
            carpeta_xml = carpeta / "04_resultados" / "02_repeticiones"

        archivo_xml = carpeta_xml / (
            prefijo + "salidas_sensores.xml"
        )

        if not archivo_xml.exists():
            raise FileNotFoundError(archivo_xml.name)

        raiz = ET.parse(archivo_xml).getroot()

        cantidad_e2 = 0

        for elemento in raiz.iter("interval"):
            sensor = elemento.get("id")

            if sensor not in zonas:
                raise ValueError(
                    f"Sensor desconocido: {sensor}"
                )

            inicio = round(float(elemento.get("begin")))
            fin = round(float(elemento.get("end")))
            zona = zonas[sensor]

            clave_sensor = (
                escenario, semilla, inicio, fin, sensor
            )

            if clave_sensor in claves_sensores:
                raise ValueError(
                    f"Sensor duplicado: {clave_sensor}"
                )

            claves_sensores.add(clave_sensor)

            clave_conteo = (
                escenario, semilla, inicio, fin, zona
            )

            if clave_conteo not in conteos:
                raise ValueError(
                    f"Conteo faltante: {clave_conteo}"
                )

            vehiculos = conteos[clave_conteo]

            registro = {
                "escenario": escenario,
                "semilla": semilla,
                "inicio_s": inicio,
                "fin_s": fin,
                "sensor": sensor,
                "zona": zona
            }

            for tipo in tipos:
                registro[f"n_{tipo}"] = vehiculos[tipo]

            registro["n_total_zona"] = sum(
                vehiculos[tipo] for tipo in tipos
            )

            # Conservar todos los indicadores E2
            for atributo, valor in elemento.attrib.items():
                if atributo not in ("id", "begin", "end"):
                    registro[atributo] = valor

            resultados.append(registro)
            cantidad_e2 += 1

        if cantidad_e2 != 120:
            raise ValueError(
                f"{escenario}, semilla {semilla}: "
                f"{cantidad_e2} filas E2 en lugar de 120"
            )

if len(resultados) != 2880:
    raise ValueError(
        f"Se esperaban 2880 filas: {len(resultados)}"
    )

# 3. Guardar conservando las columnas disponibles
campos = list(resultados[0].keys())

for fila in resultados:
    for nombre in fila:
        if nombre not in campos:
            campos.append(nombre)

with salida.open(
    "w", newline="", encoding="utf-8-sig"
) as archivo:

    escritor = csv.DictWriter(
        archivo, fieldnames=campos
    )

    escritor.writeheader()
    escritor.writerows(resultados)

print("\nINTEGRACION COMPLETADA")
print("=" * 55)
print("Escenarios:", len(escenarios))
print("Semillas:", len(semillas))
print("Ejecuciones:", len(escenarios) * len(semillas))
print("Registros integrados:", len(resultados))
print("Columnas:", len(campos))
print("Archivo:", salida.name)
