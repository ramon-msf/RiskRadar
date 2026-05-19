import os

import geopandas as gpd
import folium

from folium.plugins import (
    HeatMap,
    Fullscreen
)

from config.rodovias import (
    REGIAO,
    BRS
)


# =========================================================
# CONFIGURAÇÕES
# =========================================================

BASE_DIR = (
    f"datasets/processed/regioes/{REGIAO}"
)

BASE_CARTOGRAFICA = (
    "datasets/base_cartografica"
)

OUTPUT_DIR = (
    "output/hotspots"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# =========================================================
# CORES HOTSPOTS
# =========================================================

def cor_hotspot(score):

    if score >= 5000:
        return "#7f0000"

    elif score >= 2000:
        return "#d7301f"

    elif score >= 1000:
        return "#fc8d59"

    elif score >= 500:
        return "#fdcc8a"

    return "#31a354"


# =========================================================
# SANITIZAÇÃO
# =========================================================

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


# =========================================================
# GARANTE COLUNAS
# =========================================================

def garantir_colunas(gdf):

    colunas = [

        "mortos",
        "feridos_graves",
        "feridos_leves",
        "ilesos",
        "causa_acidente",
        "tipo_acidente"
    ]

    for col in colunas:

        if col not in gdf.columns:

            if col in [

                "causa_acidente",
                "tipo_acidente"
            ]:

                gdf[col] = (
                    "Não informado"
                )

            else:

                gdf[col] = 0

    return gdf


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n[INFO] Gerando "
        "mapas analíticos...\n"
    )

    # =====================================================
    # BASE CARTOGRÁFICA
    # =====================================================

    arquivo_estados = os.path.join(
        BASE_CARTOGRAFICA,
        "estados_nordeste.geojson"
    )

    arquivo_municipios = os.path.join(
        BASE_CARTOGRAFICA,
        "municipios_nordeste.geojson"
    )

    estados = None
    municipios = None

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

    # =====================================================
    # LOOP BRs
    # =====================================================

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

        # =================================================
        # HOTSPOTS
        # =================================================

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

            print(
                "[WARNING] "
                "GeoDataFrame vazio."
            )

            continue

        gdf = sanitizar_gdf(
            gdf
        )

        gdf = garantir_colunas(
            gdf
        )

        gdf = gdf.to_crs(
            epsg=4326
        )

        # =================================================
        # CENTRO
        # =================================================

        centro = [

            gdf.geometry.y.mean(),
            gdf.geometry.x.mean()
        ]

        # =================================================
        # MAPA
        # =================================================

        mapa = folium.Map(

            location=centro,

            zoom_start=7,

            tiles="CartoDB Positron",

            prefer_canvas=True
        )

        Fullscreen().add_to(
            mapa
        )

        # =================================================
        # FEATURE GROUPS
        # =================================================

        fg_estados = folium.FeatureGroup(
            name="Estados",
            show=True
        )

        fg_municipios = folium.FeatureGroup(
            name="Municípios",
            show=False
        )

        fg_rodovia = folium.FeatureGroup(
            name="Rodovia",
            show=True
        )

        fg_heatmap = folium.FeatureGroup(
            name="HeatMap",
            show=True
        )

        fg_acidentes = folium.FeatureGroup(
            name="Acidentes Históricos",
            show=False
        )

        fg_hotspots = folium.FeatureGroup(
            name="Hotspots",
            show=True
        )

        # =================================================
        # ESTADOS
        # =================================================

        if estados is not None:

            folium.GeoJson(

                estados,

                style_function=lambda x: {

                    "color": "#777777",
                    "weight": 1,
                    "fillOpacity": 0
                }

            ).add_to(
                fg_estados
            )

        # =================================================
        # MUNICÍPIOS
        # =================================================

        if municipios is not None:

            folium.GeoJson(

                municipios,

                style_function=lambda x: {

                    "color": "#cccccc",
                    "weight": 0.2,
                    "fillOpacity": 0
                }

            ).add_to(
                fg_municipios
            )

        # =================================================
        # RODOVIA
        # =================================================

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

            try:

                rodovia_geom = (
                    rodovia.geometry
                    .union_all()
                )

            except Exception:

                rodovia_geom = (
                    rodovia.geometry
                    .unary_union
                )

            rodovia_gdf = gpd.GeoDataFrame(

                geometry=[rodovia_geom],

                crs="EPSG:4326"
            )

            folium.GeoJson(

                rodovia_gdf,

                style_function=lambda x: {

                    "color": "#6f6f6f",
                    "weight": 5,
                    "opacity": 0.9
                }

            ).add_to(
                fg_rodovia
            )

        # =================================================
        # HEATMAP
        # =================================================

        heat_data = [

            [
                row.geometry.y,
                row.geometry.x,
                1
            ]

            for _, row in gdf.iterrows()
        ]

        HeatMap(

            heat_data,

            radius=13,

            blur=18,

            min_opacity=0.25

        ).add_to(
            fg_heatmap
        )

        # =================================================
        # ACIDENTES HISTÓRICOS
        # =================================================

        amostra = gdf.sample(

            min(
                2500,
                len(gdf)
            ),

            random_state=42
        )

        for _, row in amostra.iterrows():

            folium.CircleMarker(

                location=[
                    row.geometry.y,
                    row.geometry.x
                ],

                radius=2,

                color="#2b8cbe",

                fill=True,

                fill_opacity=0.35,

                weight=0

            ).add_to(
                fg_acidentes
            )

        # =================================================
        # HOTSPOTS
        # =================================================

        hotspots = gdf[
            gdf["hotspot_id"] != -1
        ]

        hotspots_agrupados = (

            hotspots
            .groupby("hotspot_id")
            .agg({

                "hotspot_score": "max",

                "risk_score": "mean",

                "mortos": "sum",

                "feridos_graves": "sum",

                "feridos_leves": "sum",

                "ilesos": "sum",

                "id": "count"
            })
            .rename(columns={

                "id": "qtd_acidentes"
            })
            .reset_index()
        )

        # =================================================
        # HOTSPOTS VISUAIS
        # =================================================

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

            try:

                hotspot_geom = (
                    subset.geometry
                    .union_all()
                )

            except Exception:

                hotspot_geom = (
                    subset.geometry
                    .unary_union
                )

            centroid = (
                hotspot_geom.centroid
            )

            hotspot_info = (

                hotspots_agrupados[

                    hotspots_agrupados[
                        "hotspot_id"
                    ] == hotspot_id

                ].iloc[0]
            )

            hotspot_score = float(
                hotspot_info[
                    "hotspot_score"
                ]
            )

            qtd_acidentes = int(
                hotspot_info[
                    "qtd_acidentes"
                ]
            )

            mortos = int(
                hotspot_info[
                    "mortos"
                ]
            )

            feridos_graves = int(
                hotspot_info[
                    "feridos_graves"
                ]
            )

            feridos_leves = int(
                hotspot_info[
                    "feridos_leves"
                ]
            )

            total_vitimas = (

                mortos
                + feridos_graves
                + feridos_leves
            )

            # =============================================
            # CAUSA
            # =============================================

            try:

                causa = (

                    subset[
                        "causa_acidente"
                    ]
                    .mode()
                    .iloc[0]
                )

            except Exception:

                causa = (
                    "Não informado"
                )

            # =============================================
            # TIPO
            # =============================================

            try:

                tipo = (

                    subset[
                        "tipo_acidente"
                    ]
                    .mode()
                    .iloc[0]
                )

            except Exception:

                tipo = (
                    "Não informado"
                )

            # =============================================
            # CLASSIFICAÇÃO
            # =============================================

            if mortos >= 10:

                classificacao = (
                    "Crítico"
                )

            elif mortos >= 5:

                classificacao = (
                    "Severo"
                )

            elif qtd_acidentes >= 50:

                classificacao = (
                    "Recorrente"
                )

            else:

                classificacao = (
                    "Moderado"
                )

            # =============================================
            # HOTSPOT MARKER
            # =============================================

            folium.CircleMarker(

                location=[
                    centroid.y,
                    centroid.x
                ],

                radius=max(
                    6,
                    min(
                        qtd_acidentes / 12,
                        20
                    )
                ),

                color=cor_hotspot(
                    hotspot_score
                ),

                fill=True,

                fill_color=cor_hotspot(
                    hotspot_score
                ),

                fill_opacity=0.85,

                weight=2,

                popup=(

                    f"<h4>{br}</h4>"

                    f"<b>Hotspot:</b> "
                    f"{hotspot_id}<br>"

                    f"<b>Classificação:</b> "
                    f"{classificacao}<br><br>"

                    f"<b>Acidentes:</b> "
                    f"{qtd_acidentes}<br>"

                    f"<b>Mortos:</b> "
                    f"{mortos}<br>"

                    f"<b>Feridos graves:</b> "
                    f"{feridos_graves}<br>"

                    f"<b>Feridos leves:</b> "
                    f"{feridos_leves}<br>"

                    f"<b>Total vítimas:</b> "
                    f"{total_vitimas}<br><br>"

                    f"<b>Causa predominante:</b><br>"
                    f"{causa}<br><br>"

                    f"<b>Tipo predominante:</b><br>"
                    f"{tipo}<br><br>"

                    f"<b>Score espacial:</b> "
                    f"{hotspot_score:.2f}"
                )

            ).add_to(
                fg_hotspots
            )

        # =================================================
        # CAMADAS
        # =================================================

        fg_estados.add_to(
            mapa
        )

        fg_municipios.add_to(
            mapa
        )

        fg_rodovia.add_to(
            mapa
        )

        fg_heatmap.add_to(
            mapa
        )

        fg_acidentes.add_to(
            mapa
        )

        fg_hotspots.add_to(
            mapa
        )

        folium.LayerControl(
            collapsed=False
        ).add_to(
            mapa
        )

        # =================================================
        # EXPORTAÇÃO
        # =================================================

        mapa.save(
            output
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
