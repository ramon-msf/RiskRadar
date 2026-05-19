import os
import subprocess

from config.rodovias import (
    REGIAO,
    BRS
)


# ==============================
# CONFIGURAÇÕES
# ==============================

OSM_PBF = (
    "datasets/osm/raw/"
    "nordeste-260516.osm.pbf"
)

BASE_OUTPUT = (
    "datasets/processed/"
    f"regioes/{REGIAO}"
)


# ==============================
# MAIN
# ==============================

def main():

    print("\n[INFO] Iniciando extração das BRs...\n")

    for br in BRS:

        print(f"[INFO] Processando {br}")

        # ==========================
        # DIRETÓRIOS
        # ==========================

        pasta_br = os.path.join(
            BASE_OUTPUT,
            br,
            "rodovia"
        )

        os.makedirs(
            pasta_br,
            exist_ok=True
        )

        # ==========================
        # OUTPUTS
        # ==========================

        output_pbf = os.path.join(
            pasta_br,
            "br.osm.pbf"
        )

        output_geojson = os.path.join(
            pasta_br,
            "br.geojson"
        )

        # ==========================
        # FILTRO OSMIUM
        # ==========================

        comando_filtro = [

            "osmium",
            "tags-filter",

            OSM_PBF,

            f"w/ref={br}",

            "-o",
            output_pbf
        ]

        print("[INFO] Filtrando OSM...")

        subprocess.run(
            comando_filtro,
            check=True
        )

        # ==========================
        # EXPORTAÇÃO GEOJSON
        # ==========================

        comando_export = [

            "osmium",
            "export",

            output_pbf,

            "-o",
            output_geojson
        ]

        print("[INFO] Exportando GeoJSON...")

        subprocess.run(
            comando_export,
            check=True
        )

        print(
            f"[INFO] {br} concluída.\n"
        )

    print(
        "[INFO] Processo finalizado."
    )


if __name__ == "__main__":

    main()
