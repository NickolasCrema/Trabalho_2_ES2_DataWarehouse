import psycopg2
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

def convert_data_to_dataframe(data, fields):
    """
    Converte os dados coletados do Data Warehouse em um DataFrame
    @params:
        - data: Dados do banco \n
        - fields: Campos do DataFrame \n
    @return:
        - Retorna um DataFrame
    """
    df = pd.DataFrame(data, columns=fields)
    return df


def variacao_percentual(trimestre_passado, trimestre_atual):
    """
    Calcula o percentual de variação entre os dois trimestres do semestre
    @params:
        - trimestre_passado: Receita do trimestre passado \n
        - trimestre_atual: Receita do trimestre atual \n
    @return:
        - Retorna uma tupla: \n
            - Percentual de variação da receita \n
            - 0 caso seja uma variação positiva, -1 caso seja uma variação negativa
    """
    if trimestre_atual > trimestre_passado:
        return (((trimestre_atual - trimestre_passado) / trimestre_passado) * 100, 0)
    else:
        return (((trimestre_passado - trimestre_atual) / trimestre_passado) * 100, -1)


def get_db_connection_info():
    """
    Pega as configurações de conexão com o arquivo de arquivo externo
    @params: Nenhum \n
    @return:
        - Retorna uma tupla:
            - host
            - nome da base de dados
            - usuario
            - senha
    """
    with open('dbConnection.txt', 'r') as f:
        file_output = f.read()

    file_lines = file_output.split('\n')
    host = file_lines[0].split('=')[-1]
    database = file_lines[1].split('=')[-1]
    user = file_lines[2].split('=')[-1]
    password = file_lines[3].split('=')[-1]

    return host, database, user, password

host, database, user, password = get_db_connection_info()

    ##Pegando dados do banco
connection = psycopg2.connect(host=host, database=database, user=user, password=password)
cursor = connection.cursor()

sql_1_trimestre_2023 = """SELECT * FROM view_receita_1_trimestre_2023"""
cursor.execute(sql_1_trimestre_2023)
dados_1_trimestre_2023 = cursor.fetchall()

sql_2_trimestre_2023 = """SELECT * FROM view_receita_2_trimestre_2023"""
cursor.execute(sql_2_trimestre_2023)
dados_2_trimestre_2023 = cursor.fetchall()

sql_1_trimestre_2023 = """SELECT * FROM view_vendas_1_trimestre_2023"""
cursor.execute(sql_1_trimestre_2023)
dados_vendas_1_trimestre_2023 = cursor.fetchall()

sql_2_trimestre_2023 = """SELECT * FROM view_vendas_2_trimestre_2023"""
cursor.execute(sql_2_trimestre_2023)
dados_vendas_2_trimestre_2023 = cursor.fetchall()

connection.close()


fields_faturamento = ['Faturamento', 'Quantidade_Vendida', 'Imposto', 
            'Custo_Variavel', 'Numero_Trimestre', 'Nome_Trimestre',
            'Nome_Mes', 'Data', 'Lat_Cidade', 'Long_Cidade', 'Nome_Cidade'
            ]

fields_venda = ['Quantidade_Vendida', 'Faturamento', 'Numero_Trimestre', 
            'Nome_Mes', 'Latitude', 'Longitude',
            'Nome_Cidade', 'Marca', 'Categoria', 'Desc_Prod', 'Nome_Regiao'
            ]

##Tabelas

    ##Transformando dados para DataFrame
dataset_1_trimestre_2023 = convert_data_to_dataframe(dados_1_trimestre_2023, fields_faturamento)
dataset_2_trimestre_2023 = convert_data_to_dataframe(dados_2_trimestre_2023, fields_faturamento)
dataset_vendas_1_trimestre_2023 = convert_data_to_dataframe(dados_vendas_1_trimestre_2023, fields_venda)
dataset_vendas_2_trimestre_2023 = convert_data_to_dataframe(dados_vendas_2_trimestre_2023, fields_venda)


    ##Calculo de receita
dataset_1_trimestre_2023['Receita'] = dataset_1_trimestre_2023['Faturamento']\
                                        - dataset_1_trimestre_2023['Imposto']\
                                        - dataset_1_trimestre_2023['Custo_Variavel']

dataset_2_trimestre_2023['Receita'] = dataset_2_trimestre_2023['Faturamento']\
                                        - dataset_2_trimestre_2023['Imposto']\
                                        - dataset_2_trimestre_2023['Custo_Variavel']


    ##Calculo da variância de receita entre o trimestre 1 e 2
receita_1_trimestre = dataset_1_trimestre_2023['Receita'].sum()
receita_2_trimestre = dataset_2_trimestre_2023['Receita'].sum()
variacao = variacao_percentual(receita_1_trimestre, receita_2_trimestre)
diferenca = (receita_2_trimestre - receita_1_trimestre)


    ##Concatenando os dois trimestres para pegar os dados semestrais
dataset_1_semestre_2023 = pd.concat([dataset_1_trimestre_2023, dataset_2_trimestre_2023])


    ##Agrupando os dados por cidade
receita_cidades = dataset_1_semestre_2023.groupby('Nome_Cidade')[['Receita']].sum()
receita_cidades = dataset_1_semestre_2023.drop_duplicates(subset='Nome_Cidade')\
                                    [['Nome_Cidade', 'Lat_Cidade', 'Long_Cidade']]\
                                    .merge(receita_cidades, left_on='Nome_Cidade', right_index=True)\
                                    .sort_values('Receita', ascending=False)


    ##Agrupando os dados por mês
receita_mensal_1_semestre_2023 = dataset_1_semestre_2023.groupby('Nome_Mes')[['Receita']].sum().reset_index()
sorter = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho']
sorterIndex = dict(zip(sorter, range(len(sorter))))
receita_mensal_1_semestre_2023['Mes_Rank'] = receita_mensal_1_semestre_2023['Nome_Mes'].map(sorterIndex)
receita_mensal_1_semestre_2023.sort_values(['Mes_Rank'], ascending=[True], inplace=True)
receita_mensal_1_semestre_2023.drop('Mes_Rank', axis=1, inplace=True)
receita_mensal_1_semestre_2023.head()

    ##Calculando valor médio da receita dos meses do semestre
valor_medio_receitas_mensais = receita_mensal_1_semestre_2023['Receita'].sum()\
                                     / receita_mensal_1_semestre_2023['Receita'].count()


    ##Calculo percentual de receita por cidade
receita_total = receita_cidades['Receita'].sum()
receita_cidades['Percentual_de_Receita'] = receita_cidades['Receita'] / receita_total * 100
tuple_cidades_percentual = list(map(lambda a, b: (a,b),\
                                    receita_cidades['Nome_Cidade'], receita_cidades['Percentual_de_Receita']))

    ##Quantidade vendida nos trimestres
qtd_vendida_1_trimestre_2023 = dataset_vendas_1_trimestre_2023['Quantidade_Vendida'].sum()
qtd_vendida_2_trimestre_2023 = dataset_vendas_2_trimestre_2023['Quantidade_Vendida'].sum()

    ##Diferenca e variacao da quantidade vendida
variacao_qtd_vendida = variacao_percentual(qtd_vendida_1_trimestre_2023, qtd_vendida_2_trimestre_2023)
diferenca_qtd_vendida = qtd_vendida_2_trimestre_2023 - qtd_vendida_1_trimestre_2023

    ##Media de faturamento por venda dos trimestres
media_faturamento_por_venda_1_trimestre = dataset_vendas_1_trimestre_2023['Faturamento'].mean()
media_faturamento_por_venda_2_trimestre = dataset_vendas_2_trimestre_2023['Faturamento'].mean()

    ##Diferencia e variacao da media de faturamento por venda
variacao_media_faturamento_por_venda = variacao_percentual(media_faturamento_por_venda_1_trimestre, media_faturamento_por_venda_2_trimestre)
diferenca_media_faturamento_por_venda = (media_faturamento_por_venda_2_trimestre - media_faturamento_por_venda_1_trimestre)

    ##Concatenando os trimestres para pegar os dados semestrais
dataset_vendas_1_semestre_2023 = pd.concat([dataset_vendas_1_trimestre_2023, dataset_vendas_2_trimestre_2023])

    ##Faturamento por categoria de produto
faturamento_categoria = dataset_vendas_1_semestre_2023.groupby('Categoria')[['Faturamento']]\
                            .sum().reset_index().sort_values('Faturamento', ascending=False)
faturamento_max = faturamento_categoria['Faturamento'].sum()
faturamento_categoria['Percentual'] = faturamento_categoria['Faturamento'] / faturamento_max * 100
percentual_faturamento_categoria = list(map(lambda x,y: (x,y), faturamento_categoria['Percentual'], faturamento_categoria['Categoria']))


    ##Quantidade de produtos vendidos por categoria
qtd_vendida_categoria = dataset_vendas_1_semestre_2023.groupby('Categoria')[['Quantidade_Vendida']]\
                            .sum().reset_index().sort_values('Quantidade_Vendida', ascending=False)



    ##Quantidade de produtos vendidos por cidade
qtd_vendida_cidades = dataset_vendas_1_semestre_2023.groupby('Nome_Cidade')[['Quantidade_Vendida']].sum()
qtd_vendida_cidades = dataset_vendas_1_semestre_2023.drop_duplicates(subset='Nome_Cidade')\
                                    [['Nome_Cidade', 'Latitude', 'Longitude']]\
                                    .merge(qtd_vendida_cidades, left_on='Nome_Cidade', right_index=True)\
                                    .sort_values('Quantidade_Vendida', ascending=False)

    ##Quantidade de produtos vendidos por regiao
qtd_vendida_regiao = dataset_vendas_1_semestre_2023.groupby('Nome_Regiao')[['Quantidade_Vendida']].sum()
qtd_vendida_regiao = dataset_vendas_1_semestre_2023.drop_duplicates(subset='Nome_Regiao')\
                                    [['Nome_Regiao']]\
                                    .merge(qtd_vendida_regiao, left_on='Nome_Regiao', right_index=True)\
                                    .sort_values('Quantidade_Vendida', ascending=False)
qtd_max = qtd_vendida_regiao['Quantidade_Vendida'].sum()
qtd_vendida_regiao['Percentual'] = qtd_vendida_regiao['Quantidade_Vendida'] / qtd_max * 100
vendas_regiao = list(map(lambda x,y,z: (x,y,z), qtd_vendida_regiao['Nome_Regiao'], qtd_vendida_regiao['Quantidade_Vendida'], qtd_vendida_regiao['Percentual']))


    ##Pega as Informacoes dos 5 produtos mais vendidos
top5_produtos_vendidos = dataset_vendas_1_semestre_2023.groupby('Desc_Prod')[['Quantidade_Vendida']].sum()
top5_produtos_vendidos = dataset_vendas_1_semestre_2023.drop_duplicates(subset='Desc_Prod')\
                                    [['Desc_Prod', 'Marca', 'Categoria']]\
                                    .merge(top5_produtos_vendidos, left_on='Desc_Prod', right_index=True)\
                                    .sort_values('Quantidade_Vendida', ascending=False)
top5_produtos_vendidos = top5_produtos_vendidos.head()
top5_produtos_vendidos = list(map(lambda a, b, c, d: (a,b,c,d), top5_produtos_vendidos['Desc_Prod'],\
                                   top5_produtos_vendidos['Marca'], top5_produtos_vendidos['Categoria'],\
                                      top5_produtos_vendidos['Quantidade_Vendida']))

##Graficos

    ##Mapa de Receita por Cidades
fig_mapa_receita = px.scatter_geo(
                            receita_cidades,
                            lat = 'Lat_Cidade',
                            lon = 'Long_Cidade',
                            scope = 'south america',
                            size = 'Receita',
                            template = 'seaborn',
                            hover_name = 'Nome_Cidade',
                            hover_data = {'Lat_Cidade': False, 'Long_Cidade': False},
                            color = 'Nome_Cidade',
                            color_discrete_sequence=px.colors.qualitative.Alphabet
)
fig_mapa_receita.update_layout(height=650, margin={"r":0,"t":0,"l":0,"b":0})
fig_mapa_receita.update_geos(showocean=True, oceancolor='#0E1117')

    ##Grafico de Receita por Mes
fig_receita_mensal = px.bar(
                            receita_mensal_1_semestre_2023,
                            x = 'Nome_Mes',
                            y = 'Receita',
                            range_y = (0, receita_mensal_1_semestre_2023.max()),
                            color = 'Nome_Mes',
                            color_discrete_sequence=px.colors.qualitative.Alphabet
)
fig_receita_mensal.update_layout(xaxis_title='Mês')
fig_receita_mensal.update_layout(height=600, font={'size':23}, margin={"r":0,"t":0,"l":0,"b":0})


    ##Grafico de Faturamento por Categoria de Produto
fig_faturamento_categoria = px.bar(
                            faturamento_categoria,
                            x = 'Categoria',
                            y = 'Faturamento',
                            range_y = (0, faturamento_categoria.max()),
                            color = 'Categoria',
                            color_discrete_sequence=px.colors.qualitative.Alphabet
)
fig_faturamento_categoria.update_layout(height=500, width=800, font={'size':23}, margin={"r":0,"t":0,"l":0,"b":0})

    ##Grafico de Produtos Vendidos por Categoria
fig_qtd_vendido_categoria = px.bar(
                        qtd_vendida_categoria,
                        x = 'Categoria',
                        y = 'Quantidade_Vendida',
                        range_y = (0, qtd_vendida_categoria.max()),
                        color = 'Categoria',
                        color_discrete_sequence=px.colors.qualitative.Vivid
)
fig_qtd_vendido_categoria.update_layout(height=500, width=800, font={'size':23}, margin={"r":0,"t":0,"l":0,"b":0}, yaxis_title='Quantidade Vendida')

    ##Mapa de quantidade de produtos vendidos por cidades
fig_mapa_qtd_vendida = px.scatter_geo(
                            qtd_vendida_cidades,
                            lat = 'Latitude',
                            lon = 'Longitude',
                            scope = 'south america',
                            size = 'Quantidade_Vendida',
                            template = 'seaborn',
                            hover_name = 'Nome_Cidade',
                            hover_data = {'Latitude': False, 'Longitude': False},
                            color = 'Nome_Cidade',
                            color_discrete_sequence=px.colors.qualitative.Alphabet
)
fig_mapa_qtd_vendida.update_layout(height=650, margin={"r":0,"t":0,"l":0,"b":0})
fig_mapa_qtd_vendida.update_geos(showocean=True, oceancolor='#0E1117')

def main():
    ##Visualizacao
    tab1, tab2 = st.tabs(['Receita', 'Vendas'])
    with tab1:
        st.title('DASHBOARD RECEITA PRIMEIRO SEMESTRE DE 2023 :shopping_trolley:')
        coluna1, coluna2, coluna3 = st.columns([0.2, 0.60, 0.2])

        with coluna1:
            st.header('Overview')
            st.markdown("***")
            st.metric('Receita Total do Trimestre Passado', f"R$ {format(receita_1_trimestre/1000, '.2f')}mil")
            st.markdown("***")
            st.metric('Receita Total do Trimestre Atual', f"R$ {format(receita_2_trimestre/1000, '.2f')}mil")
            st.markdown("***")
            if(variacao[1]) == 0:
                porcentagem = variacao[0]
                st.metric('Aumento de', f"{format(porcentagem, '.2f')}%", delta = f"{format(diferenca, '.2f')} R$")
            else:
                porcentagem = variacao[0]
                st.metric('Redução de', f"{format(porcentagem, '.2f')}% ", delta = f"{format(diferenca, '.2f')} R$")
            
            st.markdown("***")

            st.metric('Receita Total do Semestre', f"R$ {format((receita_1_trimestre + receita_2_trimestre)/1000, '.2f')}mil")
            
            ##Espaçamento
            st.markdown('***')
            st.header('')
            st.header('')
            st.header('')
            st.header('')
            st.header('')
            st.header('')
            st.header('')
            st.header('')
            st.header('')
            st.header('')
            st.markdown('***')
            ##FimEspaçamento

            st.metric('Valor Médio das Receitas Mensais', f"R$ {format(valor_medio_receitas_mensais/1000, '.2f')}mil")
            
            ##Espaçamento
            st.markdown('***')
            ##FimEspaçamento

        with coluna2:
            ##Espaçamento
            st.text('')
            st.text('')
            st.text('')
            st.text('')
            st.text('')
            ##FimEspaçamento

            st.subheader('Receita do Semestre por Cidade')
            st.plotly_chart(fig_mapa_receita, use_container_width=True)
            
            ##Espaçamento
            st.text('')
            st.text('')
            ##FimEspaçamento

            st.subheader('Receita Mensal do Semestre')
            st.plotly_chart(fig_receita_mensal, use_container_width=True)


        with coluna3:
            
            st.subheader('Top 5 Cidades em Percentual de Receita')
            for i, cidade in enumerate(tuple_cidades_percentual):
                if i == 5:
                    break
                nome, percentual = cidade
                st.metric(f"{nome}", f"{format(percentual, '.2f')}%")
                st.markdown("***")
                i+=1

    with tab2:
        st.title('DASHBOARD VENDAS PRIMEIRO SEMESTRE DE 2023 :shopping_trolley:')
        coluna1, coluna2, coluna3 = st.columns([0.3, 0.55, 0.15])    
        with coluna1:
            st.markdown('***')
            st.metric('Quantidade de Produtos Vendidos Trimestre Passado', f"{qtd_vendida_1_trimestre_2023}")
            st.subheader('')
            st.markdown('***')
            st.metric('Média de Faturamento por Venda no Trimestre Passado', f"{format(media_faturamento_por_venda_1_trimestre, '.2f')} R$")
            st.text('')
            st.markdown('***')

            st.subheader('Top 5 Produtos Mais Vendidos')
            for produto in top5_produtos_vendidos:
                nome, marca, categoria, qtd_vendida = produto
                st.metric(f"{marca} {nome}", f"{qtd_vendida}")

            st.text('')
            st.text('')
            st.text('')
            st.text('')
            st.text('')
            
            st.markdown('***')

            st.subheader('Faturamento por Categoria (%)')
            for categoria in percentual_faturamento_categoria:
                percentual, nome_categoria = categoria
                st.metric(nome_categoria, f"{format(percentual, '.2f')}%")

            ##Espaçamento
            st.text('')
            st.text('')
            ##Fim espaçamento

            st.markdown('***')

            st.subheader('Vendas por Região')
            for regiao in vendas_regiao:
                nome_regiao, qtd_vendida_regiao, percentual_regiao = regiao
                st.metric(nome_regiao, f"{qtd_vendida_regiao} ({format(percentual_regiao, '.1f')}%)")



        with coluna2:
            st.markdown('***')
            st.metric('Quantidade de Produtos Vendidos no Trimestre Atual', f"{qtd_vendida_2_trimestre_2023}")
            st.subheader('')
            st.markdown('***')
            st.metric('Média de Faturamento por Venda no Trimestre Atual', f"{format(media_faturamento_por_venda_2_trimestre, '.2f')} R$")
            st.text('')
            st.markdown('***')
            
            st.subheader('Quantidade de Produtos Vendidos por Categoria')
            st.plotly_chart(fig_qtd_vendido_categoria)

            st.markdown('***')
            
            st.subheader('Faturamento por Categoria de Produto')
            st.plotly_chart(fig_faturamento_categoria)

            ##Espaçamento
            st.text('')
            st.text('')
            st.text('')
            st.text('')
            st.text('')
            st.text('')
            st.text('')
            st.subheader('')
            ##FimEspaçamento
            st.markdown('***')

            st.subheader('Mapa de Quantidade de Vendas por Cidade')
            st.plotly_chart(fig_mapa_qtd_vendida)

    
        with coluna3:
            st.markdown('***')
            if(variacao_qtd_vendida[1]) == 0:
                porcentagem = variacao_qtd_vendida[0]
                st.metric('Aumento de', f"{format(porcentagem, '.2f')}%", delta = f"{int(diferenca_qtd_vendida)} UN.")
            else:
                porcentagem = variacao_qtd_vendida[0]
                st.metric('Redução de', f"{format(porcentagem, '.2f')}% ", delta = int(diferenca_qtd_vendida))
            st.markdown('***')
            if(variacao_media_faturamento_por_venda[1]) == 0:
                porcentagem = variacao_media_faturamento_por_venda[0]
                st.metric('Aumento de', f"{format(porcentagem, '.2f')}%", delta = f"{format(diferenca_media_faturamento_por_venda, '.2f')} R$")
            else:
                porcentagem = variacao_media_faturamento_por_venda[0]
                st.metric('Redução de', f"{format(porcentagem, '.2f')}% ", delta = f"{format(diferenca_media_faturamento_por_venda, '.2f')} R$")
            st.markdown('***')
            
if __name__ == "__main__":
    main()