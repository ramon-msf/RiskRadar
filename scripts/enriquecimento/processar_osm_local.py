from pyrosm import OSM
import geopandas as gpd


# ==============================
# CONFIGURAÇÕES
# ==============================

OSM_FILE = "../../datasets/osm/brazil-260515.osm.pbf"

OUTPUT_DIR = "../../datasets/osm/"


# ==============================
# MAIN
# ==============================

def main():

    print("[INFO] Carregando arquivo OSM...")

    osm = OSM(OSM_FILE)

    print("[INFO] Extraindo pontos de interesse...")

    pois = osm.get_pois()

    print(f"[INFO] Total de POIs: {len(pois)}")

    # ==========================
    # FILTROS
    # ==========================

    filtros = {

        "traffic_signals": (
            pois["highway"] == "traffic_signals"
        ),

        "speed_camera": (
            pois["highway"] == "speed_camera"
        ),

        "bus_stop": (
            pois["highway"] == "bus_stop"
        ),

        "traffic_calming": (
            pois["traffic_calming"].notnull()
        )
    }

    # ==========================
    # EXPORTAÇÃO
    # ==========================

    for nome, filtro in filtros.items():

        try:

            gdf = pois[filtro]

            print(
                f"\n[INFO] {nome}: "
                f"{len(gdf)} registros"
            )

            output_file = (
                f"{OUTPUT_DIR}/{nome}.geojson"
            )

            gdf.to_file(
                output_file,
                driver="GeoJSON"
            )

            print(
                f"[INFO] Arquivo salvo: "
                f"{output_file}"
            )

        except Exception as e:

            print(
                f"[ERRO] {nome}: {e}"
            )

    print("\n[INFO] Processamento concluído.")


if __name__ == "__main__":

    main()
