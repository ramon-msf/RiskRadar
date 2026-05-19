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

        # ==============================
        # LEITURA
        # ==============================

        df = pd.read_csv(
            csv_path,
            sep=';',
            encoding='latin1',
            low_memory=False
        )

        print(f"[INFO] Registros carregados: {len(df)}")

        # ==============================
        # NORMALIZAÇÃO
        # ==============================

        # município
        if "municipio" in df.columns:

            df["municipio"] = (
                df["municipio"]
                .apply(normalizar_texto)
            )

        # latitude
        if "latitude" in df.columns:

            df["latitude"] = (
                df["latitude"]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .astype("float32")
            )

        # longitude
        if "longitude" in df.columns:

            df["longitude"] = (
                df["longitude"]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .astype("float32")
            )

        # ==============================
        # AGREGAÇÃO
        # ==============================

        campos_agregacao = {

            # identificação temporal
            "data_inversa": "first",
            "dia_semana": "first",
            "horario": "first",

            # localização
            "uf": "first",
            "br": "first",
            "km": "first",
            "municipio": "first",
            "latitude": "first",
            "longitude": "first",

            # vítimas
            "feridos_leves": "sum",
            "feridos_graves": "sum",
            "mortos": "sum",

            # classificação
            "classificacao_acidente": "first",

            # contexto do acidente
            "causa_principal": "first",
            "causa_acidente": "first",
            "tipo_acidente": "first",

            # contexto viário
            "fase_dia": "first",
            "condicao_metereologica": "first",
            "tipo_pista": "first",
            "tracado_via": "first",
            "uso_solo": "first",
            "sentido_via": "first"
        }

        # manter apenas colunas existentes
        campos_existentes = {
            k: v for k, v in campos_agregacao.items()
            if k in df.columns
        }

        # agregação
        df_grouped = (
            df
            .groupby("id")
            .agg(campos_existentes)
            .reset_index()
        )

        print(f"[INFO] Acidentes únicos: {len(df_grouped)}")

        # ==============================
        # SAÍDA
        # ==============================

        nome_arquivo = os.path.basename(csv_path)

        ano = ''.join(
            filter(str.isdigit, nome_arquivo)
        )

        output_file = (
            f"{OUTPUT_DIR}/acidentes_{ano}_processado.csv"
        )

        # salvar
        df_grouped.to_csv(
            output_file,
            index=False
        )

        print(f"[INFO] Arquivo salvo: {output_file}")

        # mostrar colunas finais
        print("\n[INFO] Colunas processadas:")

        for col in df_grouped.columns:
            print(f" - {col}")

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
