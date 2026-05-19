##Executar o Streamlit
# C:\Python_VSCODE\Dashboard_Streamlit>streamlit run dashboard.py
# CTRL S para salvar

## Importando as bibliotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

## Configurando o tamanho da página
st.set_page_config(layout = 'wide')

## Colocando o título da página
st.title('DASHBOARD DE VENDAS:shopping_trolley:')

# Função para formatar valores
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


# Coletando os dados da API

url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

# Criando uma barra lateral fixa e filtro de região
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

# Deixano o filtro como Brasil retorna os dados padronizados
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)   
if todos_anos == '':
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao':regiao.lower(), 'ano':ano}    
response = requests.get(url, params = query_string) # carregando a requisição
dados = pd.DataFrame.from_dict(response.json()) # convertendo JSON em dataframe
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Criando o filtro de vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]


## Tabelas

# Receita por estados
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 
                                        'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra',
                                        right_index = True).sort_values('Preço',ascending = True)

# Receita mensal
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Receita por categoria
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço')

# Vendas por estados
vendas_estados = dados.groupby('Local da compra').size().reset_index(name ='Vendas')
vendas_estados = dados.drop_duplicates(subset = 
                                        'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra',
                                        right_on = 'Local da compra').sort_values('Vendas', ascending = True)

# Vendas mensais
vendas_mensais = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M')).size().reset_index(name ='Vendas')
vendas_mensais['Ano'] = vendas_mensais['Data da Compra'].dt.year
vendas_mensais['Mes'] = vendas_mensais['Data da Compra'].dt.month_name()

# Vendas por categorias
vendas_categorias = dados.groupby('Categoria do Produto').size().reset_index(name = 'Vendas').sort_values('Vendas', ascending = True)

# Vendas por vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## Gráficos

# Mapa da receita
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat':False, 'lon':False},
                                  title = 'Receita por estado')

# Receita mensal - Gráfico de linha
fig_receita_mensal = px.line(receita_mensal, 
                             x = 'Mes', 
                             y = 'Preço',
                             markers = True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

# Receita por estados - Top 5
fig_receita_estados = px.bar(receita_estados.head(),
                             y = 'Local da compra',
                             x = 'Preço',
                             text_auto = True,
                             title = 'Top estados (receita)',
                             orientation = 'h')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

# Receita por categorias - Top 5
fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por categoria',
                                x = 'Preço',
                                orientation = 'h')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

# Vendas por estados
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                  lat = 'lat',
                                  lon = 'lon',  
                                  scope = 'south america',
                                  size = 'Vendas',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat':False, 'lon':False},
                                  title = 'Vendas por estado')

# Vendas mensais
fig_vendas_mensais = px.line(vendas_mensais,
                             x = 'Mes',
                             y = 'Vendas',
                             markers = True,
                             range_y = (0, vendas_mensais.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Vendas mensais')
fig_vendas_mensais.update_layout(yaxis_title = 'Vendas')

# Vendas por estados - Top 5
fig_vendas_estados = px.bar(vendas_estados.head(),
                             y = 'Local da compra',
                             x = 'Vendas',
                             text_auto = True,
                             title = 'Top estados (vendas)',
                             orientation = 'h')
fig_vendas_estados.update_layout(yaxis_title = 'Estados')

# Vendas por categoria - Top 5
fig_vendas_categorias = px.bar(vendas_categorias,
                               y = 'Categoria do Produto',
                               x = 'Vendas',
                               text_auto = True,
                               title = 'Top categorias (vendas)',
                               orientation = 'h')
fig_vendas_categorias.update_layout(yaxis_title = 'Categorias')


## Visualização no Streamlit

# Criando abas
aba1, aba2, aba3 = st.tabs(['Receita','Quantidade de vendas', 'Vendedores'])

# Elementos da aba 1
with aba1:
# Criando Indicadores e gráficos
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

# Elementos da aba 2
with aba2:
# Criando Indicadores e gráficos
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)
 
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensais, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

# Elementos da aba 3
with aba3:
# Criando Indicadores e gráficos
    qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
 
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_venda_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending = False).head(qtd_vendedores).index,
                                        text_auto = True,
                                        title = f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_venda_vendedores)       
 

# Criando os visuais de tabela
#st.dataframe(dados)

