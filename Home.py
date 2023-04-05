import folium as fo
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import plotly.express as px
import streamlit as st
from streamlit_folium import folium_static

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

colors = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "darkred",
}

def get_color_name(color_code):
  return colors[color_code]

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
  
  # Acertando uma localização errada em um restaurante na Índia.
  df1.loc[(df1['City']=='Kochi') & (df1['Restaurant Name']=='KFC') & (df1['Longitude']==0.0), 'Longitude']=76.349474

  # Cria a coluna com o preço em dólar baseado na função definida acima.
  df1['Price in Dollar for two'] = df1.loc[:, ['Currency', 'Average Cost for two']].apply(lambda x: convert_to_dollar(x['Currency'], x['Average Cost for two']), axis=1)
  
  # Troca a coluna com a cor em código para descrição baseada na função definida acima.
  df1['Rating color'] = df1.loc[:, 'Rating color'].apply(lambda x: get_color_name(x))

  return df1

# Lendo o arquivo e limpando o data frame
df = pd.read_csv('zomato.csv')
df1 = clear_data(df)

# Streamlit
st.set_page_config(page_title='Home',
                   layout='wide',
                   initial_sidebar_state='expanded',
                   page_icon=':house:')

# Sidebar
#st.sidebar.image(Image.open('pineapple.jpg'), width=60)
#st.sidebar.markdown('# Restaurants Review')
#st.sidebar.markdown("""---""")
st.sidebar.markdown('## Filter')
countryList = st.sidebar.multiselect('Which countries do you want to view?',
                                      ['Australia', 'Brazil', 'Canada', 'England', 'India', 'Indonesia', 'New Zeland',
                                       'Philippines', 'Qatar', 'Singapure', 'South Africa', 'Sri Lanka', 'Turkey',
                                       'United Arab Emirates', 'United States of America'],
                                      default=['Brazil', 'England', 'Turkey'])
df1 = df1.loc[df1['Country Name'].isin(countryList), :]


st.sidebar.markdown("""---""")
st.sidebar.markdown('#### Powered by FNunes')
#with st.sidebar:
#  st.download_button('Download Source Data', pd.read_csv('zomato.csv'), file_name='restaurants.csv')

# Body
st.header(':house: Restaurants Review')
st.write('Restaurants Review Main Page')

with st.container():
  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    label = 'Restaurants'
    value = df1['Restaurant ID'].nunique()
    st.metric(label, value)
  with col2:
    label = 'Countries'
    value = df1['Country Code'].nunique()
    st.metric(label, value)
  with col3:
    label = 'Cities'
    value = df1['City'].nunique()
    st.metric(label, value)
  with col4:
    label = 'Votes'
    value = df1['Votes'].sum()
    st.metric(label, value)
  with col5:
    label = 'Cuisines'
    value = df1['Cuisines'].nunique()
    st.metric(label, value)

with st.container():
  # Mapa
  # https://nbviewer.org/github/bibmartin/folium/blob/issue288/examples/Popups.ipynb
  # https://towardsdatascience.com/use-html-in-folium-maps-a-comprehensive-guide-for-data-scientists-3af10baf9190#430e
  # https://www.python-graph-gallery.com/
  # https://fontawesome.com/v4/icons/
  dfDataPlot = df1.copy()

  #iframe = fo.element.IFrame(html=html, width=500, height=300)
  #popup = fo.Popup(iframe, max_width=1024)
  #popup = fo.Popup(fo.Html(html, script=True), max_width=500)

  map = fo.Map([df1['Latitude'].mean(), df1['Longitude'].mean()], zoom_start=2)
  cluster = fo.plugins.MarkerCluster()
  cluster.add_to(map)
  for i, ponto in dfDataPlot.iterrows():
      html = '<b>' + ponto['Restaurant Name'] + '</b><br/>'
      html = html + ponto['Cuisines'] + '<br/>'
      html = html + ponto['City'] + ' (' + ponto['Country Name'] + ')<br/><br/>'
      html = html + str(ponto['Average Cost for two']) + ' ' + ponto['Currency'] + '<br/>'
      html = html + 'Rating ' + str(ponto['Aggregate rating'])
      fo.Marker([ponto['Latitude'], ponto['Longitude']],
                popup=fo.Popup(fo.Html(html, script=True), max_width=500),
                icon=fo.Icon(color=ponto['Rating color'], prefix='fa', icon='home')).add_to(cluster)
  folium_static(map, height=600, width=800)
  
  #sw = dfDataPlot[['Latitude', 'Longitude']].min().values.tolist()
  #ne = dfDataPlot[['Latitude', 'Longitude']].max().values.tolist()
  #map.fit_bounds([sw, ne])
