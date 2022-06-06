##Neste código vamos baixar os dados de precipitação de imagens CHIRPS
##Gerar um dataframe contendo o dado diário, mensal e anual para ser exportado em um dataframe

#1) importando as bibliotecas
#Bibliotecas dash e html
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, ClientsideFunction
import dash_bootstrap_components as dbc
import io
import os

# #Manipulação Imagens
# from datetime import datetime
# from turtle import fillcolor
# import geemap
# import ee
# import collections
# collections.Callable = collections.abc.Callable

##Bibliotecas para grágicos
# from pyrsistent import b
import plotly.express as px
import plotly.graph_objects as go
import base64

##Biliotecas para manipulação de dados
# import numpy as np
import pandas as pd
##Biblioteca para visualização do nosso mapa
import json

# # ###Autenticação no Google Eart Engine e inicialização 
# service_account = 'my-service-account@...gserviceaccount.com'
# credentials = ee.ServiceAccountCredentials(service_account, 'C:/Users/chris/Desktop/VSCode/00 - SCRIPTS_AMBGEO/02 - Py/.private-key.json')
# ee.Initialize(credentials)

# # ##Definido nossa área de estudo 
# region = ee.FeatureCollection('users/christhianscunha/brasil_limites')

# # ##Funções necessárias para manipulação dos dados 
# def data(img):
#     return img.clip(region).set('Day', img.date().format("YYYY-MM-dd"))\
#             .set('DateH', img.date().format("YYYY-MM-dd HH"))

  
# # ##Variável data
# today = ee.Date(datetime.now())

# # ##Definindo nossa coleção de imagens
# precipitacao = ee.ImageCollection('NASA/GPM_L3/IMERG_V06')\
#                  .filterBounds(region)\
#                  .filterDate(today.advance(-30, 'day'), today)\
#                  .select(['precipitationCal'])\
#                  .map(data)
  
# # ##Remove duplicatas de uma coleção. 
# # ##Observe que as duplicatas são determinadas usando um hash forte sobre a forma serializada das propriedades selecionadas.       
# dates = precipitacao.distinct('Day').aggregate_array('Day')

# def calc_acum_dia(d):
#     collection2 = precipitacao.filter(ee.Filter.eq('Day', d))\
#                             .sum()\
#                             .divide(2)
#     return collection2.set('Day', d)

# # ##Calculo da precipitação acumulada diária
# precipitacaoDiaria =  ee.ImageCollection.fromImages(dates.map(calc_acum_dia).flatten())

# # ##Função para converter informações da imagem em tabela
# def estatisticas (image):
#     serie_reduce = image.reduceRegions(**{
#                         'collection':region,
#                         'reducer': ee.Reducer.mean().combine(**{
#                         'reducer2': ee.Reducer.min(), 
#                                     'sharedInputs': True}).combine(**{
#                         'reducer2': ee.Reducer.max(),
#                                     'sharedInputs': True}), 
#                         'scale': 5000
#                         })
     
#     serie_reduce = serie_reduce.map(lambda f: f.set({'data': image.get('Day')}))                                  

#     return serie_reduce.copyProperties(image, ["system:time_start"])

# # ##Aplicando a função de redução na Coleção 
# tabela = precipitacaoDiaria.map(estatisticas)\
#                         .flatten()\
#                         .sort('date',True)\
#                         .select(['ESTADO','data','min','mean','max'],['Estado','data','Prec_min','Prec_mean','Prec_max'])

# # ##Estabelecendo a lista dos dados
# Lista_df = tabela.reduceColumns(ee.Reducer.toList(5), ['Estado','data','Prec_min','Prec_mean','Prec_max']).values().get(0)
# # # não se esqueça que precisamos chamar o método de retorno de chamada "getInfo" para recuperar os dados
# df_precipitacao = pd.DataFrame(Lista_df.getInfo(), columns=['Estado','data','Prec_min','Prec_mean','Prec_max'])
# # ##Observe que nossa base de dados não possui uma coluna de meses e anos
# # ##Criando colunas de anos, meses e dias
# df_precipitacao[["ano", "mes", "dia"]] = df_precipitacao["data"].str.split("-", expand = True)
# # ##Exportar tabela para o drive
# export_precipit = df_precipitacao.to_csv ('C:/Users/chris/Desktop/VSCode/00 - SCRIPTS_AMBGEO/02 - Py/Prec_Chirps.csv')
#------------------------------------------Juntar dados csv com json--------------------------------------------------#
CENTER_LAT, CENTER_LON = -14.272572694355336, -51.25567404158474

##Agora vamos trabalhar com dados Json
# token = open('C:/Users/chris/Desktop/FLASKDEMO/.mapbox_token').read()
brazil_states = json.load(open('brazil_geo.json', 'r'))

##visualizando nosso dado
df = pd.read_csv("Prec_Chirps.csv",sep=",")

##Abrindo os shp
df_states = df
df_states_ = df[df['data']==df['data'].max()]
df_data = df[df["Estado"]=='RJ']

##Definido nosso dicionario para o dropdown (coluna e dicionário)
select_columns = {'Prec_min':'Precipitação Mínima',
                'Prec_mean': 'Precipitação Média',
                'Prec_max': 'Precipitação Máxima'}

##Vamos colocar o que o Dash exige para construir os dashs 
##Para estilizar os themes usar a biblioteca bootstrap ou libs
# ==========================Instansiação do Dash=============================
css = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG,css])
server  = app.server 

#Vai conter nosso gráfico do mapa
#Vou utilizar a biblioteca plotly express
fig = px.choropleth_mapbox(df_states_, locations='Estado', color='Prec_mean',
                            center={'lat':-16.95, 'lon':-47.78}, zoom=4,
                            geojson=brazil_states, color_continuous_scale='blues', opacity=0.6,
                            hover_data={'Prec_min':True, 'Prec_mean':True, 'Prec_max':True, 'Estado':True},
                            labels=select_columns
                            )

##Aqui vamos definir os parâmentors da nossa página e das caixas
fig.update_layout(
    paper_bgcolor ='#c0c4cc',
    autosize=True,
    margin=go.Margin(l=0, r=0, t=0, b=0),
    showlegend= True,
    mapbox_style = 'carto-darkmatter'
)

##Cria nosso segundo gráfico
fig2 = go.Figure(layout={'template':'plotly_dark'}) ##criando uma figura vazia (pode ser assim ou com o px)
fig2.add_trace(go.Scatter(x=df_states_['data'],y=df_data['Prec_mean']))
fig2.update_layout(
    paper_bgcolor ='#242424',
    plot_bgcolor = '#242424',
    autosize = True,
    margin = dict(l=10, r=10 , t=10 ,b=10) 
)

# ==========================Layout do Dash=============================###
##Precisaremos de 3 pontos 
#Container , row and column
test_png = 'pp.png'
test_base64 = base64.b64encode(open(test_png, 'rb').read()).decode('ascii')

##Posso inserir novas colunas e posso inserir linhas
app.layout = dbc.Container(
     children=[
        dbc.Row([ 
        ###Colulna 1    
            dbc.Col([
                    html.Div([
                        html.Img(id='logo', src='data:image/png;base64,{}'.format(test_base64), style={'height':'20%', 'width':'20%'}), ##logo da empresa
                        html.H5('Precipítação Diária (mm/dia) - Obtida GEE/GPM'),##Define o tamando do cabeçalho
                        dbc.Button('Selecione o Estado', color ='primary', id='location-button', size='lg')
                    ], style={"background-color": "#1E1E1E", "margin": "-25px", "padding": "25px"}),

                    ##inserir um texto parai nformar a data
                    html.P('Informe a data na qual deseja obter informações:', style={'margin-top':'40px'}), ##margin especifica  a distância um elemento do outro
                    html.Div(
                            className="div-for-dropdown",
                            id='div-test', 
                            children=[
                                dcc.DatePickerSingle(
                                    id ='date-picker',
                                    min_date_allowed=df_states.groupby("Estado")["data"].min().max(),
                                    max_date_allowed=df_states.groupby("Estado")["data"].max().min(),
                                    initial_visible_month=df_states.groupby("Estado")["data"].min().max(),
                                    date=df_states.groupby("Estado")["data"].max().min(),
                                    display_format="MMMM D, YYYY",
                                    style={'border': '0px solid black'},
                        ) ##permite escolher uma data
                    ],
                ),

            ##Aqui vou criar uma linha com 3 colunas
            dbc.Row([
            ##Card 1
                dbc.Col([dbc.Card([
                        dbc.CardBody([
                            html.Span('Precipitação Mínima',className="card-text"),
                            html.H3(style={'color':'#adfc92'}, id='precipitacao-minima-text'),
                            ])
                        ], color = 'light', outline= True, style={'margin-top': '10px',
                                        'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                        'color': '#FFFFFF'})],md=4), ##fim do primeiro card
              
            ###Card 2
                dbc.Col([dbc.Card([
                        dbc.CardBody([
                            html.Span('Precipitação Média',className="card-text"),
                            html.H3(style={'color':'#289fd6'}, id='precipitacao-media-text'),
                           
                        ])
                        ], color = 'light', outline= True, style={'margin-top': '10px',
                                        'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                        'color': '#FFFFFF'})],md=4), ##fim do primeiro card
            ###Card 3
                dbc.Col([dbc.Card([
                        dbc.CardBody([
                            html.Span('Precipitação Máxima',className="card-text"),
                            html.H3(style={'color':'#DF2935'}, id='precipitacao-maxima-text'),
                         ])
                        ], color = 'light', outline= True, style={'margin-top': '10px',
                                        'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                        'color': '#FFFFFF'}) ],md=4), ##fim do primeiro card
               ]),
                
               html.Div([
                    html.P('Selecione o tipo de dado que deseja visualizar:', style={'margin-top':'25px'}),
                    dcc.Dropdown(
                                    id="location-dropdown",
                                    options=[{"label": j, "value": i}
                                            for i, j in select_columns.items()
                                            ],
                                            value="Prec_mean",
                                            style={"margin-top": "10px"}
                                            ),
                                dcc.Graph(id='line-graph', figure=fig2,style={
                            "background-color": "#242424",
                            }),
                        ], id="teste")
            ], md=5, style={
                          "padding": "25px",
                          "background-color": "#242424"
                          }),
        ###Coluna 2
        dbc.Col(
                [
                    dcc.Loading(
                        id="loading-1",
                        type="default",
                        children=[dcc.Graph(id="choropleth-map", figure=fig, 
                            style={'height': '100vh', 'margin-right': '10px'})],
                    ),
                ], md=7),
            ],className="g-0")
     ], fluid=True,
)

# =====================================================================
# Interactivity
@app.callback(
    [
        Output("precipitacao-minima-text", "children"),
        Output("precipitacao-media-text", "children"),
        Output("precipitacao-maxima-text", "children"),
    ], [Input("date-picker", "date"), Input("location-button", "children")]
)
def display_status(date, location):
    # print(location, date)
    if location == "RS":
        df_data_on_date = df[df["data"] == date]
    else:
        df_data_on_date = df_states[(df_states["Estado"] == location) & (df_states["data"] == date)]

    prec_min = "-" if df_data_on_date["Prec_min"].isna().values[0] else f'{int(df_data_on_date["Prec_min"].values[0]):,}'.replace(",", ".") 
    prec_mean = "-" if df_data_on_date["Prec_mean"].isna().values[0]  else f'{int(df_data_on_date["Prec_mean"].values[0]):,}'.replace(",", ".") 
    prec_max = "-" if df_data_on_date["Prec_max"].isna().values[0]  else f'{int(df_data_on_date["Prec_max"].values[0]):,}'.replace(",", ".") 
    return (
            prec_min, 
            prec_mean, 
            prec_max, 
            )


@app.callback(
        Output("line-graph", "figure"),
        [Input("location-dropdown", "value"), Input("location-button", "children")]
)
def plot_line_graph(plot_type, location):
    if location == "RS":
        df_data_on_location = df.copy()
    else:
        df_data_on_location = df_states[(df_states["Estado"] == location)]
    fig2 = go.Figure(layout={"template":"plotly_dark"})
    bar_plots = ["Prec_min", "Prec_max"]

    if plot_type in bar_plots:
        fig2.add_trace(go.Bar(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))
    else:
        fig2.add_trace(go.Scatter(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))
    
    fig2.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        margin=dict(l=10, r=10, b=10, t=10),
        )
    return fig2


@app.callback(
    Output("choropleth-map", "figure"), 
    [Input("date-picker", "date")]
)
def update_map(date):
    df_data_on_states = df_states[df_states["data"] == date]

    fig = px.choropleth_mapbox(df_data_on_states, locations="Estado", geojson=brazil_states, 
        center={"lat": CENTER_LAT, "lon": CENTER_LON},  # https://www.google.com/maps/ -> right click -> get lat/lon
        zoom=4, color="Prec_mean", color_continuous_scale="blues", opacity=0.55,
        hover_data={"Prec_min": True, "Prec_mean": True, "Prec_max": True, "Estado": False},
        labels=select_columns
        )

    fig.update_layout(paper_bgcolor="#c0c4cc", mapbox_style="carto-darkmatter", autosize=True,
                    margin=go.layout.Margin(l=0, r=0, t=0, b=0), showlegend=False)
    return fig


@app.callback(
    Output("location-button", "children"),
    [Input("choropleth-map", "clickData"), Input("location-button", "n_clicks")]
)
def update_location(click_data, n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if click_data is not None and changed_id != "location-button.n_clicks":
        state = click_data["points"][0]["location"]
        return "{}".format(state)
    
    else:
        return "RS"


#---------------------------Executar----------------------------------------#
if __name__ =='__main__':
    
    app.run_server(debug=True, port=8050),       