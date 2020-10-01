#Importar librerias
import speech_recognition as sr
import pandas as pd
import rapidfuzz as rf
from scipy.spatial.distance import pdist       
from scipy.spatial.distance import squareform
import requests
from io import BytesIO
import numpy as np
from PIL import Image, ImageDraw
import folium
import ast
import pyttsx3
import time
import re
import plotly.graph_objects as go
from IPython.display import HTML
from IPython.core.display import display

#print('Librerias cargadas...')

#cargar configuracions
engine = pyttsx3.init()
engine.setProperty("voice", engine.getProperty("voices")[31].id)
engine.setProperty('rate', 200)
r = sr.Recognizer()
terminal_output = open('/dev/stdout', 'w')

#llamamos csvs con los datos
cities_lst = pd.read_csv('../data/cities_for_user_input.csv') #ciudades con diferentes nombres
users = pd.read_csv('../data/user_cities.csv') #csv de viajeros y las ciudades visitadas escrapeado de Nomad list
cities = pd.read_csv('../data/nomadlist_cities.csv') #tabla con todas las ciudades
ruta_prueba = pd.read_csv('../data/ruta_ejemplo.csv') #cargamos una ruta de prueba
rec = ['Queretaro, Mexico', 'Guadalajara, Mexico', 'Bangkok, Thailand', 'Hanoi, Vietnam', 'Mexico City, Mexico', 'Puerto Vallarta, Mexico', 'Chiang Mai, Thailand', 'Chiang Rai, Thailand'] #ejemplo de ciudades recomendadas


#cargando archivos
with open('stopwords_es.txt', 'r') as f:
    sw = [line.strip() for line in f]

#función de micrófono
def microfono(limite=15):
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        try:
            print('Escuchando...')
            audio = r.listen(source, phrase_time_limit=limite, timeout=2)
            text = r.recognize_google(audio, language="es-en")
            print("USUARIO: {}\n".format(text.capitalize()))
            return text
        except:
            lap_speak("No entendí lo que dices, por favor, repítelo.")
            return microfono()

#función para que la computadora hable
def lap_speak(texto):
    print(f'TRIPTY: {texto}\n')
    engine.say(texto)
    engine.runAndWait()
    return True

#función para escuchar reconocer desde el micrófono la lista de ciudades
def inicio():
    lap_speak('Hola, soy Tripty y voy a ayudarte a planear tu próximo viaje.')
    lap_speak('Para empezar dime algunas ciudades que conoces:')
    
    text = microfono()

    lap_speak("Ya lo tengo. Voy a procesar tu texto. Espera unos segundos.")
    return text

#limpieza de datos
def clean_city_input(text):
    sep_clean = [i for i in text.split(" ") if i not in sw]
    combinaciones = sep_clean + [e+' '+sep_clean[i+1] for i,e in enumerate(sep_clean) if i+1<len(sep_clean)]
    return combinaciones

#función para generar el match de las ciudades en una sola ejecución
def find_best_match(misspelled, uso='inicio'):
    lista = [x.lower() for x in list(cities_lst["City"])]
        
    #lista con las ciudades finales
    input_user = []
    for i in misspelled:
        closest, ratio = rf.process.extractOne(i.lower(), lista)
        indice = lista.index(closest)
        city_country = cities_lst.loc[indice,'City-Country_EN']
        #print(i, city_country, ratio)
        if ratio>90 and city_country not in input_user:
            input_user.append(city_country)
    #print(input_user)
    if uso == 'inicio':
        lap_speak(f"Veo que te gusta viajar! Encontré {len(input_user)} ciudades en el texto que me dijiste. Vamos con las recomendaciones!")
    return input_user

#función para generar las recomendaciones en una sola ejecución
def reco_cities(new_user_lst):
    lap_speak(f"Estoy buscando algunos viajeros similares a ti... Veamos que otras ciudades conocen para poder recomendarte.")

    #creamos una pivot table en donde pongamos todas las ciudades frente a todos los usuarios
    cities_users = pd.pivot_table(users,
                   index = "City-Country",
                   columns = "user",
                   values = "Time (days)").fillna(0)
    
    #vamos a reemplazar los valores de días con 1 y 0 si es que fue o no algún lugar 
    for i in cities_users.columns:
        cities_users.loc[cities_users[i]>0,i]=1
    
    #ingresa ciudades de nuevo usuario y creamos su data frame
    new_user = pd.DataFrame(index=set(new_user_lst))
    new_user['new user'] = 1
    
    #agregamos ese usuario a la pivot table de ciudades contra usuarios
    cities_users['new user'] = new_user
    cities_users.fillna(0, inplace=True)
    
    #creamos una matriz de similitud entre usuarios. Se va a usar la metrica de Jaccard
    distances = pd.DataFrame(1/(1 + squareform(pdist(cities_users.T, 'jaccard'))), 
                             index=cities_users.columns, columns=cities_users.columns)
    
    #generamos las recomendaciones para el usuario
    final_rec = []
    count = 1
    while len(final_rec)<10:
        similar = distances['new user'].sort_values(ascending=False)[1:count+1]
        recc_cities = users[users['user'].isin(similar.index)].groupby('City-Country').sum('Time (days)').sort_values(ascending=False, by='Time (days)')
        for i in recc_cities.index:
            if i not in new_user_lst and i not in final_rec:
                final_rec.append(i)
        count += 1
        
    lap_speak(f"Estas son las 10 ciudades más recomendadas para que conozcas:")

    for i,e in enumerate(final_rec[:10]):
        print(f'                   {i+1}. {e}')
        time.sleep(0.5)
    print('         ')
    return final_rec[:10]

#función para recortar imagenes para mapa de folium
def crop_image(url,name):
    #llamamos el url de la imagen
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    width, height = im.size   # Get dimensions

    #recortamos la imagen cuadrada
    if height<width:
        new_s = height
    else:
        new_s = width

    left = (width - new_s)/2
    top = (height - new_s)/2
    right = (width + new_s)/2
    bottom = (height + new_s)/2

    # Crop the center of the image
    img = im.crop((left, top, right, bottom))
    
    # Open the input image as numpy array, convert to RGB
    npImage=np.array(img)
    h,w=img.size

    # Create same size alpha layer with circle
    alpha = Image.new('L', img.size,0)
    draw = ImageDraw.Draw(alpha)
    draw.pieslice([0,0,h,w],0,360,fill=255)

    # Convert alpha Image to numpy array
    npAlpha=np.array(alpha)

    # Add alpha layer to RGB
    npImage=np.dstack((npImage,npAlpha))

    # Save with alpha
    path = f'../Images/Cities/{name}.png'
    image_crop = Image.fromarray(npImage).save(path)
    
    return path

#función para generar mapa con las ciudades recomendadas
def mapa_reco(lst=rec):
    lap_speak("Voy a poner estas ciudades en un mapa para que las puedas ver mejor:")

    #generamos data frame con las ciudades recomendadas
    reco_cities = cities[cities['City-Country'].isin(lst)].reset_index(drop=True)
    
    points = []
    for i in range(len(reco_cities)):
        points.append(tuple([reco_cities.loc[i,"lat"],reco_cities.loc[i,"lng"]]))
        
    ave_lat = sum(p[0] for p in points)/len(points)
    ave_lon = sum(p[1] for p in points)/len(points)

    #generamos mapa
    mapa = folium.Map(width=800,height=400, location=[ave_lat, ave_lon], zoom_start=1.5)

    #pintamos las imagenes en los marcadores de cada ciudad
    for i in range(len(reco_cities)):
        try:
            icon = folium.features.CustomIcon(icon_image=f"../Images/Cities/{reco_cities.loc[i,'City-Country']}.png" ,icon_size=(80,80))
        except:
            try:
                icon_path = crop_image(reco_cities.loc[i,'Photo'],reco_cities.loc[i,'City-Country'])
                icon = folium.features.CustomIcon(icon_image=icon_path ,icon_size=(80,80))
            except:
                icon_path = crop_image('https://www.iscr.com/website/wp-content/themes/consultix/images/no-image-found-360x250.png','no_image')
                icon = folium.features.CustomIcon(icon_image=icon_path ,icon_size=(80,80))
                
        folium.Marker([reco_cities.loc[i,"lat"],reco_cities.loc[i,"lng"]],
                      icon=icon,
                      tooltip = reco_cities.loc[i,'City-Country'],
                      popup = f"Travelers City Score: {reco_cities.loc[i,'Overall Score']}/5").add_to(mapa)
    display(mapa)
    return True

#funcion para definir el comienzo de una ruta
def definir_start():
        lap_speak('¿En qué ciudad quieres comenzar? Puedes seleccionar una de las ciudades que te recomendé u otra.')

        text = microfono(limite=5)

        clean_input = clean_city_input(text)
        start = find_best_match(clean_input, uso='otro')

        try:
            lap_speak(f"{start[0]} es una buena elección.")
            return start[0]
        except:
            lap_speak(f"No logré identificar esa ciudad, intentemos otra vez.")
            return definir_start()

        
    
#funcion para definir la duración del viaje
def definir_tiempo():
    lap_speak('¿Alrededor de cuántos días quieres que dure tu viaje? Yo te recomiendo que sea de 20 a 30 días.')

    text = microfono(limite=5)
    dias = re.findall('\d+',text)

    try:
        dia_final = int(dias[0])
        if dia_final<=15:
            lap_speak(f"{dia_final} son pocos días, será un tour rápido.")
        elif dia_final<=30:
            lap_speak(f"{dia_final} días están bien para conocer.")
        else:
            lap_speak(f"En {dia_final} puedes conocer mucho, excelente.")
        return dia_final

    except:
        lap_speak("No logré identificar ese número de días, intentemos otra vez.")
        return definir_tiempo()

#función para generar la ruta recomendada
def ruta_recomendada():
    lap_speak('Ahora te voy a recomendar un tour de algunas ciudades.')

    start = definir_start()
    wanted_days = definir_tiempo()

    #creamos el dataframe con la ciudad de inicio
    ruta = cities[cities['City-Country']==start].reset_index(drop=True)
    
    indice = 0
    days = 0

    lap_speak('Estoy procesando todos los datos. ¡Será una excelente ruta!')

    #agregamos las proximas ciudades
    while days<wanted_days:
        
        cerca = list(ast.literal_eval(ruta.loc[indice,'Closest Cities (km)']).keys())
        if len(ruta)<2:
            for i in cerca:
                if i not in list(ruta['City-Country']):
                    ruta = ruta.append(cities[cities['City-Country']==i]).reset_index(drop=True)
                    break
        else:
            sentido_hor = ruta.loc[indice-1,'lng']<ruta.loc[indice,'lng'] #si es true, va a la derecha
            sentido_ver = ruta.loc[indice-1,'lat']<ruta.loc[indice,'lat'] #si es true, va para arriba
            anexado = False
            for i in cerca:
                if i not in list(ruta['City-Country']):
                    lng_i = list(cities[cities['City-Country']==i]['lng'].values)[0]
                    if sentido_hor:
                        if ruta.loc[indice,'lng']<lng_i:
                            ruta = ruta.append(cities[cities['City-Country']==i]).reset_index(drop=True)
                            anexado = True
                            break
                    else:
                        if ruta.loc[indice,'lng']>lng_i:
                            ruta = ruta.append(cities[cities['City-Country']==i]).reset_index(drop=True)
                            anexado = True
                            break
            if anexado==False:
                for i in cerca:
                    if i not in list(ruta['City-Country']):
                        lat_i = list(cities[cities['City-Country']==i]['lat'].values)[0]
                        if sentido_ver:
                            if ruta.loc[indice,'lat']<lat_i:
                                ruta = ruta.append(cities[cities['City-Country']==i]).reset_index(drop=True)
                                anexado = True
                                break
                        else:
                            if ruta.loc[indice,'lat']>lat_i:
                                ruta = ruta.append(cities[cities['City-Country']==i]).reset_index(drop=True)
                                anexado = True
                                break
            if anexado==False:
                lap_speak(f'No tengo suficientes ciudades cerca de {start} para el número de días que quieres, pero te voy a hacer una propuesta.')
                break
        indice+=1
        days = int(sum(list(ruta['Average days'])))
        ruta['Presupuesto'] = ruta['Average days']*ruta['Cost/day (USD)']
        presupuesto = int(sum(list(ruta['Presupuesto'])))

    lap_speak(f'Ya tengo tu viaje listo, según información de otros usuarios, lo recomendable es que sea de {days} días. Podrás conocer {len(ruta)} ciudades en ese tiempo y el presupuesto aproximado es de ${presupuesto}.')

    lap_speak(f'Aquí está el itinerario completo que yo te recomiendo:')

    dias = 1
    for i in range(len(ruta)):
        print(f"                   Día {int(dias)}:   {ruta.loc[i,'City-Country']}")
        dias += ruta.loc[i,'Average days']
        time.sleep(0.5)
    print(f"                   Día {int(dias)-1}:   Fin del viaje :(\n")
    return ruta

#funcion para generar mapa de la ruta
def mapa_ruta(df=ruta_prueba):
    lap_speak(f"Enseguida voy a poner la ruta en un mapa para que la puedas ver mejor. Me tardaré un poco, son varias ciudades.")
  
    points = []
    for i in range(len(df)):
        points.append(tuple([df.loc[i,"lat"],df.loc[i,"lng"]]))
        
    ave_lat = sum(p[0] for p in points)/len(points)
    ave_lon = sum(p[1] for p in points)/len(points)

    #generamos mapa
    mapa = folium.Map(width=800,height=400,location=[ave_lat, ave_lon], zoom_start=4)

    #pintamos las imagenes en los marcadores de cada ciudad
    for i in range(len(df)):
        try:
            icon = folium.features.CustomIcon(icon_image=f"../Images/Cities/{df.loc[i,'City-Country']}.png" ,icon_size=(50,50))
        except:
            try:
                icon_path = crop_image(df.loc[i,'Photo'],df.loc[i,'City-Country'])
                icon = folium.features.CustomIcon(icon_image=icon_path ,icon_size=(50,50))
            except:
                icon_path = crop_image('https://www.iscr.com/website/wp-content/themes/consultix/images/no-image-found-360x250.png','no_image')
                icon = folium.features.CustomIcon(icon_image=icon_path ,icon_size=(50,50))
                
        folium.Marker([df.loc[i,"lat"],df.loc[i,"lng"]],
                      icon=icon,
                      tooltip = df.loc[i,'City-Country'],
                      popup = f"Travelers City Score: {df.loc[i,'Overall Score']}/5").add_to(mapa)
    #fadd lines
    folium.PolyLine(points, color="blue", weight=2.5, opacity=1).add_to(mapa)

    display(mapa)
    return True

#función para graficar las temperaturas promedio
def temp_graph(ruta=ruta_prueba):
    lap_speak('Te voy a mostrar la temperatura promedio de esta ruta por mes. Así podras definir la fecha del viaje.')
    
    #sacamos las columnas de temperatura del df
    temp_cols = [i for i in ruta.columns if i.startswith('Temp')]
    new_cols = [i.split(' ')[-1] for i in temp_cols]
    
    #generamos un nuevo dataframe de temperaturas
    temps_df = ruta[temp_cols].T.set_index([new_cols])
    
    #creamos columna con el promedio de la temperatura de cada mes
    tama = temps_df.shape[1]
    for e,i in enumerate(new_cols):
        promedio = sum(temps_df.iloc[e,:tama])/len(temps_df.iloc[e,:tama])
        temps_df.loc[i,'Average Temp (°C)'] = round(promedio,2)
    
    #usamos plotly para gráficar la linea
    fig = go.Figure(data=go.Scatter(
        x=temps_df.index, 
        y=temps_df['Average Temp (°C)']))
    
    #configuramos el título y labels del gráfico
    fig.update_layout(
        title={
            'text': "Temperatura promedio por mes (itinerario recomendado)",
            'y':0.88,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title="Months",
        yaxis_title="Average Temp (°C)")
    
    #retornamos el gráfico
    fig.show()
    
    #sacamos el mes más frio y caliente
    meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
    
    maxi = temps_df[temps_df['Average Temp (°C)']==temps_df['Average Temp (°C)'].max()]
    mini = temps_df[temps_df['Average Temp (°C)']==temps_df['Average Temp (°C)'].min()]

    temp_max = (meses[new_cols.index(maxi.index[0])],round(maxi['Average Temp (°C)'].values[0],2))
    temp_min = (meses[new_cols.index(mini.index[0])],round(mini['Average Temp (°C)'].values[0],2))
    
    time.sleep(2)
    lap_speak(f'El mes más frio es {temp_min[0]}, su promedio es {temp_min[1]} grados Celsius y el más caluroso es {temp_max[0]} con {temp_max[1]} grados Celsius.')

    return True

#función para graficar las variables extras
def extra_graph(ruta=ruta_prueba):
    lap_speak('Para terminar, mira este gráfico con 20 variables para que puedas evaluar mejor la ruta y comprar tus vuelos. Vienen algunas como, qué tan caminables o seguras son las ciudades de la ruta.')

    new_cols = ['Overall Score', 'Quality of life score','Family score','Fun', 'Safety', 
           'Education level', 'English speaking', 'Walkability', 'Peace', 'Traffic safety',
           'Hospitals', 'Happiness', 'Nightlife', 'Free WiFi in city', 'Places to work from',
           'Friendly to foreigners', 'Freedom of speech', 'Racial tolerance', 'Female friendly',
           'LGBTQ friendly']

    #generamos un nuevo dataframe de temperaturas
    temps_df = ruta[new_cols].T

    #creamos columna con el promedio de la temperatura de cada mes
    tama = temps_df.shape[1]
    for e,i in enumerate(new_cols):
        promedio = sum(temps_df.iloc[e,:tama])/len(temps_df.iloc[e,:tama])
        temps_df.loc[i,'Average (/5)'] = round(promedio,2)

    #usamos plotly para gráficar la linea
    fig = go.Figure(data=go.Scatter(
        x=temps_df.index, 
        y=temps_df['Average (/5)']))

    #configuramos el título y labels del gráfico
    fig.update_layout(
        title={
            'text': "Puntaje de la ruta",
            'y':0.88,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis_title="Variables",
        yaxis_title="Promedio (/5)")

    #retornamos el gráfico
    fig.show()

    lap_speak('¡Buen viaje! Estoy lista para ayudarte cuando tengas tu siguiente aventura. Bye Bye.')

    #imagen de cierre
    imagen = '<center><img src="../Images/cierre.jpg" width="240" height="240" align="center"/></center>'
    display(HTML(imagen))

    return True

#función para despertar a TRIPTY
def continuar(palabra):

    if palabra == 'despierta':
        palabra = 'despier'
        lap_speak('Voy a dormir un momento para que puedas seguir contando de tu proyecto al público. En cualquier momento puedes decir DESPIERTA TRIPTY para que continuemos.')
        salida = 'Ya desperté, fue una buena siesta...'
    elif palabra == 'continuar':
        palabra = 'conti'
        lap_speak('Di continuar cuando quieras que sigamos...')
        salida = 'Vamos a continuar...'

    texto = []
    text = ''
    r = sr.Recognizer()
    with sr.Microphone() as source:
        #r.adjust_for_ambient_noise(source)
        while palabra not in text.lower():
            try:
                audio = r.listen(source, phrase_time_limit=2,timeout=1)
                text = r.recognize_google(audio, language="es-en")
                print(text, file=terminal_output)
            except:
                pass

    lap_speak(salida)
    return 'Continuar'

#función principal
def tripty():
    user_input = inicio()
    clean_input = clean_city_input(user_input)
    cities_input = find_best_match(clean_input)
    recomendaciones = reco_cities(cities_input)
    recomendados_mapa = mapa_reco(lst=recomendaciones)
    siesta = continuar('despierta')
    ruta = ruta_recomendada()
    ruta_mapa = mapa_ruta(df=ruta)
    espera = continuar('continuar')
    grafico_temp = temp_graph(ruta=ruta)
    espera = continuar('continuar')
    cierre = extra_graph(ruta=ruta)
    return '¡Buen viaje!'