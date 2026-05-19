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


# ==============================
# PESOS
# ==============================

PESOS = {

    "mortos":
        10,

    "feridos_graves":
        5,

    "feridos_leves":
        2,

    "traffic_signal_near":
        1,

    "crossing_near":
        2,

    "speed_camera_near":
        1,

    "traffic_calming_near":
        1
}


# ==============================
# CLASSIFICAÇÃO
# ==============================

PESO_CLASSIFICACAO = {

    "Sem Vítimas":
        0,

    "Com Vítimas Feridas":
        5,

    "Com Vítimas Fatais":
        15
}


# ==============================
# MAIN
# ==============================

def main():

    print(
        "\n[INFO] Calculando "
        "score de risco...\n"
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
            "acidentes_enriquecidos.geojson"
        )

        output = os.path.join(
            pasta_br,
            "acidentes",
            "acidentes_score.geojson"
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
        # SCORE BASE
        # ==========================

        gdf["risk_score"] = 0

        # ==========================
        # PESOS NUMÉRICOS
        # ==========================

        for coluna, peso in PESOS.items():

            if coluna in gdf.columns:

                gdf["risk_score"] += (

                    gdf[coluna]
                    .fillna(0)
                    .astype(float)

                    * peso
                )

        # ==========================
        # CLASSIFICAÇÃO
        # ==========================

        if (
            "classificacao_acidente"
            in gdf.columns
        ):

            gdf["risk_score"] += (

                gdf[
                    "classificacao_acidente"
                ]
                .map(
                    PESO_CLASSIFICACAO
                )
                .fillna(0)
            )

        # ==========================
        # NORMALIZAÇÃO
        # ==========================

        max_score = (
            gdf["risk_score"]
            .max()
        )

        if max_score > 0:

            gdf["risk_score_normalized"] = (

                gdf["risk_score"]

                / max_score
            )

        else:

            gdf[
                "risk_score_normalized"
            ] = 0

        # ==========================
        # EXPORTAÇÃO
        # ==========================

        gdf.to_file(
            output,
            driver="GeoJSON"
        )

        print(
            f"[INFO] Score máximo: "
            f"{max_score}"
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
