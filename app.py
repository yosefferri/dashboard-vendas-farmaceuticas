import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(layout="wide")   # <- adicione essa linha aqui

from utils.carregar_dados import carregar_dados

df = carregar_dados()

def carregar_css(caminho_arquivo):
    with open(caminho_arquivo) as f:
        return f.read()

css = carregar_css("style/custom.css")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

mapa_cores_cidade = {
    "Araraquara": "#1f77b4",
    "Bauru": "#2ca02c",
    "Jaú": "#ff7f0e",
    "São Carlos": "#d62728"
}

# 1. Converte a coluna de data para o tipo Datetime do Pandas
df["date"] = pd.to_datetime(df["date"])

# 2. Cria uma coluna temporária em formato Ano-Mês (tipo Period) para ordenação cronológica correta
df["periodo"] = df["date"].dt.to_period("M")

# 3. Pega os períodos únicos e ordena cronologicamente (2025-01, 2025-02, ..., 2025-12)
periodos_ordenados = sorted(df["periodo"].unique())

# 4. Selectbox com exibição formatada (ex: "03/2025")
periodo_selecionado = st.selectbox(
    "Selecione o Mês/Ano",
    options=periodos_ordenados,
    format_func=lambda p: p.strftime("%m/%Y"),  # Exibe 03/2025 para o usuário
)

# 5. Filtra o DataFrame pelo período selecionado
df_filtrado = df[df["periodo"] == periodo_selecionado]

st.title("💊 Dashboard de Vendas Farmacêuticas")
st.caption("Dataset fícticio lendo um .csv")
st.divider()


st.write(f"Mostrando dados de: {periodo_selecionado}")
#st.write(df_filtrado)

# ---------- LINHA 1: Faturamento por dia | Faturamento por tipo de produto ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Faturamento por dia")

    # Agrupa o total de vendas por dia E por cidade
    #vendas_por_dia = df_filtrado.groupby(["date", "city"])["total"].sum().reset_index()
    cidades_disponiveis = df_filtrado["city"].unique().tolist()
    opcoes_filtro = ["Todas"] + cidades_disponiveis

    cidades_selecionadas = st.multiselect(
        "Filtrar por cidade",
        options=opcoes_filtro,
        default=["Todas"]
    )
    if "Todas" in cidades_selecionadas or len(cidades_selecionadas) == 0:
        df_grafico_dia = df_filtrado
    else:
        df_grafico_dia = df_filtrado[df_filtrado["city"].isin(cidades_selecionadas)]

    vendas_por_dia = df_grafico_dia.groupby(["date", "city"])["total"].sum().reset_index()

    fig_dia = px.line(
        vendas_por_dia,
        x="date",
        y="total",
        color="city",
        labels={"date": "Data", "total": "Total", "city": "Cidade"},
        color_discrete_map=mapa_cores_cidade
    )

    fig_dia.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=400,
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#000000"),  # Cor geral de todas as fontes
        xaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo X
            tickfont=dict(color="#000000")  # Cor dos rótulos do eixo X
        ),
        yaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo Y (Nota Média)
            tickfont=dict(color="#000000")  # Cor dos números do eixo Y
        ),
        legend=dict(
            font=dict(color="#000000"),  # Cor do texto da legenda
            title_font=dict(color="#000000")  # Cor do título da legenda (Cidade)
        )
    )
    valor_maximo = vendas_por_dia["total"].max()
    fig_dia.update_yaxes(range=[0, valor_maximo * 1.05], tickprefix="R$ ", tickformat=",.0f")

    st.plotly_chart(fig_dia, use_container_width=True, key="grafico_faturamento_dia", config={"displayModeBar": False})


with col2:
    st.subheader("Faturamento por tipo de produto")

    # Agrupa o total por categoria de produto E por cidade
    vendas_por_produto = df_filtrado.groupby(["product category", "city"])["total"].sum().reset_index()

    fig_produto = px.bar(
        vendas_por_produto,
        x="total",
        y="product category",
        color="city",
        orientation="h",
        labels={
            "total": "Total",
            "product category": "Categoria do Produto",
            "city": "Cidade"
        },
    color_discrete_map = mapa_cores_cidade
    )

    fig_produto.update_layout(
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#000000"),  # Cor geral de todas as fontes
        xaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo X
            tickfont=dict(color="#000000")  # Cor dos rótulos do eixo X
        ),
        yaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo Y (Nota Média)
            tickfont=dict(color="#000000")  # Cor dos números do eixo Y
        ),
        legend=dict(
            font=dict(color="#000000"),  # Cor do texto da legenda
            title_font=dict(color="#000000")  # Cor do título da legenda (Cidade)
        )
    )

    st.plotly_chart(fig_produto, use_container_width=True, key="grafico_faturamento_produto", config={"displayModeBar": False})

    # ---------- LINHA 2: Faturamento por filial | Tipo de pagamento | Avaliação ----------
col_mapa = st.columns(1)[0]

with col_mapa:
    st.subheader("Faturamento por filial")

    # 1. Agrupamento e ordenação por maior faturamento
    #    df_mapa = (
    #   df_filtrado.groupby("city")["total"].sum().reset_index()
    #  )

    # 2. Mapeamento de coordenadas (Araraquara, Bauru, Jaú, São Carlos)
    #  coordenadas_sp = {
    #     'Araraquara': {'lat': -21.7946, 'lon': -48.1766},
    #    'Bauru': {'lat': -22.3145, 'lon': -49.0606},
    #    'Jaú': {'lat': -22.2964, 'lon': -48.5586},
    #    'São Carlos': {'lat': -21.9906, 'lon': -47.8897}
    #}

    faturamento_filial = df_filtrado.groupby("city")["total"].sum().reset_index()
    faturamento_filial = faturamento_filial.sort_values("total", ascending=True)

    fig_comparativo = px.bar(
        faturamento_filial,
        x="total",
        y="city",
        orientation="h",
        color="city",
        text="total",
        labels={"total": "Faturamento (R$)", "city": "Cidade"},
        color_discrete_map=mapa_cores_cidade
    )

    fig_comparativo.update_traces(texttemplate="R$ %{text:,.2f}", textposition="inside")
    fig_comparativo.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#000000'),
        xaxis=dict(
            color='#000000',
            tickfont=dict(color='#000000'),
            title_font=dict(color='#000000')
        ),
        yaxis=dict(
            color='#000000',
            tickfont=dict(color='#000000'),
            title_font=dict(color='#000000')
        )
    )


    # Renderização na coluna/local do primeiro gráfico de baixo
    st.plotly_chart(fig_comparativo, use_container_width=True, key="grafico_faturamento_filial", config={"displayModeBar": False})

col4, col5 = st.columns(2)
with col4:
    st.subheader("Faturamento por tipo de pagamento")

    # Agrupa o total por tipo de pagamento
    vendas_por_pagamento = df_filtrado.groupby("payment")["total"].sum().reset_index()

    fig_pagamento = px.pie(
        vendas_por_pagamento,
        names="payment",
        values="total",
        labels={
            "payment": "Forma de Pagamento",
            "total": "Total"
        }
    )
    fig_pagamento.update_layout(
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#000000"),  # Cor geral de todas as fontes
        xaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo X
            tickfont=dict(color="#000000")  # Cor dos rótulos do eixo X
        ),
        yaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo Y (Nota Média)
            tickfont=dict(color="#000000")  # Cor dos números do eixo Y
        ),
        legend=dict(
            font=dict(color="#000000"),  # Cor do texto da legenda
            title_font=dict(color="#000000")  # Cor do título da legenda (Cidade)
        )
    )
    st.plotly_chart(fig_pagamento, use_container_width=True, key="grafico_faturamento_pagamento", config={"displayModeBar": False})

with col5:
    st.subheader("CSAT")

    # Calcula a média de avaliações (rating) por cidade
    avaliacao_por_cidade = df_filtrado.groupby("city")["rating"].mean().reset_index()

    fig_avaliacao = px.bar(
        avaliacao_por_cidade,
        x="city",
        y="rating",
        color="city",
        labels={"city": "Cidade", "rating": "Nota Média"},
        color_discrete_map=mapa_cores_cidade,
    )
    fig_avaliacao.update_layout(
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#000000"),  # Cor geral de todas as fontes
        xaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo X
            tickfont=dict(color="#000000")  # Cor dos rótulos do eixo X
        ),
        yaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo Y (Nota Média)
            tickfont=dict(color="#000000")  # Cor dos números do eixo Y
        ),
        legend=dict(
            font=dict(color="#000000"),  # Cor do texto da legenda
            title_font=dict(color="#000000")  # Cor do título da legenda (Cidade)
        )
    )

    nota_min = avaliacao_por_cidade["rating"].min()
    nota_max = avaliacao_por_cidade["rating"].max()
    fig_avaliacao.update_yaxes(range=[nota_min - 0.3, nota_max + 0.3])

    st.plotly_chart(fig_avaliacao, use_container_width=True, key="grafico_avaliacao", config={"displayModeBar": False})


col_g1, col_g2 = st.columns(2)

# GRÁFICO 1: TOP 5 LABORATÓRIOS MAIS VENDIDOS
with col_g1:
    st.subheader("Laboratórios mais vendidos")
    top_labs = (
        df_filtrado.groupby("branch")["total"]
        .sum()
        .reset_index()
        .sort_values(by="total", ascending=False)
        .head(5)
    )

    fig_labs = px.bar(
        top_labs,
        x="branch",
        y="total",
        title="<b>Top 5 Laboratórios (Faturamento R$)</b>",
        labels={"branch": "Laboratório / Marca", "total": "Faturamento (R$)"},
        text_auto=".2s",
        color="total",
        color_continuous_scale="Blues",
    )
    fig_labs.update_layout(        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        font=dict(color="#000000"),  # Cor geral de todas as fontes
        xaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo X
            tickfont=dict(color="#000000")  # Cor dos rótulos do eixo X
        ),
        yaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo Y
            tickfont=dict(color="#000000")  # Cor dos números do eixo Y
        ),
        legend=dict(
            font=dict(color="#000000"),  # Cor do texto da legenda
            title_font=dict(color="#000000")  # Cor do título da legenda
        )
    )
    st.plotly_chart(fig_labs, use_container_width=True, key="laboratorios", config={"displayModeBar": False})

# GRÁFICO 2: TOP 10 PRODUTOS MAIS VENDIDOS
with col_g2:
    st.subheader("TOP 5 Produtos mais vendidos no período")
    top_produtos = (
        df_filtrado.groupby("product name")["quantity"]
        .sum()
        .reset_index()
        .sort_values(by="quantity", ascending=True)  # Ascending para o barra horizontal do plotly
        .tail(5)
    )

    fig_prods = px.bar(
        top_produtos,
        x="quantity",
        y="product name",
        orientation="h",
        title="<b>Top 10 Produtos (Unidades Vendidas)</b>",
        labels={"quantity": "Unidades Vendidas", "product name": "Produto"},
        text_auto=True,
        color="quantity",
        color_continuous_scale="Teal",
    )
    fig_prods.update_layout(        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        font=dict(color="#000000"),  # Cor geral de todas as fontes
        xaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo X
            tickfont=dict(color="#000000")  # Cor dos rótulos do eixo X
        ),
        yaxis=dict(
            title_font=dict(color="#000000"),  # Cor do título do eixo Y
            tickfont=dict(color="#000000")  # Cor dos números do eixo Y
        ),
        legend=dict(
            font=dict(color="#000000"),  # Cor do texto da legenda
            title_font=dict(color="#000000")  # Cor do título da legenda
        )
    )
    st.plotly_chart(fig_prods, use_container_width=True, config={"displayModeBar": False})


st.divider()
st.markdown(
    """
    <div style="text-align: center; color: black; font-size: 14px; padding-top: 10px;">
        © 2026 Ferri — Dashboard de vendas de uma rede de drogarias fícticia<br>
        Feito com Python, Streamlit e Plotly · Dados via csv<br>
        Contato: joseferri225@gmail.com · <a href="https://github.com/yosefferri/ClimaTempo" style="color: gray;" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)