import os

import geopandas as gpd


# ==============================
# CONFIGURAÇÕES
# ==============================

BASE_DIR = (
    "datasets/base_cartografica"
)

ESTADOS_SHP = os.path.join(
    BASE_DIR,
    "BR_UF_2025.shp"
)

MUNICIPIOS_SHP = os.path.join(
    BASE_DIR,
    "BR_Municipios_2025.shp"
)

OUTPUT_ESTADOS = os.path.join(
    BASE_DIR,
    "estados_nordeste.geojson"
)

OUTPUT_MUNICIPIOS = os.path.join(
    BASE_DIR,
    "municipios_nordeste.geojson"
)


# ==============================
# ESTADOS NORDESTE
# ==============================

NORDESTE = [

    "MA",
    "PI",
    "CE",
    "RN",
    "PB",
    "PE",
    "AL",
    "SE",
    "BA"
]


# ==============================
# MAIN
# ==============================

def main():

    print(
        "\n[INFO] Preparando "
        "base cartográfica...\n"
    )

    # ==========================
    # ESTADOS
    # ==========================

    print(
        "[INFO] Carregando estados..."
    )

    estados = gpd.read_file(
        ESTADOS_SHP
    )

    print(
        f"[INFO] Estados carregados: "
        f"{len(estados)}"
    )

    # tenta identificar coluna UF
    colunas = estados.columns.tolist()

    print(
        f"[INFO] Colunas estados: "
        f"{colunas}"
    )

    coluna_uf = None

    for c in colunas:

        if c.upper() in [

            "SIGLA_UF",
            "UF",
            "SIGLA"
        ]:

            coluna_uf = c
            break

    if coluna_uf is None:

        raise Exception(
            "Coluna UF não encontrada."
        )

    estados_ne = estados[

        estados[coluna_uf]
        .isin(NORDESTE)
    ]

    # simplificação leve
    estados_ne["geometry"] = (

        estados_ne.geometry
        .simplify(
            tolerance=0.01,
            preserve_topology=True
        )
    )

    estados_ne.to_file(
        OUTPUT_ESTADOS,
        driver="GeoJSON"
    )

    print(
        f"[INFO] Exportado: "
        f"{OUTPUT_ESTADOS}"
    )

    # ==========================
    # MUNICÍPIOS
    # ==========================

    print(
        "\n[INFO] Carregando municípios..."
    )

    municipios = gpd.read_file(
        MUNICIPIOS_SHP
    )

    print(
        f"[INFO] Municípios carregados: "
        f"{len(municipios)}"
    )

    colunas = municipios.columns.tolist()

    print(
        f"[INFO] Colunas municípios: "
        f"{colunas}"
    )

    coluna_uf = None

    for c in colunas:

        if c.upper() in [

            "SIGLA_UF",
            "UF",
            "SIGLA"
        ]:

            coluna_uf = c
            break

    if coluna_uf is None:

        raise Exception(
            "Coluna UF não encontrada."
        )

    municipios_ne = municipios[

        municipios[coluna_uf]
        .isin(NORDESTE)
    ]

    # simplificação mais agressiva
    municipios_ne["geometry"] = (

        municipios_ne.geometry
        .simplify(
            tolerance=0.005,
            preserve_topology=True
        )
    )

    municipios_ne.to_file(
        OUTPUT_MUNICIPIOS,
        driver="GeoJSON"
    )

    print(
        f"[INFO] Exportado: "
        f"{OUTPUT_MUNICIPIOS}"
    )

    print(
        "\n[INFO] Processo concluído."
    )


if __name__ == "__main__":

    main()
