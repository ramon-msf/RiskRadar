import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# ==============================
# CONFIGURAÇÕES
# ==============================

ARQUIVO_BRS = "../../datasets/osm/brs_filtradas.geojson"

ARQUIVO_ACIDENTES = (
    "../../datasets/processed/"
    "acidentes_2025_processado.csv"
)

OUTPUT_FILE = (
    "../../datasets/processed/"
    "acidentes_br101.geojson"
)

# distância do corredor
BUFFER_METROS = 500


# ==============================
# MAIN
# ==============================

def main():

    print("[INFO] Carregando BRs...")

    gdf_brs = gpd.read_file(
        ARQUIVO_BRS
    )

    print(
        f"[INFO] Rodovias carregadas: "
        f"{len(gdf_brs)}"
    )

    # ==========================
    # CRS MÉTRICO
    # ==========================

    print("[INFO] Convertendo CRS...")

    gdf_brs = gdf_brs.to_crs(
        epsg=3857
    )

    # ==========================
    # BUFFER
    # ==========================

    print(
        f"[INFO] Criando buffer "
        f"de {BUFFER_METROS} metros..."
    )

    buffer_brs = gdf_brs.buffer(
        BUFFER_METROS
    )

    gdf_buffer = gpd.GeoDataFrame(
        geometry=buffer_brs,
        crs=gdf_brs.crs
    )

    # ==========================
    # ACIDENTES
    # ==========================

    print("[INFO] Carregando acidentes...")

    df = pd.read_csv(
        ARQUIVO_ACIDENTES
    )

    print(
        f"[INFO] Total acidentes: "
        f"{len(df)}"
    )

    # remover coordenadas inválidas
    df = df.dropna(
        subset=["latitude", "longitude"]
    )

    # geometria
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

    # converter para métrico
    gdf_acidentes = gdf_acidentes.to_crs(
        epsg=3857
    )

    # ==========================
    # INTERSEÇÃO ESPACIAL
    # ==========================

    print(
        "[INFO] Filtrando acidentes "
        "próximos da BR..."
    )

    acidentes_filtrados = gpd.sjoin(
        gdf_acidentes,
        gdf_buffer,
        predicate="intersects",
        how="inner"
    )

    print(
        f"[INFO] Acidentes próximos "
        f"da BR: {len(acidentes_filtrados)}"
    )

    # ==========================
    # EXPORTAÇÃO
    # ==========================

    acidentes_filtrados.to_file(
        OUTPUT_FILE,
        driver="GeoJSON"
    )

    print(
        f"[INFO] Arquivo salvo: "
        f"{OUTPUT_FILE}"
    )

    print("\n[INFO] Processo concluído.")


if __name__ == "__main__":

    main()
