from pyrosm import OSM
import geopandas as gpd


# ==============================
# CONFIGURAÇÕES
# ==============================

OSM_FILE = "../../datasets/osm/nordeste-260516.osm.pbf"

OUTPUT_FILE = "../../datasets/osm/brs.geojson"


# ==============================
# MAIN
# ==============================

def main():

    print("[INFO] Carregando OSM...")

    osm = OSM(OSM_FILE)

    print("[INFO] Extraindo rodovias...")

    # somente vias
    roads = osm.get_network(
        network_type="driving"
    )

    print(
        f"[INFO] Total de vias: {len(roads)}"
    )

    # ==========================
    # FILTRO BR
    # ==========================

    print("[INFO] Filtrando BRs...")

    brs = roads[
        roads["ref"].notnull()
    ]

    brs = brs[
        brs["ref"].str.contains(
            "BR",
            na=False
        )
    ]

    print(
        f"[INFO] BRs encontradas: "
        f"{len(brs)}"
    )

    # ==========================
    # EXPORTAÇÃO
    # ==========================

    brs.to_file(
        OUTPUT_FILE,
        driver="GeoJSON"
    )

    print(
        f"[INFO] Arquivo salvo: "
        f"{OUTPUT_FILE}"
    )

    print("\n[INFO] Processo concluído.")


if __name__ == "__main__":

    main()
