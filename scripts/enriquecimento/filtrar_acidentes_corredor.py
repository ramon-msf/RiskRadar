import os
import glob

import pandas as pd
import geopandas as gpd

from shapely.geometry import Point

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

DIRETORIO_PRF = (
    "datasets/processed/"
)


# ==============================
# CARREGA TODOS OS DATASETS PRF
# ==============================

print("\n[INFO] Carregando datasets PRF...")

arquivos_prf = sorted(

    glob.glob(
        os.path.join(
            DIRETORIO_PRF,
            "acidentes_*_processado.csv"
        )
    )
)

print(
    f"[INFO] Arquivos encontrados: "
    f"{len(arquivos_prf)}"
)

dfs = []

for arquivo in arquivos_prf:

    print(f"[INFO] Lendo: {arquivo}")

    df_temp = pd.read_csv(
        arquivo
    )

    print(
        f"[INFO] Registros: "
        f"{len(df_temp)}"
    )

    dfs.append(df_temp)

# concatenação
df = pd.concat(
    dfs,
    ignore_index=True
)

print(
    f"\n[INFO] Total consolidado: "
    f"{len(df)}"
)

# ==============================
# LIMPEZA
# ==============================

df = df.dropna(
    subset=[
        "latitude",
        "longitude"
    ]
)

print(
    f"[INFO] Após limpeza: "
    f"{len(df)}"
)

# ==============================
# GEODataFrame
# ==============================

geometry = [

    Point(lon, lat)

    for lon, lat in zip(
        df["longitude"],
        df["latitude"]
    )
]

gdf_acidentes = gpd.GeoDataFrame(
    df,
    geometry=geometry,
    crs="EPSG:4326"
)

print(
    "[INFO] GeoDataFrame criado."
)


# ==============================
# MAIN
# ==============================

def main():

    print(
        "\n[INFO] Filtrando acidentes "
        "por corredor...\n"
    )

    for br in BRS:

        print(f"[INFO] {br}")

        pasta_br = os.path.join(
            BASE_DIR,
            br
        )

        arquivo_corredor = os.path.join(
            pasta_br,
            "rodovia",
            "corredor.geojson"
        )

        pasta_acidentes = os.path.join(
            pasta_br,
            "acidentes"
        )

        os.makedirs(
            pasta_acidentes,
            exist_ok=True
        )

        output_geojson = os.path.join(
            pasta_acidentes,
            "acidentes.geojson"
        )

        # ==========================
        # VALIDA CORREDOR
        # ==========================

        if not os.path.exists(
            arquivo_corredor
        ):

            print(
                "[WARNING] "
                "Corredor não encontrado."
            )

            continue

        # ==========================
        # CARREGA CORREDOR
        # ==========================

        corredor = gpd.read_file(
            arquivo_corredor
        )

        if corredor.empty:

            print(
                "[WARNING] "
                "Corredor vazio."
            )

            continue

        # ==========================
        # INTERSEÇÃO ESPACIAL
        # ==========================

        acidentes_br = gpd.sjoin(
            gdf_acidentes,
            corredor,
            predicate="within",
            how="inner"
        )

        # remove colunas auxiliares
        if "index_right" in acidentes_br.columns:

            acidentes_br = (
                acidentes_br.drop(
                    columns=["index_right"]
                )
            )

        # ==========================
        # EXPORTAÇÃO
        # ==========================

        acidentes_br.to_file(
            output_geojson,
            driver="GeoJSON"
        )

        print(
            f"[INFO] Acidentes encontrados: "
            f"{len(acidentes_br)}"
        )

    print(
        "\n[INFO] Processo concluído."
    )


if __name__ == "__main__":

    main()
