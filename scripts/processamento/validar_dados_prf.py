import os
import glob
import pandas as pd


# ==============================
# CONFIGURAÇÕES
# ==============================

DATASET_DIR = "../../datasets/processed"


# ==============================
# VALIDAÇÃO
# ==============================

def validar_arquivo(csv_path):

    print("\n================================================")
    print(f"[INFO] Validando arquivo: {csv_path}")
    print("================================================")

    try:

        df = pd.read_csv(
            csv_path,
            low_memory=False
        )

        total = len(df)

        print(f"\n[INFO] Total de acidentes: {total}")

        # ==========================================
        # VALORES NULOS
        # ==========================================

        print("\n[VALIDAÇÃO] Valores nulos:")

        colunas_criticas = [
            "id",
            "municipio",
            "latitude",
            "longitude",
            "br",
            "tipo_acidente",
            "classificacao_acidente"
        ]

        for coluna in colunas_criticas:

            if coluna in df.columns:

                nulos = df[coluna].isnull().sum()

                percentual = (nulos / total) * 100

                print(
                    f" - {coluna}: "
                    f"{nulos} nulos "
                    f"({percentual:.2f}%)"
                )

        # ==========================================
        # COORDENADAS INVÁLIDAS
        # ==========================================

        print("\n[VALIDAÇÃO] Coordenadas inválidas:")

        lat_invalidas = df[
            (df["latitude"] < -35) |
            (df["latitude"] > 10)
        ]

        lon_invalidas = df[
            (df["longitude"] < -80) |
            (df["longitude"] > -20)
        ]

        print(
            f" - Latitude inválida: "
            f"{len(lat_invalidas)}"
        )

        print(
            f" - Longitude inválida: "
            f"{len(lon_invalidas)}"
        )

        # ==========================================
        # DUPLICIDADE
        # ==========================================

        print("\n[VALIDAÇÃO] Duplicidade:")

        duplicados = df["id"].duplicated().sum()

        print(f" - IDs duplicados: {duplicados}")

        # ==========================================
        # DISTRIBUIÇÃO BÁSICA
        # ==========================================

        print("\n[VALIDAÇÃO] Distribuições:")

        if "uf" in df.columns:

            print("\nUFs mais frequentes:")

            print(
                df["uf"]
                .value_counts()
                .head(10)
            )

        if "tipo_acidente" in df.columns:

            print("\nTipos de acidente mais frequentes:")

            print(
                df["tipo_acidente"]
                .value_counts()
                .head(10)
            )

        if "classificacao_acidente" in df.columns:

            print("\nClassificação dos acidentes:")

            print(
                df["classificacao_acidente"]
                .value_counts()
            )

        # ==========================================
        # ESTATÍSTICAS DE VÍTIMAS
        # ==========================================

        print("\n[VALIDAÇÃO] Estatísticas de vítimas:")

        for coluna in [
            "feridos_leves",
            "feridos_graves",
            "mortos"
        ]:

            if coluna in df.columns:

                total_coluna = df[coluna].sum()

                media = df[coluna].mean()

                print(
                    f" - {coluna}: "
                    f"total={total_coluna} | "
                    f"média={media:.2f}"
                )

        print("\n[INFO] Validação concluída.")

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

        validar_arquivo(arquivo)


if __name__ == "__main__":

    main()
