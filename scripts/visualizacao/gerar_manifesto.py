import os
import json

import geopandas as gpd

from config.rodovias import (
    REGIAO,
    BRS
)


# =====================================================
# CONFIGURAÇÕES
# =====================================================

BASE_DIR = (
    f"datasets/processed/regioes/{REGIAO}"
)

OUTPUT_DIR = (
    "output"
)

HOTSPOTS_DIR = (
    "output/hotspots"
)

MANIFESTO = os.path.join(
    OUTPUT_DIR,
    "manifest.json"
)


# =====================================================
# FUNÇÃO CLASSIFICAÇÃO
# =====================================================

def classificar_hotspot(
    mortos,
    acidentes
):

    if mortos >= 10:
        return "Crítico"

    elif mortos >= 5:
        return "Severo"

    elif acidentes >= 50:
        return "Recorrente"

    return "Moderado"


# =====================================================
# MAIN
# =====================================================

def main():

    print(
        "\n[INFO] Gerando manifesto...\n"
    )

    manifesto = []

    for br in BRS:

        print(f"[INFO] {br}")

        arquivo_hotspots = os.path.join(

            BASE_DIR,
            br,
            "acidentes",
            "hotspots.geojson"
        )

        mapa_html = (
            f"hotspots/{br}_hotspots.html"
        )

        if not os.path.exists(
            arquivo_hotspots
        ):

            print(
                "[WARNING] "
                "Hotspots não encontrados."
            )

            continue

        gdf = gpd.read_file(
            arquivo_hotspots
        )

        if gdf.empty:

            continue

        hotspots = gdf[
            gdf["hotspot_id"] != -1
        ]

        qtd_hotspots = (
            hotspots[
                "hotspot_id"
            ]
            .nunique()
        )

        qtd_acidentes = len(
            hotspots
        )

        mortos = 0

        if "mortos" in hotspots.columns:

            mortos = int(
                hotspots[
                    "mortos"
                ].sum()
            )

        severidade = (
            classificar_hotspot(
                mortos,
                qtd_acidentes
            )
        )

        manifesto.append({

            "br": br,

            "mapa": mapa_html,

            "hotspots": int(
                qtd_hotspots
            ),

            "acidentes": int(
                qtd_acidentes
            ),

            "mortos": mortos,

            "criticidade": severidade
        })

    # ===============================================
    # EXPORTAÇÃO
    # ===============================================

    with open(

        MANIFESTO,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            manifesto,

            f,

            ensure_ascii=False,

            indent=4
        )

    print(
        f"\n[INFO] Manifesto exportado: "
        f"{MANIFESTO}"
    )


if __name__ == "__main__":

    main()
