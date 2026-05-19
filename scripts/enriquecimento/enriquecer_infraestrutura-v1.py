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

DISTANCIA_METROS = 50


# ==============================
# TAGS OSM
# ==============================

TAGS_INTERESSE = {

    "traffic_signals":
        ("highway", "traffic_signals"),

    "crossing":
        ("highway", "crossing"),

    "speed_camera":
        ("highway", "speed_camera"),

    "traffic_calming":
        ("traffic_calming", None)
}


# ==============================
# MAIN
# ==============================

def main():

    print(
        "\n[INFO] Enriquecendo "
        "infraestrutura...\n"
    )

    for br in BRS:

        print(f"\n[INFO] {br}")

        pasta_br = os.path.join(
            BASE_DIR,
            br
        )

        arquivo_acidentes = os.path.join(
            pasta_br,
            "acidentes",
            "acidentes.geojson"
        )

        arquivo_rodovia = os.path.join(
            pasta_br,
            "rodovia",
            "br.geojson"
        )

        output = os.path.join(
            pasta_br,
            "acidentes",
            "acidentes_enriquecidos.geojson"
        )

        # ==========================
        # VALIDA
        # ==========================

        if not os.path.exists(
            arquivo_acidentes
        ):

            print(
                "[WARNING] "
                "Acidentes não encontrados."
            )

            continue

        if not os.path.exists(
            arquivo_rodovia
        ):

            print(
                "[WARNING] "
                "Rodovia não encontrada."
            )

            continue

        # ==========================
        # CARREGA
        # ==========================

        acidentes = gpd.read_file(
            arquivo_acidentes
        )

        rodovia = gpd.read_file(
            arquivo_rodovia
        )

        if acidentes.empty:

            print(
                "[WARNING] "
                "Sem acidentes."
            )

            continue

        if rodovia.empty:

            print(
                "[WARNING] "
                "Rodovia vazia."
            )

            continue

        # ==========================
        # CRS MÉTRICO
        # ==========================

        acidentes = acidentes.to_crs(
            epsg=3857
        )

        rodovia = rodovia.to_crs(
            epsg=3857
        )

        # ==========================
        # FLAGS
        # ==========================

        acidentes["traffic_signals"] = 0
        acidentes["crossing"] = 0
        acidentes["speed_camera"] = 0
        acidentes["traffic_calming"] = 0

        # ==========================
        # GEOMETRIA DA RODOVIA
        # ==========================

        geometria_unificada = (
            rodovia.unary_union
        )

        # ==========================
        # BUFFER LOCAL
        # ==========================

        buffer_local = (
            geometria_unificada.buffer(
                DISTANCIA_METROS
            )
        )

        # ==========================
        # VERIFICA PROXIMIDADE
        # ==========================

        acidentes.loc[
            acidentes.geometry.within(
                buffer_local
            ),
            "traffic_signals"
        ] = 1

        acidentes.loc[
            acidentes.geometry.within(
                buffer_local
            ),
            "crossing"
        ] = 1

        acidentes.loc[
            acidentes.geometry.within(
                buffer_local
            ),
            "speed_camera"
        ] = 1

        acidentes.loc[
            acidentes.geometry.within(
                buffer_local
            ),
            "traffic_calming"
        ] = 1

        # ==========================
        # EXPORTAÇÃO
        # ==========================

        acidentes = acidentes.to_crs(
            epsg=4326
        )

        acidentes.to_file(
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
