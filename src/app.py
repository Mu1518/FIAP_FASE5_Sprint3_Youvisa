import locale
import streamlit as st
from app_sobre import exibir_pagina_sobre
from app_links import exibir_links_importantes
from app_carga import exibir_pagina_carregar_dados
from app_analise import analise_exploratoria
from app_produtividade import exibir_pagina_produtividade
from app_treinamento import exibir_pagina_treinamento


st.markdown(""" <style> .centered-text {text-align: center}</style> """, unsafe_allow_html=True)
st.markdown('<h1 class="centered-text"><b> 🛰️ CHALLENGE INGREDION</b></h1>', unsafe_allow_html=True)
st.markdown('<h3 class="centered-text"><b>SPRINT 3</b></h3>', unsafe_allow_html=True)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Configuração de localidade


def main():
    st.subheader("Escolha uma opção abaixo:")
    colun1, colun2 = st.columns(2)

    if colun1.button("Sobre o Projeto", key="menu_sobre", type="secondary", use_container_width=True, icon="🗺️"):
        st.session_state.pagina_ativa = "sobre"
    if colun2.button("Links Importantes", key="menu_links", type="secondary", use_container_width=True, icon="🔗"):
        st.session_state.pagina_ativa = "links"
    if colun1.button("Carga de Dados", key="menu_carga", type="secondary", use_container_width=True, icon="☁️"):
        st.session_state.pagina_ativa = "carga"
    if colun2.button("Análise Exploratória", key="menu_analise", type="secondary", use_container_width=True, icon="🔍"):
        st.session_state.pagina_ativa = "analise"
    if colun1.button("**Treinamento de Modelos**", key="menu_treinamento", type="secondary", use_container_width=True, icon="📚"):
        st.session_state.pagina_ativa = "treinamento"
    if colun2.button("Estimativa de Produtividade", key="menu_previsao", type="primary", use_container_width=True, icon="💡"):
        st.session_state.pagina_ativa = "previsao"

    if "pagina_ativa" in st.session_state:
        if st.session_state.pagina_ativa == "sobre":
            exibir_pagina_sobre()
        elif st.session_state.pagina_ativa == "links":
            exibir_links_importantes()
        elif st.session_state.pagina_ativa == "carga":
            exibir_pagina_carregar_dados()
        elif st.session_state.pagina_ativa == "analise":
            analise_exploratoria()
        elif st.session_state.pagina_ativa == "treinamento":
            exibir_pagina_treinamento()
        elif st.session_state.pagina_ativa == "previsao":
            exibir_pagina_produtividade()


if __name__ == "__main__":
    if "pagina_ativa" not in st.session_state:
        st.session_state.pagina_ativa = None
    main()
