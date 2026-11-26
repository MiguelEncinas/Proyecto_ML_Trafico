import subprocess
import sumolib
from pathlib import Path
carpeta_proyecto = Path(__file__).resolve().parents[2]
carpeta_pruebas = carpeta_proyecto / "01_simulacion_sumo" / "pruebas_generacion"
carpeta_pruebas.mkdir(parents=True, exist_ok=True)

# 1. NODOS (Coordenadas en metros)
NODOS_XML = """<nodes>
    <!-- Dos cruces semaforizados sobre el puente de Aviación -->
    <node id="J_IZQ" x="-60.0" y="0.0" type="traffic_light" radius="12"/>
    <node id="J_DER" x="60.0"  y="0.0" type="traffic_light" radius="12"/>

    <!-- Extremos de Av. Aviación -->
    <node id="AVI_IZQ" x="-360.0" y="0.0" type="priority"/>
    <node id="AVI_DER" x="360.0"  y="0.0" type="priority"/>

    <!-- Javier Prado Auxiliar (Lado Teatro/BNP: baja con incorporación a media vía) -->
    <node id="JP_ARRIBA_IZQ" x="-60.0" y="300.0"  type="priority"/>
    <node id="JP_BAJA_MERGE" x="-60.0" y="180.0"  type="priority"/>
    <node id="JP_ABAJO_IZQ"  x="-60.0" y="-300.0" type="priority"/>

    <!-- Javier Prado Auxiliar (Lado La Rambla: sube) -->
    <node id="JP_ABAJO_DER"  x="60.0"  y="-300.0" type="priority"/>
    <node id="JP_ARRIBA_DER" x="60.0"  y="300.0"  type="priority"/>

    <!-- Conexiones con el túnel (Vía Expresa) -->
    <node id="TUNEL_NORTE_IN" x="-10.0" y="300.0"  type="priority"/>
    <node id="TUNEL_DESTINO"  x="-10.0" y="140.0"  type="priority"/>
    <node id="TUNEL_SUR_BNP"  x="-10.0" y="-240.0" type="priority"/>
    <node id="BNP_RAMPA_BASE" x="-30.0" y="-110.0" type="priority"/>
</nodes>
"""

# 2. CALLES Y CARRILES
# Avenidas principales: 2 carriles por sentido (mismo grosor).
# En Javier Prado arriba: carril 0 = Corredor Rojo (media vía), carril 1 = particulares y motos.
# Conexiones al túnel: 1 carril angosto, unidireccional, SOLO particulares y camionetas (passenger).
CALLES_XML = """<edges>
    <!-- Javier Prado Auxiliar SUBIENDO (Lado La Rambla -> Financiera OH) -->
    <edge id="jp_sube_sur" from="JP_ABAJO_DER" to="J_DER" numLanes="2" speed="13.89">
        <lane index="0" allow="bus"/>
        <lane index="1" disallow="bus"/>
    </edge>
    <edge id="jp_sube_norte" from="J_DER" to="JP_ARRIBA_DER" numLanes="2" speed="13.89">
        <lane index="0" allow="bus"/>
        <lane index="1" disallow="bus"/>
    </edge>

    <!-- Javier Prado Auxiliar BAJANDO (Lado Teatro -> BNP) -->
    <edge id="jp_baja_norte_1" from="JP_ARRIBA_IZQ" to="JP_BAJA_MERGE" numLanes="2" speed="13.89">
        <lane index="0" allow="bus"/>
        <lane index="1" disallow="bus"/>
    </edge>
    <edge id="jp_baja_norte_2" from="JP_BAJA_MERGE" to="J_IZQ" numLanes="2" speed="13.89">
        <lane index="0" allow="bus"/>
        <lane index="1" disallow="bus"/>
    </edge>
    <edge id="jp_baja_sur" from="J_IZQ" to="JP_ABAJO_IZQ" numLanes="2" speed="13.89">
        <lane index="0" allow="bus"/>
        <lane index="1" disallow="bus"/>
    </edge>

    <!-- Alimentación desde el túnel norte a media avenida (1 carril, SOLO particulares/camionetas) -->
    <edge id="salida_tunel_teatro" from="TUNEL_NORTE_IN" to="JP_BAJA_MERGE" numLanes="1" speed="11.11" allow="passenger"
          shape="-10,300 -10,250 -25,210 -60,180"/>

    <!-- Rampa ENTRANDO desde Aviación (solo este->oeste) hacia el túnel (1 carril, SOLO particulares/camionetas) -->
    <edge id="rampa_hacia_tunel" from="J_IZQ" to="TUNEL_DESTINO" numLanes="1" speed="11.11" allow="passenger"
          shape="-60,0 -45,45 -20,95 -10,140"/>

    <!-- Rampa SALIENDO del túnel sur (BNP) hacia Aviación Este (1 carril, SOLO particulares/camionetas) -->
    <edge id="entrada_tunel_bnp" from="TUNEL_SUR_BNP" to="BNP_RAMPA_BASE" numLanes="1" speed="11.11" allow="passenger"
          shape="-10,-240 -12,-180 -22,-140 -30,-110"/>
    <edge id="rampa_bnp" from="BNP_RAMPA_BASE" to="J_IZQ" numLanes="1" speed="11.11" allow="passenger"
          shape="-30,-110 -36,-65 -48,-30 -60,0"/>

    <!-- Av. Aviación (2 carriles por sentido: buses públicos + particulares) -->
    <edge id="avi_izq_in"   from="AVI_IZQ" to="J_IZQ"   numLanes="2" speed="13.89"/>
    <edge id="avi_izq_out"  from="J_IZQ"   to="AVI_IZQ" numLanes="2" speed="13.89"/>
    <edge id="puente_a_der" from="J_IZQ"   to="J_DER"   numLanes="2" speed="11.11"/>
    <edge id="puente_a_izq" from="J_DER"   to="J_IZQ"   numLanes="2" speed="11.11"/>
    <edge id="avi_der_out"  from="J_DER"   to="AVI_DER" numLanes="2" speed="13.89"/>
    <edge id="avi_der_in"   from="AVI_DER" to="J_DER"   numLanes="2" speed="13.89"/>
</edges>
"""

# 3. CONEXIONES EXPLÍCITAS
CONEXIONES_XML = """<connections>
    <!-- Incorporación a media avenida en JP_BAJA_MERGE -->
    <connection from="jp_baja_norte_1"     to="jp_baja_norte_2" fromLane="0" toLane="0"/>
    <connection from="jp_baja_norte_1"     to="jp_baja_norte_2" fromLane="1" toLane="1"/>
    <connection from="salida_tunel_teatro" to="jp_baja_norte_2" fromLane="0" toLane="1"/>

    <!-- Javier Prado bajando en J_IZQ -->
    <connection from="jp_baja_norte_2" to="jp_baja_sur" fromLane="0" toLane="0"/>
    <connection from="jp_baja_norte_2" to="jp_baja_sur" fromLane="1" toLane="1"/>
    <connection from="jp_baja_norte_2" to="avi_izq_out" fromLane="1" toLane="0"/>

    <!-- Salida del túnel sur (BNP): ÚNICAMENTE hacia el este (puente_a_der) -->
    <connection from="rampa_bnp" to="puente_a_der" fromLane="0" toLane="0"/>

    <!-- Aviación de OESTE a ESTE (avi_izq_in): NO puede entrar al túnel -->
    <connection from="avi_izq_in" to="puente_a_der" fromLane="0" toLane="0"/>
    <connection from="avi_izq_in" to="puente_a_der" fromLane="1" toLane="1"/>
    <connection from="avi_izq_in" to="jp_baja_sur"  fromLane="0" toLane="1"/>

    <!-- Aviación de ESTE a OESTE (puente_a_izq): ÚNICA vía que entra al túnel -->
    <connection from="puente_a_izq" to="avi_izq_out"       fromLane="0" toLane="0"/>
    <connection from="puente_a_izq" to="avi_izq_out"       fromLane="1" toLane="1"/>
    <connection from="puente_a_izq" to="rampa_hacia_tunel" fromLane="0" toLane="0"/>
    <connection from="puente_a_izq" to="jp_baja_sur"       fromLane="1" toLane="1"/>

    <!-- Javier Prado subiendo en J_DER -->
    <connection from="jp_sube_sur" to="jp_sube_norte" fromLane="0" toLane="0"/>
    <connection from="jp_sube_sur" to="jp_sube_norte" fromLane="1" toLane="1"/>
    <connection from="jp_sube_sur" to="avi_der_out"   fromLane="1" toLane="0"/>

    <!-- Aviación desde derecha (este->oeste) en J_DER -->
    <connection from="avi_der_in" to="puente_a_izq"  fromLane="0" toLane="0"/>
    <connection from="avi_der_in" to="puente_a_izq"  fromLane="1" toLane="1"/>
    <connection from="avi_der_in" to="jp_sube_norte" fromLane="0" toLane="1"/>

    <!-- Puente hacia derecha (oeste->este) en J_DER -->
    <connection from="puente_a_der" to="avi_der_out"   fromLane="0" toLane="0"/>
    <connection from="puente_a_der" to="avi_der_out"   fromLane="1" toLane="1"/>
    <connection from="puente_a_der" to="jp_sube_norte" fromLane="1" toLane="1"/>
</connections>
"""

# 4. PARADEROS Y SENSORES DE ÁREA (E2 UPSTREAM)
ADICIONALES_XML = """<additional>
    <!-- Paraderos reales -->
    <busStop id="paradero_rambla"  lane="jp_sube_sur_0"     startPos="160" endPos="200" name="Paradero La Rambla (Corredor)"/>
    <busStop id="paradero_teatro"  lane="jp_baja_norte_2_0" startPos="60"  endPos="100" name="Paradero Teatro Nacional (Corredor)"/>
    <busStop id="paradero_cultura" lane="avi_izq_in_0"      startPos="170" endPos="210" name="Estacion La Cultura"/>
    <busStop id="paradero_tambo"   lane="avi_der_in_0"      startPos="170" endPos="210" name="Paradero Aviacion / Tambo"/>

    <!-- Detectores de área (E2) ajustados al número exacto de carriles -->
    <laneAreaDetector id="e2_jp_sube_bus"   lane="jp_sube_sur_0"     pos="50" length="200" freq="300" file="salidas_sensores.xml"/>
    <laneAreaDetector id="e2_jp_sube_priv"  lane="jp_sube_sur_1"     pos="50" length="200" freq="300" file="salidas_sensores.xml"/>

    <laneAreaDetector id="e2_jp_baja_bus"   lane="jp_baja_norte_2_0" pos="10" length="140" freq="300" file="salidas_sensores.xml"/>
    <laneAreaDetector id="e2_jp_baja_priv"  lane="jp_baja_norte_2_1" pos="10" length="140" freq="300" file="salidas_sensores.xml"/>

    <laneAreaDetector id="e2_tunel_norte_0" lane="salida_tunel_teatro_0" pos="15" length="90" freq="300" file="salidas_sensores.xml"/>

    <laneAreaDetector id="e2_avi_izq_0" lane="avi_izq_in_0" pos="60" length="200" freq="300" file="salidas_sensores.xml"/>
    <laneAreaDetector id="e2_avi_izq_1" lane="avi_izq_in_1" pos="60" length="200" freq="300" file="salidas_sensores.xml"/>

    <laneAreaDetector id="e2_avi_der_0" lane="avi_der_in_0" pos="60" length="200" freq="300" file="salidas_sensores.xml"/>
    <laneAreaDetector id="e2_avi_der_1" lane="avi_der_in_1" pos="60" length="200" freq="300" file="salidas_sensores.xml"/>

    <laneAreaDetector id="e2_rampa_0"   lane="rampa_bnp_0"  pos="10" length="80"  freq="300" file="salidas_sensores.xml"/>
</additional>
"""

# 5. TRÁFICO DE PRUEBA (1 hora simulada)
RUTAS_XML = """<routes>
    <!-- Tipos de vehículos -->
    <vType id="auto"         vClass="passenger"  length="4.5"  maxSpeed="13.89" color="255,220,0"/>
    <vType id="camioneta"    vClass="passenger"  length="5.3"  maxSpeed="13.89" color="180,180,180"/>
    <vType id="moto"         vClass="motorcycle" length="2.2"  maxSpeed="15.0"  color="255,120,0"/>
    <vType id="corredor"     vClass="bus"        length="12.0" maxSpeed="11.11" color="220,20,20"/>
    <vType id="bus_aviacion" vClass="bus"        length="10.5" maxSpeed="11.11" color="30,110,220"/>

    <!-- Rutas Javier Prado (arriba) -->
    <route id="r_jp_sube"          edges="jp_sube_sur jp_sube_norte"/>
    <route id="r_jp_sube_der"      edges="jp_sube_sur avi_der_out"/>
    <route id="r_jp_baja"          edges="jp_baja_norte_1 jp_baja_norte_2 jp_baja_sur"/>
    <route id="r_jp_baja_der"      edges="jp_baja_norte_1 jp_baja_norte_2 avi_izq_out"/>

    <!-- Alimentación desde túnel norte a media avenida (SOLO particulares/camionetas) -->
    <route id="r_tunel_norte_baja" edges="salida_tunel_teatro jp_baja_norte_2 jp_baja_sur"/>
    <route id="r_tunel_norte_avi"  edges="salida_tunel_teatro jp_baja_norte_2 avi_izq_out"/>

    <!-- Rutas Av. Aviación (todo de frente) -->
    <route id="r_avi_hacia_der"    edges="avi_izq_in puente_a_der avi_der_out"/>
    <route id="r_avi_hacia_izq"    edges="avi_der_in puente_a_izq avi_izq_out"/>

    <!-- Particulares girando desde Aviación hacia JP o hacia el túnel (SOLO este->oeste al túnel) -->
    <route id="r_avi_izq_a_jp"     edges="avi_izq_in jp_baja_sur"/>
    <route id="r_avi_der_a_jp"     edges="avi_der_in jp_sube_norte"/>
    <route id="r_avi_der_a_tunel"  edges="avi_der_in puente_a_izq rampa_hacia_tunel"/>

    <!-- Salida del túnel sur (BNP) -> Aviación Este (SOLO particulares/camionetas) -->
    <route id="r_tunel_bnp_este"   edges="entrada_tunel_bnp rampa_bnp puente_a_der avi_der_out"/>

    <!-- 1. Corredor Rojo (SOLO por arriba en su carril segregado) -->
    <flow id="f_corredor_sube" type="corredor" route="r_jp_sube" begin="0" end="3600" vehsPerHour="45">
        <stop busStop="paradero_rambla" duration="20"/>
    </flow>
    <flow id="f_corredor_baja" type="corredor" route="r_jp_baja" begin="0" end="3600" vehsPerHour="40">
        <stop busStop="paradero_teatro" duration="20"/>
    </flow>

    <!-- 2. Particulares, camionetas y motos en Javier Prado (arriba) -->
    <flow id="f_jp_sube_auto" type="auto"      route="r_jp_sube"     begin="0" end="3600" vehsPerHour="260"/>
    <flow id="f_jp_sube_cam"  type="camioneta" route="r_jp_sube"     begin="0" end="3600" vehsPerHour="100"/>
    <flow id="f_jp_sube_moto" type="moto"      route="r_jp_sube"     begin="0" end="3600" vehsPerHour="90"/>
    <flow id="f_jp_sube_giro" type="auto"      route="r_jp_sube_der" begin="0" end="3600" vehsPerHour="80"/>

    <flow id="f_jp_baja_auto" type="auto"      route="r_jp_baja"     begin="0" end="3600" vehsPerHour="200"/>
    <flow id="f_jp_baja_cam"  type="camioneta" route="r_jp_baja"     begin="0" end="3600" vehsPerHour="80"/>
    <flow id="f_jp_baja_moto" type="moto"      route="r_jp_baja"     begin="0" end="3600" vehsPerHour="80"/>
    <flow id="f_jp_baja_giro" type="auto"      route="r_jp_baja_der" begin="0" end="3600" vehsPerHour="60"/>

    <!-- Alimentación desde túnel norte (SOLO particulares y camionetas) -->
    <flow id="f_tunel_n_auto" type="auto"      route="r_tunel_norte_baja" begin="0" end="3600" vehsPerHour="120"/>
    <flow id="f_tunel_n_cam"  type="camioneta" route="r_tunel_norte_baja" begin="0" end="3600" vehsPerHour="60"/>
    <flow id="f_tunel_n_avi"  type="auto"      route="r_tunel_norte_avi"  begin="0" end="3600" vehsPerHour="50"/>

    <!-- 3. Av. Aviación: Buses públicos en mayor proporción (SOLO de frente) + particulares -->
    <flow id="f_avi_der_bus"  type="bus_aviacion" route="r_avi_hacia_der" begin="0" end="3600" vehsPerHour="180">
        <stop busStop="paradero_cultura" duration="18"/>
    </flow>
    <flow id="f_avi_der_auto" type="auto"         route="r_avi_hacia_der" begin="0" end="3600" vehsPerHour="140"/>
    <flow id="f_avi_der_cam"  type="camioneta"    route="r_avi_hacia_der" begin="0" end="3600" vehsPerHour="55"/>

    <flow id="f_avi_izq_bus"  type="bus_aviacion" route="r_avi_hacia_izq" begin="0" end="3600" vehsPerHour="175">
        <stop busStop="paradero_tambo" duration="18"/>
    </flow>
    <flow id="f_avi_izq_auto" type="auto"         route="r_avi_hacia_izq" begin="0" end="3600" vehsPerHour="130"/>
    <flow id="f_avi_izq_cam"  type="camioneta"    route="r_avi_hacia_izq" begin="0" end="3600" vehsPerHour="50"/>

    <!-- 4. Particulares desde Aviación hacia JP o hacia el túnel (SOLO este->oeste) -->
    <flow id="f_avi_izq_jp"    type="auto"      route="r_avi_izq_a_jp"    begin="0" end="3600" vehsPerHour="70"/>
    <flow id="f_avi_der_jp"    type="auto"      route="r_avi_der_a_jp"    begin="0" end="3600" vehsPerHour="70"/>
    <flow id="f_avi_der_tunel" type="auto"      route="r_avi_der_a_tunel" begin="0" end="3600" vehsPerHour="90"/>
    <flow id="f_avi_der_tun_c" type="camioneta" route="r_avi_der_a_tunel" begin="0" end="3600" vehsPerHour="50"/>

    <!-- 5. Túnel sur (BNP) -> Aviación Este (SOLO particulares y camionetas) -->
    <flow id="f_tunel_bnp_auto" type="auto"      route="r_tunel_bnp_este" begin="0" end="3600" vehsPerHour="120"/>
    <flow id="f_tunel_bnp_cam"  type="camioneta" route="r_tunel_bnp_este" begin="0" end="3600" vehsPerHour="70"/>
</routes>
"""

# 6. ARCHIVO DE CONFIGURACIÓN DE SUMO
CONFIG_XML = """<configuration>
    <input>
        <net-file value="jp_aviacion.net.xml"/>
        <route-files value="trafico_prueba.rou.xml"/>
        <additional-files value="adicionales.add.xml"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
    </time>
</configuration>
"""

def main():
    archivos = {
        "jp_aviacion.nod.xml": NODOS_XML,
        "jp_aviacion.edg.xml": CALLES_XML,
        "jp_aviacion.con.xml": CONEXIONES_XML,
        "adicionales.add.xml": ADICIONALES_XML,
        "trafico_prueba.rou.xml": RUTAS_XML,
        "simulacion.sumocfg": CONFIG_XML,
    }
    for nombre, contenido in archivos.items():
        destino = carpeta_pruebas / nombre
        with destino.open("w", encoding="utf-8") as f:
            f.write(contenido)
    print("Archivos XML generados correctamente.")

    netconvert_bin = sumolib.checkBinary("netconvert")
    cmd = [
        netconvert_bin,
        "--node-files", "jp_aviacion.nod.xml",
        "--edge-files", "jp_aviacion.edg.xml",
        "--connection-files", "jp_aviacion.con.xml",
        "--output-file", "jp_aviacion.net.xml",
        "--no-turnarounds", "true",
    ]
    subprocess.run(cmd, check=True, cwd=carpeta_pruebas)
    print("Red compilada: jp_aviacion.net.xml")

    sumo_gui_bin = sumolib.checkBinary("sumo-gui")
    subprocess.Popen(
        [sumo_gui_bin, "-c", "simulacion.sumocfg"],
        cwd=carpeta_pruebas
        )
    print("Abriendo SUMO-GUI...")
    
if __name__ == "__main__":
    main()