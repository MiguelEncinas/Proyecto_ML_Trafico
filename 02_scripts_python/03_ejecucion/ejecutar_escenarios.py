
from pathlib import Path
import subprocess

from sumolib import checkBinary

carpeta = Path(__file__).resolve().parents[2]

config = carpeta / "01_simulacion_sumo" / "configuracion" / "simulacion.sumocfg"

carpeta_escenarios = carpeta / "01_simulacion_sumo" / "escenarios"

carpeta_resultados = carpeta / "04_resultados" / "nuevas_ejecuciones" / "escenarios_basicos"
carpeta_resultados.mkdir(parents=True, exist_ok=True)

escenarios = ["baja", "media", "alta"]

if not config.exists():
    raise FileNotFoundError(
        "No se encontro simulacion.sumocfg"
    )

print("\nEJECUCION DE ESCENARIOS SUMO")
print("=" * 55)

for nombre in escenarios:

    rutas = carpeta_escenarios / f"trafico_{nombre}.rou.xml"

    if not rutas.exists():
        raise FileNotFoundError(
            f"No se encontro {rutas.name}"
        )

    print(f"\nEjecutando escenario: {nombre}")

    comando = [
        checkBinary("sumo"),
        "-c", str(config),
        "--route-files", str(rutas),
        "--begin", "0",
        "--end", "3600",
        "--seed", "42",
        "--output-prefix", f"../../04_resultados/nuevas_ejecuciones/escenarios_basicos/{nombre}_",
        "--tripinfo-output", "tripinfo.xml",
        "--summary-output", "resumen.xml",
        "--no-step-log", "true"
    ]

    resultado = subprocess.run(
        comando,
        cwd=config.parent,
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:
        print("ERROR EN EL ESCENARIO:", nombre)
        print(resultado.stdout)
        print(resultado.stderr)
        raise SystemExit(1)

    sensores = carpeta_resultados / f"{nombre}_salidas_sensores.xml"
    viajes = carpeta_resultados / f"{nombre}_tripinfo.xml"

    resumen = carpeta_resultados / f"{nombre}_resumen.xml"

    for archivo in [sensores, viajes, resumen]:
        print(
            archivo.name,
            "|",
            "OK" if archivo.exists() else "NO ENCONTRADO"
        )

    print("Escenario terminado:", nombre)

print("\nLOS TRES ESCENARIOS FINALIZARON")
