import os

import geopandas as gpd
import folium

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

OUTPUT_DIR = (
    "output/hotspots"
)

BASE_CARTOGRAFICA = (
    "datasets/base_cartografica"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ==============================
# CORES HOTSPOTS
# ==============================

def cor_hotspot(score):

    if score >= 5000:
        return "darkred"

    elif score >= 2000:
        return "red"

    elif score >= 1000:
        return "orange"

    elif score >= 500:
        return "yellow"

    return "green"


# ==============================
# REMOVE DATETIME
# ==============================

def sanitizar_gdf(gdf):

    for col in gdf.columns:

        try:

            if str(gdf[col].dtype).startswith(
                "datetime"
            ):

                gdf[col] = (
                    gdf[col]
                    .astype(str)
                )

        except Exception:
            pass

    return gdf


# ==============================
# MAIN
# ==============================

def main():

    print(
        "\n[INFO] Gerando "
        "mapas de hotspots...\n"
    )

    for br in BRS:

        print(f"\n[INFO] {br}")

        pasta_br = os.path.join(
            BASE_DIR,
            br
        )

        arquivo_hotspots = os.path.join(
            pasta_br,
            "acidentes",
            "hotspots.geojson"
        )

        arquivo_rodovia = os.path.join(
            pasta_br,
            "rodovia",
            "br.geojson"
        )

        output = os.path.join(
            OUTPUT_DIR,
            f"{br}_hotspots.html"
        )

        # ==========================
        # VALIDA HOTSPOTS
        # ==========================

        if not os.path.exists(
            arquivo_hotspots
        ):

            print(
                "[WARNING] "
                "Hotspots não encontrados."
            )

            continue

        # ==========================
        # CARREGA HOTSPOTS
        # ==========================

        gdf = gpd.read_file(
            arquivo_hotspots
        )

        if gdf.empty:

            print(
                "[WARNING] "
                "GeoDataFrame vazio."
            )

            continue

        gdf = sanitizar_gdf(gdf)

        gdf = gdf.to_crs(
            epsg=4326
        )

        # ==========================
        # CENTRO MAPA
        # ==========================

        centro = [

            gdf.geometry.y.mean(),
            gdf.geometry.x.mean()
        ]

        # ==========================
        # MAPA
        # ==========================

        mapa = folium.Map(

            location=centro,

            zoom_start=7,

            tiles="CartoDB Voyager"
        )

        # ==========================
        # ESTADOS
        # ==========================

        arquivo_estados = os.path.join(
            BASE_CARTOGRAFICA,
            "estados_nordeste.geojson"
        )

        if os.path.exists(
            arquivo_estados
        ):

            estados = gpd.read_file(
                arquivo_estados
            )

            estados = sanitizar_gdf(
                estados
            )

            estados = estados.to_crs(
                epsg=4326
            )

            folium.GeoJson(

                estados,

                name="Estados",

                style_function=lambda x: {

                    "color": "#666666",
                    "weight": 1,
                    "fillOpacity": 0
                }

            ).add_to(mapa)

            print(
                "[INFO] Estados adicionados."
            )

        # ==========================
        # MUNICÍPIOS
        # ==========================

        arquivo_municipios = os.path.join(
            BASE_CARTOGRAFICA,
            "municipios_nordeste.geojson"
        )

        if os.path.exists(
            arquivo_municipios
        ):

            municipios = gpd.read_file(
                arquivo_municipios
            )

            municipios = sanitizar_gdf(
                municipios
            )

            municipios = municipios.to_crs(
                epsg=4326
            )

            folium.GeoJson(

                municipios,

                name="Municípios",

                style_function=lambda x: {

                    "color": "#bbbbbb",
                    "weight": 0.3,
                    "fillOpacity": 0
                }

            ).add_to(mapa)

            print(
                "[INFO] Municípios adicionados."
            )

        # ==========================
        # RODOVIA
        # ==========================

        if os.path.exists(
            arquivo_rodovia
        ):

            rodovia = gpd.read_file(
                arquivo_rodovia
            )

            rodovia = sanitizar_gdf(
                rodovia
            )

            rodovia = rodovia.to_crs(
                epsg=4326
            )

            folium.GeoJson(

                rodovia,

                name="Rodovia",

                style_function=lambda x: {

                    "color": "#9e9e9e",
                    "weight": 4,
                    "opacity": 0.8
                }

            ).add_to(mapa)

            print(
                "[INFO] Rodovia adicionada."
            )

        # ==========================
        # ACIDENTES
        # ==========================

        for _, row in gdf.iterrows():

            folium.CircleMarker(

                location=[
                    row.geometry.y,
                    row.geometry.x
                ],

                radius=2,

                color="blue",

                fill=True,

                fill_opacity=0.4,

                weight=0

            ).add_to(mapa)

        # ==========================
        # HOTSPOTS
        # ==========================

        hotspots = gdf[
            gdf["hotspot_id"] != -1
        ]

        hotspots_agrupados = (

            hotspots
            .groupby("hotspot_id")
            .agg({

                "hotspot_score":
                    "max",

                "risk_score":
                    "count"
            })
            .reset_index()
        )

        # ==========================
        # CENTRÓIDES HOTSPOTS
        # ==========================

        for hotspot_id in (

            hotspots_agrupados[
                "hotspot_id"
            ]
        ):

            subset = hotspots[

                hotspots[
                    "hotspot_id"
                ] == hotspot_id
            ]

            centroid = (

                subset.geometry
                .union_all()
                .centroid
            )

            hotspot_score = (

                subset[
                    "hotspot_score"
                ].max()
            )

            qtd_acidentes = len(
                subset
            )

            folium.CircleMarker(

                location=[
                    centroid.y,
                    centroid.x
                ],

                radius=8,

                color=cor_hotspot(
                    hotspot_score
                ),

                fill=True,

                fill_opacity=0.85,

                popup=(

                    f"<b>BR:</b> "
                    f"{br}<br>"

                    f"<b>Hotspot:</b> "
                    f"{hotspot_id}<br>"

                    f"<b>Score:</b> "
                    f"{hotspot_score:.2f}<br>"

                    f"<b>Acidentes:</b> "
                    f"{qtd_acidentes}<br>"

                    f"<b>Criticidade:</b> "
                    f"{cor_hotspot(hotspot_score)}"
                )

            ).add_to(mapa)

        # ==========================
        # CONTROLE CAMADAS
        # ==========================

        folium.LayerControl().add_to(
            mapa
        )

        # ==========================
        # EXPORTAÇÃO
        # ==========================

        mapa.save(output)

        print(
            f"[INFO] Mapa exportado: "
            f"{output}"
        )

    print(
        "\n[INFO] Processo concluído."
    )


if __name__ == "__main__":

    main()
