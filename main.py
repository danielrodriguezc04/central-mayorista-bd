import subprocess
import sys
import time

PASOS = [
    ("Extracción → Bronze", "scripts/extract.py"),
    ("Limpieza → Silver", "scripts/transform_silver.py"),
    ("Modelo → Gold", "scripts/transform_gold.py"),
    ("Consultas Analíticas", "scripts/analyze.py"),
    ("Benchmark", "scripts/benchmark.py"),
]

print("=" * 60)
print(" CENTRAL MAYORISTA — MINI LAKEHOUSE ")
print("=" * 60)

inicio_total = time.time()

for nombre, script in PASOS:
    print(f"\n>>> Ejecutando: {nombre}")
    inicio = time.time()

    resultado = subprocess.run([sys.executable, script])

    if resultado.returncode != 0:
        print(f"\nERROR en {script}")
        sys.exit(1)

    tiempo = time.time() - inicio
    print(f"Completado en {tiempo:.2f} segundos")

fin_total = time.time()

print("\n" + "=" * 60)
print(f"Pipeline finalizado correctamente en {fin_total - inicio_total:.2f} segundos")
print("Archivos finales disponibles en lakehouse/gold/")
print("=" * 60)