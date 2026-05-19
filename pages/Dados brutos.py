## Criando uma página com dados brutos

## Importando as bibliotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

## Funções

# Armazenando o download em cache
@st.cache_data

# Função para converter o df em CSV
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

# Criando a mensagem de sucesso após o download
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = '✅')
    time.sleep(5)   # Mensagem exibida durante 5 minutos
    sucesso.empty() # Desligar mensagem

## Colocando o título da página
st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

# Carregando a requisição
response = requests.get(url)

# Convertendo JSON em dataframe
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Criando filtros

# Filtro para seleção de colunas da tabela Dados Brutos
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# Barra lateral de filtros
st.sidebar.title('Filtros')

with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0, 5000))
with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione os locais de compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione as formas de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())    
with st.sidebar.expander('Quantidade de parcelas'):
    parcelas = st.slider('Selecione as parcelas', 1, 24, value = (1, 24)) 
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a nota', 1, 5, value = (1, 5))    

# Criando uma query para a filtragem dos dados para os filtros
query = '''
Produto in @produtos and \
@preco[0] <= Preço <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
`Categoria do Produto` in @categoria and \
`Vendedor` in @vendedor and \
`Local da compra` in @local_compra and \
`Tipo de pagamento` in @tipo_pagamento and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1] and \
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] 

'''
dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

# Visualizando o df
st.dataframe(dados_filtrados)

# Mensagem de quantidade de linhas e colunas
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)    
