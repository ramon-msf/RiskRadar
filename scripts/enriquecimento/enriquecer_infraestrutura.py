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

INFRA_DIR = (
    "datasets/osm/infrastructure"
)

DISTANCIA_METROS = 50


# ==============================
# INFRAESTRUTURA
# ==============================

ARQUIVOS_INFRA = {

    "traffic_signal_near":
        "traffic_signals.geojson",

    "crossing_near":
        "crossings.geojson",

    "speed_camera_near":
        "speed_cameras.geojson",

    "traffic_calming_near":
        "traffic_calming.geojson"
}


# ==============================
# CARREGA INFRAESTRUTURA
# ==============================

print(
    "\n[INFO] Carregando "
    "infraestrutura OSM..."
)

infraestruturas = {}

for coluna, arquivo in ARQUIVOS_INFRA.items():

    caminho = os.path.join(
        INFRA_DIR,
        arquivo
    )

    if not os.path.exists(caminho):

        print(
            f"[WARNING] "
            f"Infraestrutura não encontrada: "
            f"{arquivo}"
        )

        continue

    gdf = gpd.read_file(
        caminho
    )

    if gdf.empty:

        print(
            f"[WARNING] "
            f"Infraestrutura vazia: "
            f"{arquivo}"
        )

        continue

    # converte CRS métrico
    gdf = gdf.to_crs(
        epsg=3857
    )

    infraestruturas[coluna] = gdf

    print(
        f"[INFO] {coluna}: "
        f"{len(gdf)} elementos"
    )


# ==============================
# MAIN
# ==============================

def main():

    print(
        "\n[INFO] Enriquecendo "
        "acidentes...\n"
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

        # ==========================
        # CARREGA ACIDENTES
        # ==========================

        acidentes = gpd.read_file(
            arquivo_acidentes
        )

        if acidentes.empty:

            print(
                "[WARNING] "
                "Sem acidentes."
            )

            continue

        print(
            f"[INFO] Acidentes: "
            f"{len(acidentes)}"
        )

        # ==========================
        # CRS MÉTRICO
        # ==========================

        acidentes = acidentes.to_crs(
            epsg=3857
        )

        # ==========================
        # CORREÇÃO HORÁRIO
        # ==========================

        if "horario" in acidentes.columns:

            acidentes["horario"] = (
                acidentes["horario"]
                .astype("string")
            )

        # ==========================
        # FLAGS
        # ==========================

        for coluna in ARQUIVOS_INFRA.keys():

            acidentes[coluna] = 0

        # ==========================
        # ENRIQUECIMENTO
        # ==========================

        for coluna, infra in infraestruturas.items():

            print(
                f"[INFO] Verificando "
                f"{coluna}"
            )

            # cria cópia
            infra_buffer = infra.copy()

            # buffer espacial
            infra_buffer["geometry"] = (
                infra_buffer.geometry.buffer(
                    DISTANCIA_METROS
                )
            )

            # spatial join
            join = gpd.sjoin(
                acidentes,
                infra_buffer,
                predicate="intersects",
                how="left"
            )

            # ======================
            # CORREÇÃO DO ERRO
            # ======================

            indices_validos = (

                join[
                    join.index_right.notnull()
                ].index.unique()
            )

            # marca acidentes
            acidentes.loc[
                indices_validos,
                coluna
            ] = 1

            print(
                f"[INFO] "
                f"{len(indices_validos)} acidentes "
                f"marcados"
            )

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
