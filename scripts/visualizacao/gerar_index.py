import json
import os


# =====================================================
# CONFIGURAÇÕES
# =====================================================

MANIFESTO = (
    "output/manifest.json"
)

OUTPUT_HTML = (
    "output/index.html"
)


# =====================================================
# CORES CRITICIDADE
# =====================================================

def cor_criticidade(valor):

    cores = {

        "Crítico": "#b30000",

        "Severo": "#e34a33",

        "Recorrente": "#fc8d59",

        "Moderado": "#31a354"
    }

    return cores.get(
        valor,
        "#666666"
    )


# =====================================================
# MAIN
# =====================================================

def main():

    print(
        "\n[INFO] Gerando "
        "portal RiskRadar...\n"
    )

    # ================================================
    # CARREGA MANIFESTO
    # ================================================

    with open(

        MANIFESTO,

        "r",

        encoding="utf-8"

    ) as f:

        dados = json.load(f)

    # ================================================
    # ORDENA BRs
    # ================================================

    dados = sorted(

        dados,

        key=lambda x: x["br"]
    )

    # ================================================
    # CARDS
    # ================================================

    cards = ""

    for item in dados:

        cor = cor_criticidade(
            item["criticidade"]
        )

        card = f"""

        <div class="card">

            <div class="topo">

                <h2>{item['br']}</h2>

                <span
                    class="badge"
                    style="background:{cor};"
                >
                    {item['criticidade']}
                </span>

            </div>

            <div class="conteudo">

                <p>
                    <b>Hotspots:</b>
                    {item['hotspots']}
                </p>

                <p>
                    <b>Acidentes:</b>
                    {item['acidentes']}
                </p>

                <p>
                    <b>Mortos:</b>
                    {item['mortos']}
                </p>

            </div>

            <a
                href="{item['mapa']}"
                target="_blank"
                class="botao"
            >
                Abrir mapa
            </a>

        </div>
        """

        cards += card

    # ================================================
    # HTML
    # ================================================

    html = f"""
<!DOCTYPE html>

<html lang="pt-br">

<head>

<meta charset="UTF-8">

<title>RiskRadar</title>

<style>

body {{

    margin:0;
    padding:0;

    background:#f4f4f4;

    font-family:Arial;
}}

header {{

    background:#1f2937;

    color:white;

    padding:25px;
}}

header h1 {{

    margin:0;
}}

header p {{

    margin-top:8px;

    color:#d1d5db;
}}

.container {{

    padding:20px;
}}

#busca {{

    width:100%;

    padding:14px;

    border-radius:8px;

    border:1px solid #ccc;

    margin-bottom:25px;

    font-size:16px;
}}

.grid {{

    display:grid;

    grid-template-columns:
        repeat(auto-fit,minmax(320px,1fr));

    gap:20px;
}}

.card {{

    background:white;

    border-radius:12px;

    padding:20px;

    box-shadow:
        0 2px 8px rgba(0,0,0,0.08);

    transition:0.2s;
}}

.card:hover {{

    transform:translateY(-3px);
}}

.topo {{

    display:flex;

    justify-content:space-between;

    align-items:center;
}}

.topo h2 {{

    margin:0;
}}

.badge {{

    color:white;

    padding:6px 12px;

    border-radius:20px;

    font-size:13px;

    font-weight:bold;
}}

.conteudo {{

    margin-top:18px;

    line-height:1.7;
}}

.botao {{

    display:block;

    margin-top:20px;

    text-align:center;

    background:#2563eb;

    color:white;

    text-decoration:none;

    padding:12px;

    border-radius:8px;

    font-weight:bold;
}}

.botao:hover {{

    background:#1d4ed8;
}}

footer {{

    text-align:center;

    padding:30px;

    color:#666;
}}

</style>

</head>

<body>

<header>

    <h1>RiskRadar</h1>

    <p>
        Plataforma Analítica Espacial
        de Criticidade Rodoviária
    </p>

</header>

<div class="container">

    <input
        type="text"
        id="busca"
        placeholder="Pesquisar BR..."
        onkeyup="filtrarCards()"
    >

    <div
        class="grid"
        id="grid"
    >

        {cards}

    </div>

</div>

<footer>

    RiskRadar · Projeto de Pesquisa
    em Análise Espacial Rodoviária

</footer>

<script>

function filtrarCards() {{

    let input = document
        .getElementById("busca");

    let filtro = input.value
        .toUpperCase();

    let cards = document
        .getElementsByClassName("card");

    for (let i = 0;
        i < cards.length;
        i++) {{

        let titulo = cards[i]
            .getElementsByTagName("h2")[0];

        let texto = titulo
            .innerText;

        if (
            texto.toUpperCase()
            .indexOf(filtro) > -1
        ) {{

            cards[i].style.display = "";

        }} else {{

            cards[i].style.display = "none";
        }}
    }}
}}

</script>

</body>

</html>
"""

    # ================================================
    # EXPORTAÇÃO
    # ================================================

    with open(

        OUTPUT_HTML,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(html)

    print(
        f"[INFO] Portal exportado: "
        f"{OUTPUT_HTML}"
    )


if __name__ == "__main__":

    main()
