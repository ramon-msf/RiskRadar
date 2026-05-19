import os

import geopandas as gpd

from config.rodovias import (
    REGIAO,
    BRS
)


# ==============================
# CONFIGURAÇÕES
# ==============================

BASE_DIR = (
    f"datasets/processed/"
    f"regioes/{REGIAO}"
)

BUFFER_METROS = 75


# ==============================
# MAIN
# ==============================

def main():

    print(
        "\n[INFO] Criando corredores "
        "espaciais...\n"
    )

    for br in BRS:

        print(f"[INFO] Processando {br}")

        pasta_rodovia = os.path.join(
            BASE_DIR,
            br,
            "rodovia"
        )

        arquivo_br = os.path.join(
            pasta_rodovia,
            "br.geojson"
        )

        arquivo_corredor = os.path.join(
            pasta_rodovia,
            "corredor.geojson"
        )

        # ==========================
        # VALIDA EXISTÊNCIA
        # ==========================

        if not os.path.exists(
            arquivo_br
        ):

            print(
                f"[WARNING] "
                f"{arquivo_br} "
                "não encontrado."
            )

            continue

        # ==========================
        # CARREGA GEOMETRIA
        # ==========================

        gdf = gpd.read_file(
            arquivo_br
        )

        if gdf.empty:

            print(
                f"[WARNING] "
                f"{br} vazio."
            )

            continue

        # ==========================
        # CRS MÉTRICO
        # ==========================

        gdf = gdf.to_crs(
            epsg=3857
        )

        # ==========================
        # BUFFER
        # ==========================

        corredor = gdf.buffer(
            BUFFER_METROS
        )

        gdf_corredor = gpd.GeoDataFrame(
            geometry=corredor,
            crs=gdf.crs
        )

        # volta para WGS84
        gdf_corredor = (
            gdf_corredor.to_crs(
                epsg=4326
            )
        )

        # ==========================
        # EXPORTAÇÃO
        # ==========================

        gdf_corredor.to_file(
            arquivo_corredor,
            driver="GeoJSON"
        )

        print(
            f"[INFO] Corredor criado: "
            f"{arquivo_corredor}"
        )

    print(
        "\n[INFO] Processo concluído."
    )


if __name__ == "__main__":

    main()
