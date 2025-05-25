import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from app_dados import carregar_dados_oracle

@st.cache_data
def carregar_dados_ndvi():  # Carregar dados de NDVI via API
    df_ndvi_completo = carregar_dados_oracle("ndvi")
    if df_ndvi_completo.empty:
        return pd.DataFrame()
    if 'data' in df_ndvi_completo.columns:
        df_ndvi_completo['data'] = pd.to_datetime(
            df_ndvi_completo['data'], errors='coerce')
    return df_ndvi_completo


@st.cache_data  # Cache para evitar chamadas repetidas à API
def carregar_dados_produtividade():  # Carregar dados de produtividade via API
    return carregar_dados_oracle("produtividade")

@st.cache_data  # Cache para evitar chamadas repetidas à API
def carregar_dados_meteorologicos():
    return carregar_dados_oracle("meteorologicos")

@st.cache_data  # Cache para evitar chamadas repetidas à API
def carregar_dados_custos():
    return carregar_dados_oracle("custos")

def executar_analise():

    # Carregar todos os datasets
    df_ndvi_completo = carregar_dados_ndvi()
    df_produtividade_completo = carregar_dados_produtividade()
    df_meteorologicos_completo = carregar_dados_meteorologicos()
    df_custos_completo = carregar_dados_custos()

    # Verificar se os dados estão disponíveis
    if df_ndvi_completo.empty or df_produtividade_completo.empty or df_meteorologicos_completo.empty or df_custos_completo.empty:
        return None  # Indica que não há dados suficientes

    # Análise de limpeza dos dados
    def analise_limpeza(df, nome):
        return {
            "Nome": nome,
            "Número de linhas": len(df),
            "Número de colunas": len(df.columns),
            "Número de valores ausentes": df.isnull().sum().sum(),
            "Número de duplicados": df.duplicated().sum()
        }

    # Resultdos da anãlise da limpeza dos datasets
    resultados_limpeza = [
        analise_limpeza(df_ndvi_completo, "NDVI"),
        analise_limpeza(df_produtividade_completo, "Produtividade"),
        analise_limpeza(df_meteorologicos_completo, "Meteorológicos"),
        analise_limpeza(df_custos_completo, "Custos")
    ]

    # Converter os resultados em um DataFrame para exibição
    df_resultados_limpeza = pd.DataFrame(resultados_limpeza)

    # Tratamento e limpeza dos dados (apenas para exibição na análise)
    df_ndvi = df_ndvi_completo.dropna(subset=['ndvi']).copy()
    df_produtividade = df_produtividade_completo.dropna(
        subset=['rendimento_medio']).copy()
    df_meteorologicos = df_meteorologicos_completo.dropna().copy()
    df_custos = df_custos_completo.dropna().copy()

    # Converter a coluna 'data' para 'datetime' em todos os DataFrames, se existir
    dataframes = {
        "NDVI": df_ndvi,
        "Produtividade": df_produtividade,
        "Meteorologicos": df_meteorologicos,
        "Custos": df_custos
    }
    for nome, df in dataframes.items():
        if 'data' in df.columns:
            try:
                df['data'] = pd.to_datetime(df['data'], errors='coerce')
            except (ValueError, TypeError) as e:
                st.error(
                    f"Erro ao converter a coluna 'data' em {nome}: {e}. Verifique o formato da data.")
                return None  # Retorna None em caso de erro

        resultados = {
            "df_resultados_limpeza": df_resultados_limpeza,
            "df_ndvi_completo": df_ndvi_completo,
            "df_produtividade_completo": df_produtividade_completo,
            "df_meteorologicos_completo": df_meteorologicos_completo,
            "df_custos_completo": df_custos_completo,
            "df_ndvi": df_ndvi,
            "df_produtividade": df_produtividade,
            "df_meteorologicos": df_meteorologicos,
            "df_custos": df_custos,
        }

    # Análise do Label
    if not df_ndvi.empty:
        resultados["describe_ndvi"] = df_ndvi['ndvi'].describe().to_frame()
        resultados["fig_hist_ndvi"] = px.histogram(
            df_ndvi, x='ndvi', marginal='box', title='Distribuição do NDVI')

    # Análise das Features
    resultados["colunas_features"] = []
    if not df_produtividade.empty:
        resultados["colunas_features"].append(
            ('rendimento_medio', df_produtividade, 'Produtividade'))
        resultados["describe_produtividade"] = df_produtividade['rendimento_medio'].describe(
        ).to_frame()
        resultados["fig_hist_produtividade"] = px.histogram(
            df_produtividade, x='rendimento_medio', marginal='box', title='Distribuição de Produtividade')

    if not df_meteorologicos.empty:
        print(
            f"Número de linhas em df_meteorologicos após limpeza: {len(df_meteorologicos)}")
        print("Colunas em df_meteorologicos:", df_meteorologicos.columns)
        print("Head do df_meteorologicos antes da análise:",
              df_meteorologicos.head())

        colunas_meteorologicas = [
            'precipitacao', 'pressao_atmosferica', 'temperatura_bulbo_seco']
        for col in colunas_meteorologicas:
            if col in df_meteorologicos.columns:
                resultados["colunas_features"].append(
                    (col, df_meteorologicos, col.capitalize().replace('_', ' ')))
                print(f"Coluna '{col}' adicionada a colunas_features.")
            else:
                print(
                    f"A coluna '{col}' não foi encontrada no DataFrame de meteorológicos.")

        # Dicionário para armazenar as descrições
        resultados["describe_meteorologicos"] = {}
        for col in colunas_meteorologicas:
            if col in df_meteorologicos.columns:
                describe = df_meteorologicos[col].describe().to_frame()
                resultados["describe_" +
                           col.replace('_', ' ').lower()] = describe
                print(
                    f"Descrição de '{col}' calculada e armazenada como 'resultados[describe_{col.replace('_', ' ').lower()}]'.")
            else:
                resultados["describe_meteorologicos"][col] = pd.DataFrame()

        resultados["fig_hist_meteorologicos"] = {}
        for col in colunas_meteorologicas:
            if col in df_meteorologicos.columns:
                fig = px.histogram(
                    df_meteorologicos, x=col, marginal='box', title=f'Distribuição de {col.capitalize().replace('_', ' ')}')
                resultados["fig_hist_" + col.replace('_', ' ').lower()] = fig
                print(
                    f"Histograma de '{col}' calculado e armazenado como 'resultados[fig_hist_{col.replace('_', ' ').lower()}]'.")
            else:
                resultados["fig_hist_meteorologicos"][col] = None
    if not df_custos.empty:
        resultados["colunas_features"].append(('custo', df_custos, 'Custos'))
        resultados["describe_custos"] = df_custos['custo'].describe().to_frame()
        resultados["fig_hist_custos"] = px.histogram(
            df_custos, x='custo', marginal='box', title='Distribuição de Custos')
        resultados["describe_custos"] = df_custos['custo'].describe().to_frame()

    # Análise de Correlação com o NDVI
    if 'ndvi' in df_ndvi and not df_ndvi.empty:
        df_merged = df_ndvi.copy()  # Copia o DataFrame de NDVI
        for col, df, _ in resultados["colunas_features"]:
            if col in df and 'data' in df and 'data' in df_merged:
                df_merged = pd.merge(
                    df_merged, df[['data', col]], on='data', how='inner', suffixes=('', f'_{col}'))

        # Filtrar apenas colunas numéricas para calcular a correlação
        numeric_cols_ndvi = df_merged.select_dtypes(include=np.number).columns
        if 'ndvi' in numeric_cols_ndvi:
            resultados["corr_matrix"] = df_merged[numeric_cols_ndvi].corr()['ndvi'].sort_values(
                ascending=False).to_frame()
            resultados["fig_corr_ndvi_heatmap"] = px.imshow(
                df_merged[numeric_cols_ndvi].corr(), title='Matriz de Correlação com NDVI')
        else:
            resultados["corr_matrix"] = None
            resultados["fig_corr_ndvi_heatmap"] = None
    else:
        resultados["corr_matrix"] = None
        resultados["fig_corr_ndvi_heatmap"] = None

    # Análise de Dispersão entre Features e NDVI
    if 'ndvi' in df_ndvi and not df_ndvi.empty:
        resultados["scatter_plots"] = []
        for col, df, title in resultados["colunas_features"]:
            if col in df and 'data' in df and 'data' in df_ndvi:
                df_scatter = pd.merge(
                    df_ndvi, df[['data', col]], on='data', how='inner')
                if not df_scatter.empty:
                    resultados["scatter_plots"].append({
                        "col": col,
                        "title": title,
                        "fig": px.scatter(df_scatter, x=col, y='ndvi',
                                          title=f'Dispersão entre {title} e NDVI')
                    })
    else:
        resultados["scatter_plots"] = []

    # Análise de Tendências Temporais
    if 'data' in df_ndvi and not df_ndvi.empty:
        resultados["fig_tendencia_ndvi"] = px.line(
            df_ndvi, x='data', y='ndvi', title='Tendência Temporal do NDVI')
        resultados["tendencias_temporais"] = []
        for col, df, title in resultados["colunas_features"]:
            if col in df and 'data' in df:
                resultados["tendencias_temporais"].append({
                    "col": col,
                    "title": title,
                    "fig": px.line(df, x='data', y=col,
                                   title=f'Tendência Temporal de {title}')
                })
    else:
        resultados["fig_tendencia_ndvi"] = None
        resultados["tendencias_temporais"] = []

    # Matriz de Correlação entre Features (incluindo NDVI)
    df_features = pd.DataFrame()
    for col, df, _ in resultados["colunas_features"]:
        if col in df and 'data' in df:
            if df_features.empty:
                df_features = df[['data', col]].copy()
            else:
                df_features = pd.merge(
                    df_features, df[['data', col]], on='data', how='inner', suffixes=('', f'_{col}'))

    # Adicionar a coluna 'ndvi' ao df_features, se existir
    if 'ndvi' in df_ndvi.columns and 'data' in df_ndvi.columns:
        if df_features.empty:
            df_features = df_ndvi[['data', 'ndvi']].copy()
        else:
            df_features = pd.merge(
                df_features, df_ndvi[['data', 'ndvi']], on='data', how='inner')

    if not df_features.empty and df_features.shape[1] > 1:
        # Filtrar apenas colunas numéricas para calcular a correlação
        numeric_cols_features = df_features.select_dtypes(
            include=np.number).columns
        # Recalcular a matriz de correlação incluindo 'ndvi'
        resultados["corr_matrix_features"] = df_features[numeric_cols_features].corr()
        resultados["fig_corr_features_heatmap"] = px.imshow(
            resultados["corr_matrix_features"], title='Matriz de Correlação entre Features (incluindo NDVI)')
    else:
        resultados["corr_matrix_features"] = None
        resultados["fig_corr_features_heatmap"] = None

    return resultados


def analise_exploratoria():

    st.header("🔍 Análise Exploratória")
    st.write("---")

    # lista para obter os resultados pré-calculados, se existirem
    resultados = executar_analise()

    if resultados is None:  # Verifica se os dados estão disponíveis e, se não, exibe uma mensagem de erro
        st.warning("Dados insuficientes para análise.")
        return

    opcoes_exibicao = [
        "Resultados da Limpeza",
        "Dados Completos (Amostra)",
        "Análise da Variável NDVI",
        "Análise das Variáveis Features",
        "Análise de Correlação com o NDVI",
        "Análise de Dispersão entre Features e NDVI",
        "Análise de Tendências Temporais",
        "Matriz de Correlação entre Features (incluindo NDVI)",
        "Download dos Dados"
    ]

    st.write("Selecione o que deseja visualizar:")
    num_colunas = 3  # Número de colunas para exibir os botões
    colunas = st.columns(num_colunas)
    indice_coluna = 0
    selecoes = []

    for opcao in opcoes_exibicao:
        if colunas[indice_coluna].button(opcao, use_container_width=True):
            selecoes.append(opcao)
        indice_coluna = (indice_coluna + 1) % num_colunas

    # Exibir as seções selecionadas
    if "Resultados da Limpeza" in selecoes:
        st.subheader("Resultados da Limpeza de Dados")
        if "df_resultados_limpeza" in resultados:
            st.dataframe(resultados["df_resultados_limpeza"])
        else:
            st.warning("Resultados da limpeza não disponíveis.")

    if "Dados Completos (Amostra)" in selecoes:
        st.subheader("Dados Completos (Amostra)")
        if "df_ndvi_completo" in resultados:
            st.write("Dados de NDVI:")
            st.dataframe(resultados["df_ndvi_completo"].head())
        else:
            st.warning("Dados de NDVI não disponíveis.")
        if "df_produtividade_completo" in resultados:
            st.write("Dados de Produtividade:")
            st.dataframe(resultados["df_produtividade_completo"].head())
        else:
            st.warning("Dados de Produtividade não disponíveis.")
        if "df_meteorologicos_completo" in resultados:
            st.write("Dados Meteorológicos:")
            st.dataframe(resultados["df_meteorologicos_completo"].head())
        else:
            st.warning("Dados Meteorológicos não disponíveis.")
        if "df_custos_completo" in resultados:
            st.write("Dados de Custos:")
            st.dataframe(resultados["df_custos_completo"].head())
        else:
            st.warning("Dados de Custos não disponíveis.")

    if "Análise da Variável NDVI" in selecoes:
        if "describe_ndvi" in resultados and "fig_hist_ndvi" in resultados and resultados["fig_hist_ndvi"] is not None:
            st.subheader("Análise da Variável NDVI")
            st.write(resultados["describe_ndvi"])
            st.plotly_chart(resultados["fig_hist_ndvi"])
        else:
            st.warning("Análise da variável NDVI não disponível.")

    if "Análise das Variáveis Features" in selecoes:
        if "colunas_features" in resultados:
            st.subheader("Análise das Variáveis Features")
            for col, df, title in resultados["colunas_features"]:
                st.write(f"### {title}")
                if f"describe_{title.lower()}" in resultados and resultados[f"describe_{title.lower()}"] is not None and not resultados[f"describe_{title.lower()}"] .empty:
                    st.write(resultados[f"describe_{title.lower()}"])
                else:
                    st.warning(f"Descrição de {title} não disponível.")
                if f"fig_hist_{title.lower()}" in resultados and resultados[f"fig_hist_{title.lower()}"] is not None:
                    if isinstance(resultados[f"fig_hist_{title.lower()}"], dict):
                        for fig in resultados[f"fig_hist_{title.lower()}"]:
                            if resultados[f"fig_hist_{title.lower()}"][fig] is not None:
                                st.plotly_chart(
                                    resultados[f"fig_hist_{title.lower()}"][fig])
                            else:
                                st.warning(
                                    f"Histograma de {title} não disponível.")
                    else:
                        st.plotly_chart(
                            resultados[f"fig_hist_{title.lower()}"])
                else:
                    st.warning(f"Histograma de {title} não disponível.")
        else:
            st.warning("Análise das variáveis features não disponível.")

    if "Análise de Correlação com o NDVI" in selecoes:
        if "corr_matrix" in resultados and "fig_corr_ndvi_heatmap" in resultados and resultados["corr_matrix"] is not None and resultados["fig_corr_ndvi_heatmap"] is not None:
            st.subheader("Análise de Correlação com o NDVI")
            st.write("Correlação com NDVI:")
            st.write(resultados["corr_matrix"])
            st.plotly_chart(resultados["fig_corr_ndvi_heatmap"])
        else:
            st.warning("Análise de correlação com NDVI não disponível.")

    if "Análise de Dispersão entre Features e NDVI" in selecoes:
        if "scatter_plots" in resultados:
            st.subheader("Análise de Dispersão entre Features e NDVI")
            for scatter_plot in resultados["scatter_plots"]:
                if scatter_plot["fig"] is not None:
                    st.plotly_chart(scatter_plot["fig"])
                else:
                    st.warning(
                        f"Gráfico de dispersão para {scatter_plot['title']} não disponível.")
        else:
            st.warning("Análise de dispersão não disponível.")

    if "Análise de Tendências Temporais" in selecoes:
        if "fig_tendencia_ndvi" in resultados and resultados["fig_tendencia_ndvi"] is not None:
            st.subheader("Análise de Tendências Temporais")
            st.plotly_chart(resultados["fig_tendencia_ndvi"])
        else:
            st.warning("Tendência temporal do NDVI não disponível.")
        if "tendencias_temporais" in resultados:
            for tendencia in resultados["tendencias_temporais"]:
                if tendencia["fig"] is not None:
                    st.plotly_chart(tendencia["fig"])
                else:
                    st.warning(
                        f"Tendência temporal de {tendencia['title']} não disponível.")
        else:
            st.warning("Análise de tendências temporais não disponível.")

    if "Matriz de Correlação entre Features (incluindo NDVI)" in selecoes:
        if "corr_matrix_features" in resultados and "fig_corr_features_heatmap" in resultados and resultados["corr_matrix_features"] is not None and resultados["fig_corr_features_heatmap"] is not None:
            st.subheader(
                "Matriz de Correlação entre Features (incluindo NDVI)")
            st.plotly_chart(resultados["fig_corr_features_heatmap"])
        else:
            st.warning("Matriz de correlação entre features não disponível.")

    if "Download dos Dados" in selecoes:
        # Salvar os datasets como CSV e permitir download
        st.subheader(
            "Clique abaixo para fazer o download do Dataset escolhido: ")
        # Criadas 4 colunas, uma para cada opção de download
        col1, col2, col3, col4 = st.columns(4)

        def download_csv(df, filename, button_text, col):
            if df is not None and not df.empty:
                csv = df.to_csv(index=False).encode('utf-8')
                col.download_button(label=button_text, data=csv,
                                    file_name=filename, mime='text/csv')
            else:
                col.warning(
                    f"Dados de {button_text.split(' ')[1]} não disponíveis para download.")

        if "df_ndvi_completo" in resultados:
            download_csv(resultados["df_ndvi_completo"], 'dados_ndvi.csv',
                         'Dataset NDVI', col1)
        else:
            col1.warning("Dados de NDVI não disponíveis.")
        if "df_produtividade_completo" in resultados:
            download_csv(resultados["df_produtividade_completo"], 'dados_produtividade.csv',
                         'Dataset Produtividade', col2)
        else:
            col2.warning("Dados de Produtividade não disponíveis.")
        if "df_meteorologicos_completo" in resultados:
            download_csv(resultados["df_meteorologicos_completo"], 'dados_meteorologicos.csv',
                         'Dataset Dados Metereológicos', col3)
        else:
            col3.warning("Dados Meteorológicos não disponíveis.")
        if "df_custos_completo" in resultados:
            download_csv(resultados["df_custos_completo"], 'dados_custos.csv',
                         'Dataset Custos', col4)
        else:
            col4.warning("Dados de Custos não disponíveis.")
