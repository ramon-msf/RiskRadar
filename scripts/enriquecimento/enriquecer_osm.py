import pandas as pd
import requests
import time


# ==============================
# CONFIGURAÇÕES
# ==============================

INPUT_FILE = "../../datasets/processed/acidentes_2025_processado.csv"

OUTPUT_FILE = "../../datasets/processed/acidentes_2025_enriquecido.csv"

LIMIT_ACIDENTES = 100

RAIO_BUSCA = 300

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


# ==============================
# CONSULTA OSM
# ==============================

def consultar_osm(lat, lon):

    query = f"""
    [out:json][timeout:25];

    (
      node(around:{RAIO_BUSCA},{lat},{lon})["highway"="traffic_signals"];
      node(around:{RAIO_BUSCA},{lat},{lon})["highway"="speed_camera"];
      node(around:{RAIO_BUSCA},{lat},{lon})["highway"="bus_stop"];
      node(around:{RAIO_BUSCA},{lat},{lon})["traffic_calming"];
    );

    out body;
    """

    headers = {
        "User-Agent": "RiskRadar/1.0"
    }

    try:

        response = requests.post(
            OVERPASS_URL,
            data=query,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        elementos = data.get("elements", [])

        tipos = {}

        for el in elementos:

            tags = el.get("tags", {})

            tipo = (
                tags.get("highway")
                or tags.get("traffic_calming")
                or "outro"
            )

            tipos[tipo] = tipos.get(tipo, 0) + 1

        return {
            "total_elementos": len(elementos),
            "tipos": tipos
        }

    except Exception as e:

        print(f"[ERRO OSM] {e}")

        return {
            "total_elementos": 0,
            "tipos": {}
        }


# ==============================
# MAIN
# ==============================

def main():

    print("[INFO] Carregando dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"[INFO] Total de acidentes: {len(df)}")

    # limitar amostra
    df = df.head(LIMIT_ACIDENTES)

    print(f"[INFO] Amostra utilizada: {len(df)}")

    resultados = []

    for index, row in df.iterrows():

        acidente_id = row["id"]

        lat = row["latitude"]
        lon = row["longitude"]

        print(
            f"\n[INFO] Processando acidente {acidente_id}"
        )

        enriquecimento = consultar_osm(lat, lon)

        print(
            f"[INFO] Elementos encontrados: "
            f"{enriquecimento['total_elementos']}"
        )

        resultado = row.to_dict()

        resultado["osm_total_elementos"] = (
            enriquecimento["total_elementos"]
        )

        resultado["osm_tipos"] = str(
            enriquecimento["tipos"]
        )

        resultados.append(resultado)

        # evitar sobrecarga
        time.sleep(1)

    # salvar
    df_saida = pd.DataFrame(resultados)

    df_saida.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n[INFO] Enriquecimento concluído.")

    print(f"[INFO] Arquivo salvo: {OUTPUT_FILE}")


if __name__ == "__main__":

    main()
