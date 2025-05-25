import streamlit as st
import pandas as pd
import requests

def exibir_pagina_carregar_dados():

    def upload_dados(tipo):

        st.subheader(tipo["titulo"])
        st.markdown(
            "Os dados devem estar em formato CSV e devem conter as seguintes colunas:<br>"
            f"<b>{tipo['colunas']}</b><br>",
            unsafe_allow_html=True
        )

        df = st.file_uploader(
            "Carregar arquivo CSV",
            type=["csv"],
            label_visibility="collapsed",
            help="Selecione o arquivo CSV",
            key=f"upload_{tipo['url']}"
        )
        if df is not None:
            try:
                df = pd.read_csv(df)
                if tipo == NDVI or tipo == METEOROLOGICOS:    
                    if 'DATA' in df.columns:
                        df['DATA'] = pd.to_datetime(df['DATA'], format='mixed').dt.strftime('%Y-%m-%d %H:%M:%S')
                st.write("Preview dos dados:")
                st.dataframe(df.head(), hide_index=True)
                if st.button("Processar Dados", key="upload_dados", help="Carregar arquivo CSV", icon="📤"):
                    try:
                        dados = df.to_csv(index=False, quotechar='"', quoting=1)
                        response = requests.post(
                            f"{API_URL}/{tipo["url"]}/batchload?batchRows=500",
                            data=dados,
                            headers={"Content-Type": "text/csv"}
                        )
                        if "SUCCESS" in response.text:
                            st.success(f"Dados enviados com sucesso! {len(df)} registros processados.")
                            return True
                        elif "ERROR" in response.text:
                            st.error(f"Erro ao enviar dados: {response.status_code} - {response.text}")
                            return False
                    except Exception as e:
                        st.error(f"Erro durante o upload: {str(e)}")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {str(e)}")

        st.markdown("---")


    API_URL = "https://g12bbd4aea16cc4-orcl1.adb.ca-toronto-1.oraclecloudapps.com/ords/fiap"
    NDVI = {
        "titulo": "Dados NDVI",
        "url": "carga_ndvi",
        "colunas": '"ID", "LOCALIDADE", "CULTURA", "DATA", "NDVI"'
    }
    PRODUTIVIDADE = {
        "titulo": "Dados de Produtividade",
        "url": "carga_produtividade",
        "colunas": '"ID","LOCALIDADE","CULTURA","ANO","AREA_PLANTADA","AREA_COLHIDA","RENDIMENTO_MEDIO"'
    }
    METEOROLOGICOS = {
        "titulo": "Dados Meteorológicos",
        "url": "carga_dados_meteorologicos",
        "colunas": '"ID","LOCALIDADE","DATA","PRECIPITACAO","PRESSAO_ATMOSFERICA","RADIACAO_SOLAR_GLOBAL","TEMPERATURA_BULBO_SECO","TEMPERATURA_ORVALHO","UMIDADE_RELATIVA","VELOCIDADE_VENTO"'
    }

    # Cabeçalho
    st.header("☁️ Carga de Dados")
    st.markdown("---")

    # Conteúdo
    upload_dados(NDVI)
    upload_dados(PRODUTIVIDADE)
    upload_dados(METEOROLOGICOS)
