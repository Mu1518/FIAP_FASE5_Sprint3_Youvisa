import streamlit as st
import pickle
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.ensemble import AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
from app_dados import carregar_dados_oracle


@st.cache_data  # Cache para evitar chamadas repetidas à API
def carregar_dados_produtividade():  # Carregar dados de produtividade via API
    return carregar_dados_oracle("produtividade")


def treinar_modelos_supervisionados(X, y, modelos_selecionados):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    modelos = {
        'LinearRegression': (LinearRegression(), {}),
        'SVR': (SVR(), {'C': [0.1, 1, 10], 'kernel': ['rbf', 'linear', 'poly']}),
        'RandomForest': (RandomForestRegressor(), {
            'n_estimators': [100, 200],
            'max_depth': [None, 10],
            'min_samples_split': [2, 5]
        }),
        'GradientBoosting': (GradientBoostingRegressor(), {
            'n_estimators': [100, 200],
            'learning_rate': [0.01, 0.1],
            'max_depth': [3, 5]
        }),
        'Ridge': (Ridge(), {'alpha': [0.1, 1.0, 10.0]}),
        'Lasso': (Lasso(), {'alpha': [0.1, 1.0, 10.0]}),
        'ElasticNet': (ElasticNet(), {'alpha': [0.1, 1.0, 10.0], 'l1_ratio': [0.2, 0.5, 0.8]}),
        'DecisionTree': (DecisionTreeRegressor(), {'max_depth': [None, 5, 10]}),
        'KNeighbors': (KNeighborsRegressor(), {'n_neighbors': [3, 5, 7]}),
        'AdaBoost': (AdaBoostRegressor(), {'n_estimators': [50, 100], 'learning_rate': [0.01, 0.1]})
    }

    resultados = {}
    for nome in modelos_selecionados:
        modelo, params = modelos[nome]
        try:
            with st.spinner(f"Treinando {nome}..."):
                grid = GridSearchCV(modelo, params, cv=5,
                                    scoring='neg_mean_squared_error',
                                    n_jobs=-1, verbose=0)
                grid.fit(X_train, y_train)
                y_pred = grid.predict(X_test)
                score = np.sqrt(mean_squared_error(y_test, y_pred))
                resultados[nome] = {
                    'score': score,
                    'melhor_modelo': grid.best_estimator_,
                    'melhores_params': grid.best_params_
                }
        except Exception as e:
            st.warning(f"Erro no modelo {nome}: {str(e)}")
    return resultados


def exibir_pagina_treinamento():
    st.header("📚 Treinamento de Modelos")
    st.markdown("---")

    modelos_opcoes = {
        'LinearRegression': 'Regressão Linear',
        'SVR': 'Máquina de Vetores de Suporte',
        'RandomForest': 'Random Forest',
        'GradientBoosting': 'Gradient Boosting',
        'Ridge': 'Ridge',
        'Lasso': 'Lasso',
        'ElasticNet': 'Elastic Net',
        'DecisionTree': 'Árvore de Decisão',
        'KNeighbors': 'KNN',
        'AdaBoost': 'AdaBoost'
    }

    st.write(
        "Selecione os modelos que deseja treinar. Você pode escolher mais de um modelo para comparação."
    )
    modelos_selecionados = st.multiselect(
        "Modelos",
        options=list(modelos_opcoes.keys()),
        format_func=lambda x: modelos_opcoes[x],
        default=[],
        label_visibility="collapsed",
    )

    if st.button("Iniciar Treinamento", type="primary"):
        if not modelos_selecionados:
            st.error("Selecione pelo menos um modelo!")
            return

        df = carregar_dados_produtividade()
        if df.empty:
            st.error("Dados insuficientes para treinamento.")
            return

        X = pd.get_dummies(
            df.drop(columns=["rendimento_medio", "data"], errors='ignore'))
        y = df["rendimento_medio"]

        with st.spinner("Treinando modelos..."):
            resultados = treinar_modelos_supervisionados(
                X, y, modelos_selecionados)

            if resultados:
                melhor_modelo = min(
                    resultados, key=lambda k: resultados[k]['score'])
                PASTA_MODELOS = "modelos_treinados"
                os.makedirs(PASTA_MODELOS, exist_ok=True)

                # Salvar todos modelos
                for nome, info in resultados.items():
                    with open(os.path.join(PASTA_MODELOS, f"{nome}.pkl"), "wb") as f:
                        pickle.dump(info, f)

                # Salvar melhor modelo
                with open(os.path.join(PASTA_MODELOS, "melhor_modelo.pkl"), "wb") as f:
                    pickle.dump({
                        'nome': melhor_modelo,
                        'modelo': resultados[melhor_modelo]['melhor_modelo'],
                        'params': resultados[melhor_modelo]['melhores_params'],
                        'score': resultados[melhor_modelo]['score']
                    }, f)

                # Exibir resultados
                st.subheader("Resultados do Treinamento")
                st.success(
                    f"Melhor modelo: {melhor_modelo} (RMSE: {resultados[melhor_modelo]['score']:.2f})")

                with st.expander("Detalhes dos Modelos"):
                    for nome, info in resultados.items():
                        st.write(f"**{modelos_opcoes[nome]}**")
                        st.write(f"RMSE: {info['score']:.2f}")
                        st.write(
                            f"Melhores parâmetros: {info['melhores_params']}")
                        st.write("---")

                st.balloons()
            else:
                st.error("Nenhum modelo foi treinado com sucesso.")


