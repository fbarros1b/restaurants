import folium as fo
from streamlit_folium import folium_static
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import plotly.express as px
import streamlit as st

countries = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}

def country_name(country_id):
    return countries[country_id]

def get_price_range_description(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

def convert_to_dollar(currency, price):
    if currency == 'Botswana Pula(P)':
        return price*0.076
    elif currency == 'Brazilian Real(R$)':
        return price*0.19
    elif currency == 'Dollar($)':
        return price*1
    elif currency == 'Emirati Diram(AED)':
        return price*0.27
    elif currency == 'Indian Rupees(Rs.)':
        return price*0.012
    elif currency == 'Indonesian Rupiah(IDR)':
        return price*0.000066
    elif currency == 'NewZealand($)':
        return price*0.623515
    elif currency == 'Pounds(£)':
        return price*1.24
    elif currency == 'Qatari Rial(QR)':
        return price*0.27
    elif currency == 'Rand(R)':
        return price*0.056
    elif currency == 'Sri Lankan Rupee(LKR)':
        return price*0.0031
    elif currency == 'Turkish Lira(TL)':
        return price*0.0052
    else:
        return price

def clear_data(df):
  # Limpeza
  # Remove itens duplicados
  df1 = df.drop_duplicates()

  # Reseta index para não criar o problema de itens "pulados" pelo filtro.
  # O inplace=True serve para executar as alterações no próprio dataframe (e não como retorno), e
  # o drop=True serve para ele não gerar uma nova coluna de index.
  df1.reset_index(inplace=True, drop=True)

  # Disable chained assignments, evita o warning de cópia sobre uma parte do dataframe.
  pd.options.mode.chained_assignment = None

  # A coluna do dataframe possui várias informações separadas por vírgulas. Essa função remove as
  # demais e atribui apenas o primeiro valor.
  # Possível utilização também da função assign:
  # df = df.assign(my_col=lambda d: d['my_col'].astype(int))
  df1['Cuisines'] = df1.loc[:, 'Cuisines'].apply(lambda x: str(x).split(',')[0])

  # Cria a coluna com o nome do país baseado na função definida acima.
  df1['Country Name'] = df1.loc[:, 'Country Code'].apply(lambda x: country_name(x))

  # Cria a coluna com a descrição da faixa de preço baseado na função definida acima.
  df1['Price Range Description'] = df1.loc[:, 'Price range'].apply(lambda x: get_price_range_description(x))

  # Acertando um valor errado em um restaurante na Austrália.
  df1.loc[(df1['Country Name']=='Australia') & (df1['Average Cost for two']==25000017.0), 'Average Cost for two']=250

  # Cria a coluna com o preço em dólar baseado na função definida acima.
  df1['Price in Dollar for two'] = df1.loc[:, ['Currency', 'Average Cost for two']].apply(lambda x: convert_to_dollar(x['Currency'], x['Average Cost for two']), axis=1)
  
  return df1

st.set_page_config(page_title='Country View',
                   layout='wide',
                   initial_sidebar_state='expanded',
                   page_icon=':earth_americas:')

# Lendo o arquivo e limpando o data frame
df = pd.read_csv('zomato.csv')
df1 = clear_data(df)

# Streamlit
# Barra lateral
#st.sidebar.image(Image.open('pineapple.jpg'), width=60)
#st.sidebar.markdown("""---""")

st.sidebar.markdown('## Filter')
countryList = st.sidebar.multiselect('Which countries do you want to view?',
                                      ['Australia', 'Brazil', 'Canada', 'England', 'India', 'Indonesia', 'New Zeland',
                                       'Philippines', 'Qatar', 'Singapure', 'South Africa', 'Sri Lanka', 'Turkey',
                                       'United Arab Emirates', 'United States of America'],
                                      default=['Brazil', 'England', 'India', 'Turkey', 'United States of America'])
df1 = df1.loc[df1['Country Name'].isin(countryList), :]

st.sidebar.markdown("""---""")
st.sidebar.markdown('#### Powered by FNunes')

# Layout principal
# https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.header(':earth_americas: Country View')
with st.container():
  # Quantidade de restaurantes registrados por país, gráfico de barras.
  dfCountry = df1.loc[:, ['Country Name', 'Restaurant ID']].groupby('Country Name').count()
  dfCountry = dfCountry.sort_values('Restaurant ID', ascending=False).reset_index()
  dfCountry.rename(columns = {'Country Name': 'Country', 'Restaurant ID': 'Number of Restaurants'}, inplace=True)
  st.plotly_chart(px.bar(dfCountry, x='Country', y='Number of Restaurants', title='Qty of Restaurants by Country'), use_container_width=True)

with st.container():
  # Quantidade de cidades registradas por país, gráfico de barras.
  dfCountry = df1.loc[:, ['Country Name', 'City']].drop_duplicates()
  dfCountry = dfCountry.groupby('Country Name').count()
  dfCountry = dfCountry.sort_values('City', ascending=False).reset_index()
  dfCountry.rename(columns = {'Country Name': 'Country', 'City': 'Qty of Cities'}, inplace=True)
  st.plotly_chart(px.bar(dfCountry, x='Country', y='Qty of Cities', title='Qty of Cities by Country'), use_container_width=True)
  
with st.container():
  col1, col2 = st.columns(2)
  with col1:
    # Gráfico de barras com a média de avaliações feitas por país.
    dfCountry = df1.loc[:, ['Country Name', 'Votes']]
    dfCountry = dfCountry.groupby('Country Name').mean().reset_index()
    dfCountry = dfCountry.sort_values('Votes', ascending=False).reset_index(drop=True)
    dfCountry.rename(columns = {'Country Name': 'Country'}, inplace=True)
    st.plotly_chart(px.bar(dfCountry, x='Country', y='Votes', title='Qty of Votes by Country'), use_container_width=True)
  with col2:
    # Gráfico de barras com a média de um prato para duas pessoas por país.
    dfCountry = df1.loc[:, ['Country Name', 'Price in Dollar for two']]
    dfCountry = dfCountry.groupby('Country Name').mean()
    dfCountry = dfCountry.sort_values('Price in Dollar for two', ascending=False).reset_index()
    dfCountry.rename(columns = {'Country Name': 'Country', 'Price in Dollar for two': 'USD Price for Two'}, inplace=True)
    st.plotly_chart(px.bar(dfCountry, x='Country', y='USD Price for Two', title='Average USD Price for Two'), use_container_width=True)