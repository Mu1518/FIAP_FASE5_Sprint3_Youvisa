import streamlit as st
import pandas as pd
from datetime import datetime
import pickle
import os
from app_dados import carregar_dados_oracle


# acrescenta o prefixo R$ e formata o valor com duas casas decimais
def formata_valores(valor, prefixo=''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


# formata o valor com duas casas decimais e acrescenta o sufixo desejado
def formata_valores_posfixo(valor, posfixo=''):

    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{valor:.2f} {unidade} {posfixo}'.strip()
        valor /= 1000
    return f'{valor:.2f} milhões {posfixo}'.strip()


def exibir_pagina_produtividade():
    st.header("💡 Estimativa de Produtividade")
    st.markdown("---")

    try:
        # Carregar dados para as opções de seleção (localidades e culturas)
        df_prod = carregar_dados_oracle("produtividade")
        if df_prod.empty:
            st.warning("Não há dados de produtividade disponíveis para seleção.")
            return
        localidades = df_prod['localidade'].unique()
        culturas_base = df_prod['cultura'].unique()

        col1, col2 = st.columns(2)
        localidade_selecionada = col1.selectbox("Localidade", localidades)
        culturas_filtradas = df_prod[df_prod['localidade']
                                     == localidade_selecionada]['cultura'].unique()
        cultura_selecionada = col2.selectbox("Cultura", culturas_filtradas)

        col1, col2, col3 = st.columns(3)
        ano_atual = datetime.now().year
        anos_futuros = list(range(ano_atual, ano_atual + 6))
        ano_plantio = col1.selectbox("Ano de Plantio", anos_futuros)
        meses = list(range(1, 13))
        mes_plantio = col2.selectbox(
            "Mês de Plantio",
            meses,
            format_func=lambda x: datetime(ano_atual, x, 1).strftime("%B"),
        )
        area_plantada = col3.number_input(
            "Área Plantada (ha)", min_value=0.0, step=0.1)

        if st.button("Calcular", type="primary"):
            PASTA_MODELOS = "modelos_treinados"
            modelo_path = os.path.join(PASTA_MODELOS, "melhor_modelo.pkl")

            if area_plantada == 0:
                st.error("A área plantada deve ser maior do que zero")
                return

            if not os.path.exists(modelo_path):
                st.error("O melhor modelo não foi encontrado. Por favor, treine os modelos primeiro.")
                return

            with open(modelo_path, "rb") as f:
                melhor_modelo_data = pickle.load(f)
                modelo = melhor_modelo_data.get('modelo', None)
                modelo_nome = melhor_modelo_data.get(
                    'nome', 'Modelo desconhecido')
                # Obter nomes das features esperadas
                modelo_features = getattr(modelo, 'feature_names_in_', None)

            # Preparar os dados de entrada para a predição
            input_data = pd.DataFrame({
                'localidade': [localidade_selecionada],
                'cultura': [cultura_selecionada],
                'ano': [ano_plantio],
                'mes': [mes_plantio],
                'area_plantada': [area_plantada]

            })

            input_data = pd.get_dummies(input_data)

            if modelo_features is not None:
                # Adicionar colunas ausentes com valor 0
                for feature in modelo_features:
                    if feature not in input_data.columns:
                        input_data[feature] = 0
                # Garantir a ordem correta das colunas
                input_data = input_data[modelo_features]
            elif hasattr(modelo, 'n_features_in_') and input_data.shape[1] != modelo.n_features_in_:
                st.error(
                    f"Número de features de entrada ({input_data.shape[1]}) não corresponde ao esperado pelo modelo ({modelo.n_features_in_}).")
                return

            # Realizar a predição
            predicao = modelo.predict(input_data)[0]
            st.info("RESULTADO", icon="ℹ️")
            st.write(f"**Localidade:** {localidade_selecionada}")
            st.write(f"**Cultura:** {cultura_selecionada}")
            st.write(f"**Ano de Plantio:** {ano_plantio}")
            st.write(
                f"**Mês de Plantio:** {datetime(ano_atual, mes_plantio, 1).strftime('%B')}")
            st.write(
                f"**Área Plantada:** {formata_valores_posfixo(area_plantada, 'ha')}")
            st.write(
                f"**Produtividade Prevista:** {formata_valores_posfixo(predicao, 'kg/ha')}")
            st.subheader(
                f"Produção Total Estimada: {formata_valores(predicao * area_plantada, 'R$ ')}"
            )
            st.caption(
                f"Modelo utilizado para cálculo da produtividade: {modelo_nome}")

    except Exception as e:
        st.error(f"Ocorreu um erro ao realizar a previsão: {e}")
