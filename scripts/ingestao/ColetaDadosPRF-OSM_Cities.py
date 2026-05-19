import pandas as pd
import requests
import argparse
import unicodedata
import time

# ==============================
# CONFIG
# ==============================

# Caminho do CSV da PRF
ARQUIVO_PRF = "DadosPRF/acidentes.csv"

# Normalizar strings CIDADE
def normalizar(texto):
    if isinstance(texto, str):
        return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").upper()
    return texto

# Definição do RAIO de busca na base OSM
RAIO_BUSCA = 500 # metros

# ==============================
# PRF (CSV)
# ==============================

# Filtrar por cidade
def filtrar_cidade(df, cidade):
    cidade_norm = normalizar(cidade)
    return df[df["municipio"].apply(normalizar) == cidade_norm]

def explorar_prf(cidade):
    print("\n==============================")
    print("DADOS PRF (ACIDENTES)")
    print("==============================")

    try:
        df = pd.read_csv(ARQUIVO_PRF, sep=";", encoding="latin1", low_memory=False)
        #correcao de cordenada (string -> float)
        df["latitude"] = df["latitude"].str.replace(",", ".").astype(float)
        df["longitude"] = df["longitude"].str.replace(",", ".").astype(float)
        df = filtrar_cidade(df, cidade)
    except Exception as e:
        print("[ERRO] Não foi possível carregar CSV:", e)
        return None

    print("\nTotal de registros:", len(df))

    print("\n Colunas principais:")
    print(df.columns.tolist()[:20])

    print("\n Head:")
    print(df.head(5))

    print("\n Resumo:")
    colunas = [
        "municipio",
        "uf",
        "tipo_acidente",
        "causa_acidente",
        "condicao_metereologica"
    ]

    for col in colunas:
        if col in df.columns:
            print(f"\n{col}:")
            print(df[col].value_counts().head())

    return df


# ==============================
# OSM (API)
# ==============================

# Obter coordenadas
def obter_coordenadas(cidade):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": f"{cidade}, Brasil",
        "format": "json",
        "limit": 1
    }

    response = requests.get(url, params=params, headers={"User-Agent": "teste"})
    data = response.json()

    if not data:
        raise ValueError("Cidade não encontrada")

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])

    return lat, lon

#def explorar_osm(lat, lon):

#    return df_osm


# Consultar elementos da via por localização do acidente
def consultar_osm_acidente(lat, lon):
    url = "https://overpass.kumi.systems/api/interpreter"

    query = f"""
    [out:json][timeout:25];
    (
      node["highway"="traffic_signals"](around:{RAIO_BUSCA},{lat},{lon});
      node["highway"="crossing"](around:{RAIO_BUSCA},{lat},{lon});
      node["traffic_calming"](around:{RAIO_BUSCA},{lat},{lon});
      node["highway"="speed_camera"](around:{RAIO_BUSCA},{lat},{lon});
    );
    out;
    """

    try:
        response = requests.post(url, data=query, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("elements", [])
    except:
        return []

# ==============================
# MAIN
# ==============================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True, help="Nome da cidade")

    args = parser.parse_args()
    cidade = args.city

    print(f"\n[INFO] Cidade selecionada: {cidade}")

    # PRF
    df_prf = explorar_prf(cidade)

    # Coordenadas
    lat, lon = obter_coordenadas(cidade)
    print(f"[INFO] Coordenadas: {lat}, {lon}")

    print("\n==============================")
    print(" SUMÁRIO FINAL")
    print("==============================")

    if df_prf is not None:
        print(f"PRF: {len(df_prf)} registros")

    print("\n==============================")
    print("ANÁLISE POR ACIDENTE (AMOSTRA)")
    print("==============================")

    df_grouped = df_prf.groupby("id").agg({
        "latitude": "first",
        "longitude": "first",
        "feridos_leves": "sum",
        "feridos_graves": "sum",
        "mortos": "sum",
        "classificacao_acidente": "first"
    }).reset_index()

    df_sample = df_grouped.head(10)

    for i, row in df_sample.iterrows():
        lat_ac = row["latitude"]
        lon_ac = row["longitude"]

        elementos = consultar_osm_acidente(lat_ac, lon_ac)

        # contagem por tipo
        tipos = {}

        for el in elementos:
            tags = el.get("tags", {})

            if "highway" in tags:
                tipo = tags["highway"]
            elif "traffic_calming" in tags:
                tipo = "traffic_calming"
            else:
                tipo = "outros"

            if tipo in tipos:
                tipos[tipo] += 1
            else:
                tipos[tipo] = 1

        # BLOCO ÚNICO POR ACIDENTE
        print("\n----------------------------------------")
        print(f"Acidente ID: {row['id']}")
        print(f"Localização: ({lat_ac}, {lon_ac})")

        print("\nVítimas:")
        print(f" - Leves: {row['feridos_leves']}")
        print(f" - Graves: {row['feridos_graves']}")
        print(f" - Mortos: {row['mortos']}")
        print(f"Classificação: {row['classificacao_acidente']}")

        print("\nInfraestrutura próxima:")
        print(f"Total de elementos: {len(elementos)}")

        if tipos:
            for tipo, qtd in tipos.items():
                print(f" - {tipo}: {qtd}")
        else:
            print(" - Nenhum elemento encontrado")

        time.sleep(1)

if __name__ == "__main__":
    main()
