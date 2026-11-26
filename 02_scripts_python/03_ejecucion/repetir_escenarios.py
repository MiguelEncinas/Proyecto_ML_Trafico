
from pathlib import Path
import subprocess

from sumolib import checkBinary

carpeta = Path(__file__).resolve().parents[2]
config = carpeta / "01_simulacion_sumo" / "configuracion" / "simulacion.sumocfg"
carpeta_escenarios = carpeta / "01_simulacion_sumo" / "escenarios"
carpeta_resultados = carpeta / "04_resultados" / "nuevas_ejecuciones" / "repeticiones"
carpeta_resultados.mkdir(parents=True, exist_ok=True)

escenarios = [
    "baja",
    "media",
    "alta",
    "punta_jp",
    "punta_avi",
    "punta_tuneles",
    "asimetrico_1",
    "asimetrico_2"
]

semillas = [43, 44]

print("\nREPETICION DE ESCENARIOS SUMO")
print("=" * 60)

completadas = 0

for semilla in semillas:
    for escenario in escenarios:

        rutas = carpeta_escenarios / f"trafico_{escenario}.rou.xml"
        prefijo = f"rep_s{semilla}_{escenario}_"

        if not rutas.exists():
            raise FileNotFoundError(rutas.name)

        print(
            f"\nEscenario: {escenario} "
            f"| Semilla: {semilla}",
            flush=True
        )

        comando = [
            checkBinary("sumo"),
            "-c", str(config),
            "--route-files", str(rutas),
            "--begin", "0",
            "--end", "3600",
            "--seed", str(semilla),
            "--output-prefix", f"../../04_resultados/nuevas_ejecuciones/repeticiones/{prefijo}",
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
            print("ERROR EN LA SIMULACION")
            print(resultado.stdout)
            print(resultado.stderr)
            raise SystemExit(1)

        archivos = [
            carpeta_resultados / f"{prefijo}salidas_sensores.xml",
            carpeta_resultados / f"{prefijo}tripinfo.xml",
            carpeta_resultados / f"{prefijo}resumen.xml"
        ]

        for archivo in archivos:
            if not archivo.exists():
                raise FileNotFoundError(
                    f"No se genero: {archivo.name}"
                )

        completadas += 1
        print("Resultado: OK", flush=True)

print("\nREPETICIONES FINALIZADAS")
print("Nuevas ejecuciones:", completadas)
print("Ejecuciones originales:", len(escenarios))
print("Total acumulado:", completadas + len(escenarios))
