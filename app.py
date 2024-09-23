import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data_from_sheet(uploaded_file, sheet_name):
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name, engine='openpyxl', header=None)

    # Exclui as primeiras linhas que não contêm dados relevantes
    df = df.drop([0, 1, 2, 3, 4]).reset_index(drop=True)

    df.columns = ['Setor', 'Segmento', 'Categoria', 'Total', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Exclui as linhas vazias do DataFrame
    df = df.dropna(how='all').reset_index(drop=True)

    return df

def main():
    st.title('Visitantes no Parque Nacional da Tijuca')
    st.image('./Logotipo_do_Parque_Nacional_da_Tijuca.jpg')


    # Color pickers para personalização do fundo e fonte
    col1, col2 = st.columns(2)
    with col1:
        bg_color = st.color_picker("Escolha a cor de fundo:", "#000000")
    with col2:
        font_color = st.color_picker("Escolha a cor das fontes:", "#ffffff")

    # Session State para manter as preferências do usuário
    if 'selected_sheet' not in st.session_state:
        st.session_state.selected_sheet = None
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = []
    if 'filter_column' not in st.session_state:
        st.session_state.filter_column = None
    if 'selected_value' not in st.session_state:
        st.session_state.selected_value = None

    # Aplicar cores de fundo e fontes ao estilo da página usando CSS
    st.markdown(f"""
    <style>
    .reportview-container {{
        background-color: {bg_color}; /* Cor de fundo do container principal */
    }}
    .markdown-text-container {{
        color: {font_color}; /* Cor do texto em markdown */
    }}
    .stApp {{
        background-color: {bg_color}; /* Cor de fundo do aplicativo */
    }}
    .stText, .stFileUploader, .stProgress {{
        color: {font_color} !important; /* Cor do texto em diversos componentes */
    }}
    .stMultiSelect div, .stMultiSelect span {{
        color: {font_color} !important; /* Cor do texto no multiselect */
    }}
    .stDataFrame, .stSpinner {{
        color: {font_color}; /* Cor do texto em DataFrames e spinners */
    }}
    .stDownloadButton {{
        color: {font_color}; /* Cor do texto no botão de download */
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {font_color}; /* Cor dos cabeçalhos */
    }}
    .stSelectbox, .stSelectbox div {{
        color: {font_color} !important; /* Cor do selectbox */
    }}
    </style>
    """, unsafe_allow_html=True)

    # Upload do arquivo
    uploaded_file = st.file_uploader("Escolha um arquivo:", type="xlsx")

    if uploaded_file:
        # Exibir uma barra de progresso enquanto o arquivo é carregado
        with st.spinner("Carregando os dados. Por favor aguarde..."):
            my_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1)
            time.sleep(1)
            my_bar.empty()

        # Dados
        xls = pd.ExcelFile(uploaded_file, engine='openpyxl')
        sheet_names = xls.sheet_names
        
        # Filtra os anos
        year_filter = [str(year) for year in range(2007, 2021)]
        filter_sheet_names = [name for name in sheet_names if name in year_filter]

        # Define a aba da panilha
        if st.session_state.selected_sheet is None or st.session_state.selected_sheet not in filter_sheet_names:
            st.session_state.selected_sheet = filter_sheet_names[0] if filter_sheet_names else None

        # Seleciona o ano (aba) a ser visualizado
        selected_sheet = st.selectbox(
            'Selecione o ano:',
            filter_sheet_names,
            index=filter_sheet_names.index(st.session_state.selected_sheet) if st.session_state.selected_sheet in filter_sheet_names else 0
        )
        st.session_state.selected_sheet = selected_sheet

        if selected_sheet:
            df = load_data_from_sheet(uploaded_file, selected_sheet)

            # Escolher as colunas a serem exibidas
            columns = df.columns.tolist()
            if st.session_state.selected_columns:
                default_columns = st.session_state.selected_columns
            else:
                default_columns = columns

            # Seleção de colunas
            selected_columns = st.multiselect(
                'Selecione as colunas para exibir:',
                columns,
                default=default_columns
            )
            st.session_state.selected_columns = selected_columns

            if selected_columns:
                df = df[selected_columns]
                # Exclui as últimas 6 linhas do DataFrame
                if len(df) > 7:
                    df = df[:-7]

                st.markdown(f"<span style='color: {font_color};'>Dados com as colunas selecionadas:</span>", unsafe_allow_html=True)
                st.dataframe(df)

                # Filtro de coluna
                if st.session_state.filter_column not in selected_columns:
                    st.session_state.filter_column = selected_columns[0] if selected_columns else None

                filter_column = st.selectbox(
                    'Selecione a coluna para filtro:',
                    selected_columns,
                    index=selected_columns.index(st.session_state.filter_column) if st.session_state.filter_column in selected_columns else 0
                )
                st.session_state.filter_column = filter_column
                
                unique_values = df[filter_column].dropna().unique().tolist()
                if st.session_state.selected_value not in unique_values:
                    st.session_state.selected_value = unique_values[0] if unique_values else None

                selected_value = st.selectbox(
                    'Selecione o valor para filtro:',
                    unique_values,
                    index=unique_values.index(st.session_state.selected_value) if st.session_state.selected_value in unique_values else 0
                )
                st.session_state.selected_value = selected_value


                # Filtra o DataFrame com base no valor selecionado
                if selected_value:
                    filtered_df = df[df[filter_column] == selected_value]
                    st.markdown(f"<span style='color: {font_color};'>Dados filtrados pela coluna {filter_column} com valor {selected_value}:</span>", unsafe_allow_html=True)
                    st.dataframe(filtered_df)

                    # Download dos dados filtrados em formato CSV
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Baixar dados filtrados",
                        data=csv,
                        file_name='dados_filtrados.csv',
                        mime='text/csv')

                    # Exibir Métricas Básicas
                    st.markdown(f"<h3 style='color: {font_color};'>Análise em gráficos</h3>", unsafe_allow_html=True)
                    if 'Total' in selected_columns:
                        filtered_df['Total'] = pd.to_numeric(filtered_df['Total'], errors='coerce')
                        st.markdown(f"<p style='color: {font_color};'>Total de registros: {len(filtered_df)}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: {font_color};'>Média Total: {filtered_df['Total'].mean()}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: {font_color};'>Soma Total: {filtered_df['Total'].sum()}</p>", unsafe_allow_html=True)

                    # Gráfico de linha
                    st.line_chart(filtered_df[['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']].T)

                    # Histograma
                    plt.figure(figsize=(10, 4), facecolor=bg_color)
                    sns.set_style('white')
                    sns.histplot(filtered_df['Total'], stat='count', color='cyan', bins=30)

                    plt.xlabel('Total', color=font_color)
                    plt.ylabel('Frequência', color=font_color)
                    plt.title('Histograma da coluna Total', color=font_color)
                    plt.tick_params(colors=font_color)
                    st.pyplot(plt)



if __name__ == "__main__":
    main()
