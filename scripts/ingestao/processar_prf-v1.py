import os
import glob
import pandas as pd
import unicodedata


# ==============================
# CONFIGURAÇÕES
# ==============================

DATASET_DIR = "../../datasets/raw"
OUTPUT_DIR = "../../datasets/processed"


# ==============================
# NORMALIZAÇÃO
# ==============================

def normalizar_texto(texto):
    if pd.isna(texto):
        return texto

    texto = str(texto).lower()

    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    )


# ==============================
# PROCESSAMENTO
# ==============================

def processar_arquivo(csv_path):

    print(f"\n[INFO] Processando: {csv_path}")

    try:

        # leitura
        df = pd.read_csv(
            csv_path,
            sep=';',
            encoding='latin1',
            low_memory=False
        )

        print(f"[INFO] Registros carregados: {len(df)}")

        # normalização de cidade
        if "municipio" in df.columns:
            df["municipio"] = df["municipio"].apply(normalizar_texto)

        # coordenadas
        if "latitude" in df.columns:
            df["latitude"] = (
                df["latitude"]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .astype("float32")
            )

        if "longitude" in df.columns:
            df["longitude"] = (
                df["longitude"]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .astype("float32")
            )

        # agregação por acidente
        df_grouped = df.groupby("id").agg({
            "data_inversa": "first",
            "dia_semana": "first",
            "horario": "first",
            "uf": "first",
            "br": "first",
            "km": "first",
            "municipio": "first",
            "latitude": "first",
            "longitude": "first",
            "feridos_leves": "sum",
            "feridos_graves": "sum",
            "mortos": "sum",
            "classificacao_acidente": "first",
            "causa_acidente": "first",
            "tipo_acidente": "first"
        }).reset_index()

        print(f"[INFO] Acidentes únicos: {len(df_grouped)}")

        # nome do arquivo de saída
        nome_arquivo = os.path.basename(csv_path)

        ano = ''.join(filter(str.isdigit, nome_arquivo))

        output_file = (
            f"{OUTPUT_DIR}/acidentes_{ano}_processado.csv"
        )

        # salvar
        df_grouped.to_csv(
            output_file,
            index=False
        )

        print(f"[INFO] Arquivo salvo: {output_file}")

    except Exception as e:
        print(f"[ERRO] {e}")


# ==============================
# MAIN
# ==============================

def main():

    arquivos_csv = glob.glob(
        f"{DATASET_DIR}/*.csv"
    )

    print(f"[INFO] Arquivos encontrados: {len(arquivos_csv)}")

    for arquivo in arquivos_csv:
        processar_arquivo(arquivo)


if __name__ == "__main__":
    main()
