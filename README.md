# RiskRadar

Plataforma Analítica Espacial para Identificação de Hotspots de Acidentes em Rodovias Federais Brasileiras.

---

# Visão Geral

O RiskRadar é uma plataforma de análise espacial voltada para identificação, visualização e análise operacional de hotspots de acidentes rodoviários em rodovias federais brasileiras.

O projeto integra:

- dados históricos da Polícia Rodoviária Federal (PRF)
- infraestrutura rodoviária derivada do OpenStreetMap (OSM)
- análise espacial georreferenciada
- clustering espacial
- visualização interativa baseada em GIS web

A plataforma foi inicialmente estruturada para análise da região Nordeste do Brasil, mas sua arquitetura foi projetada para futura expansão nacional.

---

# Objetivos

- identificar hotspots críticos de acidentes
- analisar recorrência espacial
- avaliar severidade operacional
- enriquecer acidentes com infraestrutura rodoviária
- fornecer visualização geoespacial interativa
- apoiar estudos de segurança viária

---

# Funcionalidades

## Processamento espacial

- consolidação multianual PRF
- extração de corredores rodoviários
- enriquecimento geoespacial
- clustering DBSCAN
- cálculo de hotspots

---

## Infraestrutura OSM

Extração offline de:

- traffic signals
- crossings
- speed cameras
- traffic calming

---

## Visualização analítica

- mapas interativos Folium
- heatmaps
- hotspots operacionais
- camadas ativáveis
- cartografia regional
- portal navegável

---

# Estrutura do Projeto

```text
RiskRadar/
├── config/
├── datasets/
├── output/
├── scripts/
├── README.md
├── requirements.txt
└── .gitignore
