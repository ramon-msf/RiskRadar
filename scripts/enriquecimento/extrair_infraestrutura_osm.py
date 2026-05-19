import os
import subprocess


# ==============================
# CONFIGURAÇÕES
# ==============================

OSM_PBF = (
    "datasets/osm/raw/"
    "nordeste-260516.osm.pbf"
)

OUTPUT_DIR = (
    "datasets/osm/infrastructure"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ==============================
# ELEMENTOS
# ==============================

ELEMENTOS = {

    "traffic_signals":
        "n/highway=traffic_signals",

    "crossings":
        "n/highway=crossing",

    "speed_cameras":
        "n/highway=speed_camera",

    "traffic_calming":
        "n/traffic_calming"
}


# ==============================
# MAIN
# ==============================

def main():

    print(
        "\n[INFO] Extraindo "
        "infraestrutura OSM...\n"
    )

    for nome, filtro in ELEMENTOS.items():

        print(f"[INFO] {nome}")

        output_pbf = os.path.join(
            OUTPUT_DIR,
            f"{nome}.osm.pbf"
        )

        output_geojson = os.path.join(
            OUTPUT_DIR,
            f"{nome}.geojson"
        )

        # ==========================
        # FILTRO OSMIUM
        # ==========================

        comando_filtro = [

            "osmium",
            "tags-filter",

            OSM_PBF,

            filtro,

            "-o",
            output_pbf,

            "--overwrite"
        ]

        subprocess.run(
            comando_filtro,
            check=True
        )

        print(
            f"[INFO] PBF criado: "
            f"{output_pbf}"
        )

        # ==========================
        # EXPORTAÇÃO GEOJSON
        # ==========================

        comando_export = [

            "osmium",
            "export",

            output_pbf,

            "-o",
            output_geojson,

            "--overwrite"
        ]

        subprocess.run(
            comando_export,
            check=True
        )

        print(
            f"[INFO] GeoJSON criado: "
            f"{output_geojson}"
        )

    print(
        "\n[INFO] Processo concluído."
    )


if __name__ == "__main__":

    main()
