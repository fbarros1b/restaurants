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

def get_metric(df, i):
  label = df.loc[i, 'Restaurant Name']
  value = df.loc[i, 'Aggregate rating']
  helpText = df.loc[i, 'Cuisines'] + ' '
  helpText = helpText + df.loc[i, 'City'] + ' (' + df.loc[i, 'Country Name'] + ') '
  helpText = helpText + 'USD ' + str(dfCuisines.loc[i, 'Price in Dollar for two']) + ' for two'
  return label, value, helpText

st.set_page_config(page_title='Cuisine View',
                   layout='wide',
                   initial_sidebar_state='expanded',
                   page_icon=':knife_fork_plate:')

# Lendo o arquivo e limpando o data frame
df = pd.read_csv('zomato.csv')
df1 = clear_data(df)

# Streamlit
# Barra lateral
#st.sidebar.image(Image.open('pineapple.jpg'), width=60)
#st.sidebar.markdown('# Cuisines View')
#st.sidebar.markdown("""---""")
st.sidebar.markdown('## Filter')
countryList = st.sidebar.multiselect('Which countries do you want to view?',
                                      ['Australia', 'Brazil', 'Canada', 'England', 'India', 'Indonesia', 'New Zeland',
                                       'Philippines', 'Qatar', 'Singapure', 'South Africa', 'Sri Lanka', 'Turkey',
                                       'United Arab Emirates', 'United States of America'],
                                      default=['Brazil', 'England', 'India', 'Turkey', 'United States of America'])
df1 = df1.loc[df1['Country Name'].isin(countryList), :]

st.sidebar.markdown("""---""")

qtyRestaurants = st.sidebar.slider('How many restaurants do you want to see?',
                                   value=10, min_value=3, max_value=20)

st.sidebar.markdown("""---""")

cuisineList = st.sidebar.multiselect('Which cuisines do you want to view?',
                                      df1['Cuisines'].unique(),
                                      default=['Brazilian', 'BBQ', 'Italian', 'Japanese'])
df1 = df1.loc[df1['Cuisines'].isin(cuisineList), :]

st.sidebar.markdown("""---""")

st.sidebar.markdown('#### Powered by FNunes')

# Layout principal
# https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.header(':knife_fork_plate: Cuisine View')
with st.container():
  st.markdown('## Best Restaurants')
  dfCuisines = (df1.loc[:,
                        ['Restaurant ID', 'Restaurant Name', 'Country Name',
                         'City', 'Cuisines', 'Aggregate rating', 'Price in Dollar for two']]
                       .reset_index(drop=True))
  dfCuisines = dfCuisines.sort_values(['Aggregate rating', 'Restaurant ID'], ascending=[False, True]).reset_index(drop=True)
  col0, col1, col2, col3, col4 = st.columns(5, gap='large')
  with col0:
    label, value, helpText = get_metric(dfCuisines, 0)
    st.metric(label, value, help=helpText)
  with col1:
    label, value, helpText = get_metric(dfCuisines, 1)
    st.metric(label, value, help=helpText)
  with col2:
    label, value, helpText = get_metric(dfCuisines, 2)
    st.metric(label, value, help=helpText)
  with col3:
    label, value, helpText = get_metric(dfCuisines, 3)
    st.metric(label, value, help=helpText)
  with col4:
    label, value, helpText = get_metric(dfCuisines, 4)
    st.metric(label, value, help=helpText)

with st.container():
  # Top 10 restaurantes
  dfCuisines = (df1.loc[:,
                        ['Restaurant ID', 'Restaurant Name', 'Country Name', 'City',
                         'Cuisines', 'Price in Dollar for two', 'Aggregate rating', 'Votes']]
                       .reset_index(drop=True))
  dfCuisines = dfCuisines.sort_values(['Aggregate rating', 'Restaurant ID'], ascending=[False, True])
  st.dataframe(dfCuisines.head(qtyRestaurants))

with st.container():
  col1, col2 = st.columns(2)
  with col1:
    # Top melhores culinárias.
    dfCuisines = df1.loc[:, ['Cuisines', 'Aggregate rating']].groupby('Cuisines').mean()
    dfCuisines = dfCuisines.sort_values(['Aggregate rating', 'Cuisines'], ascending=[False, True]).reset_index()
    dfCuisines.rename(columns = {'Aggregate rating': 'Rating', 'Cuisines': 'Cuisine'}, inplace=True)
    st.plotly_chart(px.bar(dfCuisines.head(10), x='Cuisine', y='Rating', title='Best Cuisines'), use_container_width=True)

  with col2:
    # Bottom piores culinárias.
    dfCuisines = df1.loc[:, ['Cuisines', 'Aggregate rating']].groupby('Cuisines').mean()
    dfCuisines = dfCuisines.sort_values(['Aggregate rating', 'Cuisines'], ascending=[True, True]).reset_index()
    dfCuisines.rename(columns = {'Aggregate rating': 'Rating', 'Cuisines': 'Cuisine'}, inplace=True)
    st.plotly_chart(px.bar(dfCuisines.head(10), x='Cuisine', y='Rating', title='Worst Cuisines'), use_container_width=True)