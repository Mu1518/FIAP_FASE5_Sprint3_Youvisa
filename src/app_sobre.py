import streamlit as st

def exibir_pagina_sobre():
    st.header(" 🗺️ Sobre o Projeto")
    st.write("---")
    st.write("""
            Este projeto, referente a segunda fase do Challenge Ingredion do Curso de Inteligência Artificial da FiAP (1TIAO),
            tem como foco o desenvolvimento de um modelo de Inteligência Artificial para cálculo de previsão da produtividade agrícola, utilizando NDVI
            (Índice de Vegetação Normalizada), dados climáticos, de produtividade e custo.
            
            Os datasets utilizados no programa foram previamente tratados e limpos antes de serem carregados via APEX para a nuvem Oracle. Isso ocorreu pela
            natureza diversa das formatações e pela necessidade de padronização dos dados para garantir a integridade e a precisão das análises.
            
            Os valores faltantes foram tratados com a média dos dados disponíveis, e os dados foram convertidos para o formato adequado para análise.
            
            O projeto foi desenvolvido em Python, utilizando as bibliotecas Streamlit, Pandas, NumPy, Scikit-learn, Plotly, Pickle, Os, Requests, Locale e Datetime.       
        
    """)

    st.subheader(" 🌟 Nosso Time")

    nomes_com_espacos = "Jonatas Gomes&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Iolanda Manzali&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Murilo Nasser&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Pedro Sousa&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Amanda Fragnan"
    st.write(nomes_com_espacos)

    st.subheader(" ⏳ Próximos Passos")
    st.write("""
            Este é um projeto em evolução. Inicialmente foi selecionada a cultura de milho da cidade de  Sorriso, localizada no estado do Mato Grosso.
            O programa foi construido para ser escalável, e para novas versões esperamos acrescentar novos dados para extrapolar o calculo da produtividade.
        """)

    st.write('👍🏻 Gostou do Projeto?')
    sentiment_mapping = ["1", "2", "3", "4", "5"]
    selected = st.feedback("stars")
    if selected is not None:
        st.markdown(f"Você selecionou {sentiment_mapping[selected]} estrelas!")
        st.balloons()
