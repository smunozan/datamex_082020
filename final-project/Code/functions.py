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
#print('Librerias cargadas...')

#cargar configuracions
engine = pyttsx3.init()
engine.setProperty("voice", engine.getProperty("voices")[31].id)
engine.setProperty('rate', 200)
r = sr.Recognizer()

def iniciar_conv():
    print('TRIPTY: Hola, soy Tripty y voy a ayudarte a planear tu próximo viaje.\n')
    engine.say("Hola, soy Tripty y voy a ayudarte a planear tu próximo viaje.")
    engine.runAndWait()
    return mic_rec()

#función para escuchar reconocer desde el micrófono la lista de ciudades
def mic_rec():
    with sr.Microphone() as source:
        print('TRIPTY: Para empezar dime algunas ciudades que conoces:\n')
        engine.say("Para empezar dime algunas ciudades que conoces:")
        engine.runAndWait()
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="es-en")
            print("USUARIO: {}\n".format(text))
            time.sleep(2)
            print("TRIPTY: Ya lo tengo. Voy a buscar otros viajeros similares a ti y te recomendaré nuevas ciudades para que vayas. Espera unos segundos.\n")
            engine.say("Ya lo tengo. Voy a buscar otros viajeros similares a ti y te recomendaré nuevas ciudades para que vayas. Espera unos segundos.")
            engine.runAndWait()
            return text
        except:
            print("TRIPTY: No entendí lo que dices, comencemos nuevamente.\n")
            engine.say("No entendí lo que dices, comencemos nuevamente.")
            engine.runAndWait()
            mic_rec()

#limpieza de datos
def clean_city_input(text):
    with open('stopwords_es.txt', 'r') as f:
        sw = [line.strip() for line in f]
    sep_clean = [i for i in text.split(" ") if i not in sw]
    combinaciones = sep_clean + [e+' '+sep_clean[i+1] for i,e in enumerate(sep_clean) if i+1<len(sep_clean)]
    return combinaciones

#función para generar el match de las ciudades en una sola ejecución
def find_best_match(misspelled, uso='inicio'):
    #llamamos el csv con los datos
    cities_lst = pd.read_csv('../data/cities_for_user_input.csv')
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
        print(f"TRIPTY: Veo que te gusta viajar! Encontré {len(input_user)} ciudades en el texto que me dijiste. Vamos con las recomendaciones!\n")
        engine.say(f"Veo que te gusta viajar! Encontré {len(input_user)} ciudades en el texto que me dijiste. Vamos con las recomendaciones!")
        engine.runAndWait()
    return input_user

#función para generar las recomendaciones en una sola ejecución
def reco_cities(new_user_lst):
    #print('Cargando datos de otros viajeros...')
    print(f"TRIPTY: Estoy buscando algunos viajeros similares a ti... Veamos que otras ciudades les gusta.\n")
    engine.say(f"Estoy buscando algunos viajeros similares a ti... Veamos que otras ciudades les gusta.")
    engine.runAndWait()

    #importamos csv de viajeros y las ciudades visitadas escrapeado de Nomad list
    users = pd.read_csv('../data/user_cities.csv')

    #creamos una pivot table en donde pongamos todas las ciudades frente a todos los usuarios
    cities_users = pd.pivot_table(users,
                   index = "City-Country",
                   columns = "user",
                   values = "Time (days)").fillna(0)
    
    #vamos a reemplazar los valores de días con 1 y 0 si es que fue o no algún lugar 
    for i in cities_users.columns:
        cities_users.loc[cities_users[i]>0,i]=1
    
    #print('Verificando viajeros similares...')
    
    #ingresa ciudades de nuevo usuario y creamos su data frame
    new_user = pd.DataFrame(index=set(new_user_lst))
    new_user['new user'] = 1
    
    #agregamos ese usuario a la pivot table de ciudades contra usuarios
    cities_users['new user'] = new_user
    cities_users.fillna(0, inplace=True)
    
    #creamos una matriz de similitud entre usuarios. Se va a usar la metrica de Jaccard
    distances = pd.DataFrame(1/(1 + squareform(pdist(cities_users.T, 'jaccard'))), 
                             index=cities_users.columns, columns=cities_users.columns)
    
    #print('Generando recomendaciones...')
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
        
    print(f"TRIPTY: Estas son las 10 ciudades más recomendadas para que conozcas:\n")
    engine.say(f"Estas son las 10 ciudades más recomendadas para que conozcas, espero que me lleves contigo.")
    engine.runAndWait()
    for i,e in enumerate(final_rec[:10]):
        print(f'                   {i+1}. {e}')
        time.sleep(0.5)
    print('         ')
    return final_rec[:10]

#función para recortar imagenes para mapa de folium
def crop_image(url,name):
    #llamamos elurl de la imagen
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
def mapa_reco(lst):
    print(f"TRIPTY: Voy a poner estas ciudades en un mapa para que las puedas ver mejor:")
    engine.say(f"Voy a poner estas ciudades en un mapa para que las puedas ver mejor:")
    engine.runAndWait()

    #cargamos la tabla con todas las ciudades
    cities = pd.read_csv('../data/nomadlist_cities.csv')

    #generamos data frame con las ciudades recomendadas
    reco_cities = cities[cities['City-Country'].isin(lst)].reset_index(drop=True)
    
    points = []
    for i in range(len(reco_cities)):
        points.append(tuple([reco_cities.loc[i,"lat"],reco_cities.loc[i,"lng"]]))
        
    ave_lat = sum(p[0] for p in points)/len(points)
    ave_lon = sum(p[1] for p in points)/len(points)

    #generamos mapa
    mapa = folium.Map(location=[ave_lat, ave_lon], zoom_start=1.5)


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

    return mapa

#funcion para definir el comienzo de una ruta
def definir_start():
        print('TRIPTY: ¿En qué ciudad quieres comenzar? Puedes seleccionar una de las ciudades que te recomendé u otra.\n')
        engine.say("¿En qué ciudad quieres comenzar? Puedes seleccionar una de las ciudades que te recomendé u otra.")
        engine.runAndWait()

        with sr.Microphone() as source:
            engine.runAndWait()
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language="es-en")
                print("USUARIO: {}\n".format(text))
                clean_input = clean_city_input(text)
                start = find_best_match(clean_input, uso='otro')
                #time.sleep(2)
                print(f"TRIPTY: {start[0]} es una buena elección.\n")
                engine.say(f"{start[0]} es una buena elección.")
                engine.runAndWait()
                return start[0]
            except:
                print("TRIPTY: No entendí lo que dices, comencemos nuevamente.\n")
                engine.say("No entendí lo que dices, comencemos nuevamente.")
                engine.runAndWait()
                definir_start()
    
#funcion para definir la duración del viaje
def definir_tiempo():
        print('TRIPTY: ¿Alrededor de cuántos días quieres que dure tu viaje? Yo te recomiendo que sea de 20 a 30 días.\n')
        engine.say("¿Alrededor de cuántos días quieres que dure tu viaje? Yo te recomiendo que sea de 20 a 30 días.")
        engine.runAndWait()

        with sr.Microphone() as source:
            engine.runAndWait()
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language="es-en")
                print("USUARIO: {}\n".format(text))
                dias = re.findall('\d+',text)
                #time.sleep(2)
                if int(dias[0])<=15:
                    print(f"TRIPTY: {dias[0]} son pocos días, será un tour rápido.\n")
                    engine.say(f"{dias[0]} son pocos días, será un tour rápido.")
                    engine.runAndWait()
                elif int(dias[0])<=30:
                    print(f"TRIPTY: {dias[0]} días están bien para conocer.\n")
                    engine.say(f"{dias[0]} días están bien para conocer.")
                    engine.runAndWait()
                else:
                    print(f"TRIPTY: {dias[0]} son bastantes días, va a ser un buen viaje.\n")
                    engine.say(f"{dias[0]} son bastantes días, va a ser un buen viaje.")
                    engine.runAndWait()
                return int(dias[0])
            except:
                print("TRIPTY: No entendí lo que dices, comencemos nuevamente.\n")
                engine.say("No entendí lo que dices, comencemos nuevamente.")
                engine.runAndWait()
                definir_tiempo()

#función para generar la ruta recomendada
def ruta_recomendada():
    print('TRIPTY: Ahora te voy a recomendar un tour de algunas ciudades.\n')
    engine.say("Ahora te voy a recomendar un tour de algunas ciudades.")
    engine.runAndWait()

    start = definir_start()
    wanted_days = definir_tiempo()
    
    #cargamos la tabla con todas las ciudades
    cities = pd.read_csv('../data/nomadlist_cities.csv')

    #creamos el dataframe con la ciudad de inicio
    ruta = cities[cities['City-Country']==start].reset_index(drop=True)

    indice = 0
    days = 0

    print('TRIPTY: Estoy procesando todos los datos. ¡Será una excelente ruta!\n')
    engine.say("Estoy procesando todos los datos. ¡Será una excelente ruta!")
    engine.runAndWait()

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
                print(f'TRIPTY: No tengo suficientes ciudades cerca de {start} para el número de días que quieres, pero te voy a hacer una propuesta.\n')
                engine.say(f'No tengo suficientes ciudades cerca de {start} para el número de días que quieres, pero te voy a hacer una propuesta.')
                engine.runAndWait()
                break
        indice+=1
        days = int(sum(list(ruta['Average days'])))

    print(f'TRIPTY: Ya tengo tu viaje listo, según información de otros usuarios, lo recomendable es que sea de {days} días. Podrás conocer {len(ruta)} ciudades en ese tiempo.\n')
    engine.say(f'Ya tengo tu viaje listo, según información de otros usuarios, lo recomendable es que sea de {days} días. Podrás conocer {len(ruta)} ciudades en ese tiempo.')
    engine.runAndWait()

    print(f'TRIPTY: Aquí está el itinerario completo que yo te recomiendo:\n')
    engine.say(f'Aquí está el itinerario completo que yo te recomiendo:')
    engine.runAndWait()

    dias = 1
    for i in range(len(ruta)):
        print(f"Día {int(dias)}:   {ruta.loc[i,'City-Country']}")
        dias += ruta.loc[i,'Average days']
    print(f"Día {int(dias)}:   Fin del viaje :(")
    return ruta

#funcion para generar mapa de la ruta
def mapa_ruta(df):
    print(f"TRIPTY: Enseguida voy a poner la ruta en un mapa para que la puedas ver mejor. Me tardaré un poco, son varias ciudades.")
    engine.say(f"Enseguida voy a poner la ruta en un mapa para que la puedas ver mejor. Me tardaré un poco, son varias ciudades.")
    engine.runAndWait()

    #cargamos la tabla con todas las ciudades
    cities = pd.read_csv('../data/nomadlist_cities.csv')
    
    points = []
    for i in range(len(df)):
        points.append(tuple([df.loc[i,"lat"],df.loc[i,"lng"]]))
        
    ave_lat = sum(p[0] for p in points)/len(points)
    ave_lon = sum(p[1] for p in points)/len(points)

    #generamos mapa
    mapa = folium.Map(location=[ave_lat, ave_lon], zoom_start=4)


    #pintamos las imagenes en los marcadores de cada ciudad
    for i in range(len(df)):
        try:
            icon = folium.features.CustomIcon(icon_image=f"../Images/Cities/{df.loc[i,'City-Country']}.png" ,icon_size=(80,80))
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
    
    return mapa

#función para despertar a TRIPTY
def despertar_tripty():
    time.sleep(2)
    print('TRIPTY: Voy a dormir un momento para que puedas seguir contando de tu proyecto al público. En cualquier momento puedes decir DESPIERTA TRIPTY para que continuemos.\n')
    engine.say("Voy a dormir un momento para que puedas seguir contando de tu proyecto al público. En cualquier momento puedes decir DESPIERTA TRIPTY para que continuemos.")
    engine.runAndWait()

    texto = []
    while 'despierta' not in texto:
        with sr.Microphone() as source:
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio, language="es-en")
                texto = clean_city_input(text)
                
            except:
                pass
    print('TRIPTY: Ya desperté, fue una buena siesta...\n')
    engine.say("Ya desperté, fue una buena siesta...")
    engine.runAndWait()
    return 'Tripty despierta'

def tripty():
    user_input = iniciar_conv()
    clean_input = clean_city_input(user_input)
    cities_input = find_best_match(clean_input)
    recomendaciones = reco_cities(cities_input)
    recomendados_mapa = mapa_reco(recomendaciones)
    display(recomendados_mapa)
    siesta = despertar_tripty()
    ruta = ruta_recomendada()
    ruta_mapa = mapa_ruta(ruta)
    display(ruta_mapa)