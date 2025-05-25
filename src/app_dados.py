import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# URL base da API Oracle
url_base = "https://g12bbd4aea16cc4-orcl1.adb.ca-toronto-1.oraclecloudapps.com/ords/fiap"

# Cabeçalho para requisições JSON
CONTENT_TYPE_JSON = {"Content-Type": "application/json"}


def carregar_dados_oracle(tipo):  # Carregar dados da API Oracle
    endpoint, cols = None, None  # Inicialização de endpoint e colunas
    if tipo == "ndvi":
        endpoint = f"{url_base}/carga_ndvi/"
        cols = ["localidade", "cultura", "data", "ndvi"]
    elif tipo == "produtividade":
        endpoint = f"{url_base}/carga_produtividade/"
        cols = [
            "localidade",
            "cultura",
            "ano",
            "area_plantada",
            "area_colhida",
            "rendimento_medio",
        ]
    elif tipo == "meteorologicos":
        endpoint = f"{url_base}/carga_dados_meteorologicos/"
        cols = [
            "localidade",
            "data",
            "precipitacao",
            "pressao_atmosferica",
            "radiacao_solar_global",
            "temperatura_bulbo_seco",
            "temperatura_orvalho",
            "umidade_relativa",
            "velocidade_vento",
        ]
    elif tipo == "custos":
        endpoint = f"{url_base}/carga_custos/"
        cols = ["localidade", "cultura", "ano", "indicador", "custo"]
    else:
        st.error(f"Tipo de dados inválido: {tipo}")
        return pd.DataFrame()

    all_items = []  # Lista para armazenar todos os itens
    has_more = True  # Variável para controle de paginação
    while has_more:  # Loop para carregar dados paginados
        try:
            response = requests.get(
                endpoint, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            response_json = response.json()

            if "items" in response_json:
                all_items.extend(response_json["items"])
            else:
                st.warning(
                    f"A resposta da API para {tipo} não continha 'items'. Verifique a API.")
                return pd.DataFrame()
            has_more = response_json.get("hasMore", False)
            if has_more:
                next_link = next(
                    (link["href"] for link in response_json.get(
                        "links", []) if link["rel"] == "next"),
                    None,
                )
                if next_link:
                    endpoint = next_link
                else:
                    st.warning(
                        f"A API para {tipo} indicou 'hasMore', mas não forneceu um link 'next'.")
                    has_more = False
            else:
                has_more = False
        except requests.exceptions.RequestException as e:  # Tratamento de exceções para requisições
            st.error(f"Erro ao carregar dados de {tipo}: {e}")
            return pd.DataFrame(columns=cols)
        except ValueError as e:  # Tratamento de exceções para decodificação JSON
            st.error(
                f"Erro ao decodificar JSON para {tipo}: {e}. Verifique a resposta da API.")
            return pd.DataFrame(columns=cols)
        except KeyError as e:  # Tratamento de exceções para chaves ausentes no JSON
            st.error(
                f"Erro de chave no JSON para {tipo}: {e}. Verifique a estrutura da resposta da API.")
            return pd.DataFrame(columns=cols)

    if not all_items and cols:  # Verifica se não há itens e se as colunas estão definidas
        st.warning(f"Nenhum dado encontrado para o tipo: {tipo}.")
        return pd.DataFrame(columns=cols)
    elif not all_items:
        st.warning(
            f"Nenhum dado encontrado para o tipo: {tipo} e colunas não definidas.")
        return pd.DataFrame()
    else:
        return pd.DataFrame(all_items, columns=cols)
