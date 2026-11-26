
from pathlib import Path
import subprocess

from sumolib import checkBinary

carpeta = Path(__file__).resolve().parents[2]
config = carpeta / "01_simulacion_sumo" / "configuracion" / "simulacion.sumocfg"
carpeta_escenarios = carpeta / "01_simulacion_sumo" / "escenarios"
carpeta_resultados = carpeta / "04_resultados" / "nuevas_ejecuciones" / "escenarios_variados"
carpeta_resultados.mkdir(parents=True, exist_ok=True)

# Excluimos punta_combinada porque
# es equivalente al escenario alta.
escenarios = [
    "punta_jp",
    "punta_avi",
    "punta_tuneles",
    "asimetrico_1",
    "asimetrico_2"
]

print("\nEJECUCION DE ESCENARIOS VARIADOS")
print("=" * 60)

for nombre in escenarios:

    rutas = carpeta_escenarios / f"trafico_{nombre}.rou.xml"

    if not rutas.exists():
        raise FileNotFoundError(
            f"No se encontro {rutas.name}"
        )

    print(f"\nEjecutando: {nombre}")

    comando = [
        checkBinary("sumo"),
        "-c", str(config),
        "--route-files", str(rutas),
        "--begin", "0",
        "--end", "3600",
        "--seed", "42",
        "--output-prefix", f"../../04_resultados/nuevas_ejecuciones/escenarios_variados/{nombre}_",
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
        print("ERROR:", nombre)
        print(resultado.stdout)
        print(resultado.stderr)
        raise SystemExit(1)

    archivos = [
        carpeta_resultados / f"{nombre}_salidas_sensores.xml",
        carpeta_resultados / f"{nombre}_tripinfo.xml",
        carpeta_resultados / f"{nombre}_resumen.xml"
    ]

    for archivo in archivos:
        if not archivo.exists():
            raise FileNotFoundError(
                f"No se genero {archivo.name}"
            )

        print(archivo.name, "| OK")

    print("Escenario finalizado:", nombre)

print("\nTODOS LOS ESCENARIOS VARIADOS FINALIZARON")
