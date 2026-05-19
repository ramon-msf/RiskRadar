import os

import numpy as np

import geopandas as gpd

from sklearn.cluster import DBSCAN

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

# distância máxima cluster
EPS_METROS = 150

# mínimo acidentes cluster
MIN_SAMPLES = 5


# ==============================
# MAIN
# ==============================

def main():

    print(
        "\n[INFO] Detectando "
        "hotspots...\n"
    )

    for br in BRS:

        print(f"\n[INFO] {br}")

        pasta_br = os.path.join(
            BASE_DIR,
            br
        )

        arquivo = os.path.join(
            pasta_br,
            "acidentes",
            "acidentes_score.geojson"
        )

        output = os.path.join(
            pasta_br,
            "acidentes",
            "hotspots.geojson"
        )

        # ==========================
        # VALIDA
        # ==========================

        if not os.path.exists(
            arquivo
        ):

            print(
                "[WARNING] "
                "Arquivo não encontrado."
            )

            continue

        # ==========================
        # CARREGA
        # ==========================

        gdf = gpd.read_file(
            arquivo
        )

        if gdf.empty:

            print(
                "[WARNING] "
                "Sem acidentes."
            )

            continue

        print(
            f"[INFO] Acidentes: "
            f"{len(gdf)}"
        )

        # ==========================
        # CRS MÉTRICO
        # ==========================

        gdf = gdf.to_crs(
            epsg=3857
        )

        # ==========================
        # COORDENADAS
        # ==========================

        coords = np.array([

            (
                geom.x,
                geom.y
            )

            for geom in gdf.geometry
        ])

        # ==========================
        # DBSCAN
        # ==========================

        clustering = DBSCAN(

            eps=EPS_METROS,
            min_samples=MIN_SAMPLES

        ).fit(coords)

        # labels
        gdf["hotspot_id"] = (
            clustering.labels_
        )

        # ==========================
        # HOTSPOT SCORE
        # ==========================

        gdf["hotspot_score"] = 0

        hotspots_validos = (

            gdf[
                gdf["hotspot_id"] != -1
            ]
        )

        for hotspot_id in (

            hotspots_validos[
                "hotspot_id"
            ].unique()
        ):

            subset = hotspots_validos[

                hotspots_validos[
                    "hotspot_id"
                ] == hotspot_id
            ]

            score_cluster = (

                subset[
                    "risk_score"
                ].sum()
            )

            gdf.loc[

                gdf["hotspot_id"]
                == hotspot_id,

                "hotspot_score"

            ] = score_cluster

        # ==========================
        # ESTATÍSTICAS
        # ==========================

        num_clusters = len(

            hotspots_validos[
                "hotspot_id"
            ].unique()
        )

        print(
            f"[INFO] Hotspots: "
            f"{num_clusters}"
        )

        # ==========================
        # EXPORTAÇÃO
        # ==========================

        gdf = gdf.to_crs(
            epsg=4326
        )

        gdf.to_file(
            output,
            driver="GeoJSON"
        )

        print(
            f"[INFO] Exportado: "
            f"{output}"
        )

    print(
        "\n[INFO] Processo concluído."
    )


if __name__ == "__main__":

    main()
