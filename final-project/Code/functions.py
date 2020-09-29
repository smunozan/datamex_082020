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
print('Librerias cargadas...')

#función para escuchar reconocer desde el micrófono
def mic_rec():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak Anything:")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="es-en")
            print("You said: {}".format(text))
            return text
        except:
            print("Sorry could not recognize what you said")
            mic_rec()

#limpieza de datos
def clean_city_input(text):
    with open('stopwords_es.txt', 'r') as f:
        sw = [line.strip() for line in f]
    sep_clean = [i for i in text.split(" ") if i not in sw]
    combinaciones = sep_clean + [e+' '+sep_clean[i+1] for i,e in enumerate(sep_clean) if i+1<len(sep_clean)]
    return combinaciones

#función para generar el match de las ciudades en una sola ejecución
def find_best_match(misspelled):
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
    print(input_user)
    return input_user

#función para generar las recomendaciones en una sola ejecución
def reco_cities(new_user_lst):
    print('Cargando datos de otros viajeros...')

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
    
    print('Verificando viajeros similares...')
    
    #ingresa ciudades de nuevo usuario y creamos su data frame
    new_user = pd.DataFrame(index=set(new_user_lst))
    new_user['new user'] = 1
    
    #agregamos ese usuario a la pivot table de ciudades contra usuarios
    cities_users['new user'] = new_user
    cities_users.fillna(0, inplace=True)
    
    #creamos una matriz de similitud entre usuarios. Se va a usar la metrica de Jaccard
    distances = pd.DataFrame(1/(1 + squareform(pdist(cities_users.T, 'jaccard'))), 
                             index=cities_users.columns, columns=cities_users.columns)
    
    print('Generando recomendaciones...')
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
    print(final_rec[:10])
    return final_rec[:10]

#función para recortar imagenes para mapa de folium
def crop_image(url,name):
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    width, height = im.size   # Get dimensions

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
    #cargamos la tabla con todas las ciudades
    cities = pd.read_csv('../data/nomadlist_cities.csv')

    #generamos data frame con las ciudades recomendadas
    reco_cities = cities[cities['City-Country'].isin(lst)].reset_index(drop=True)

    #generamos mapa
    mapa=folium.Map([31.653830718,9.17416597],zoom_start=2)

    #pintamos las imagenes en los marcadores de cada ciudad
    for i in range(len(reco_cities)):
        try:
            icon = folium.features.CustomIcon(icon_image=f"../Images/Cities/{reco_cities.loc[i,'City-Country']}.png" ,icon_size=(80,80))
        except:
            icon_path = crop_image(reco_cities.loc[i,'Photo'],reco_cities.loc[i,'City-Country'])
            icon = folium.features.CustomIcon(icon_image=icon_path ,icon_size=(80,80))

        folium.Marker([reco_cities.loc[i,"lat"],reco_cities.loc[i,"lng"]],
                      icon=icon,
                      tooltip = reco_cities.loc[i,'City-Country'],
                      popup = f"Travelers City Score: {reco_cities.loc[i,'Overall Score']}/5").add_to(mapa)

    return mapa