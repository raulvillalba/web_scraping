# -*- coding: utf-8 -*-
"""
@author: Jose Cano y Raul Villalba
"""

# Imports necesarios
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Devuelve el texto de la crítica y la puntuación asignada por el crítico'
def obtener_criticas(href):
    url = href
    criticas = []
    puntuaciones = []
    resultado = []
    pagina = requests.get(url)
    soup = BeautifulSoup(pagina.content, 'html.parser')
    reviews = soup.findAll('div', class_='review-text1')
    if reviews is None:
        return -1
    for item in reviews:
        criticas.append(item.getText())
    rating = soup.findAll('div', class_='user-reviews-movie-rating')
    if rating is None:
        return -1
    for item in rating:
        puntuaciones.append(item.getText())

    for i in range(len(criticas)):
        resultado.append([criticas[i], puntuaciones[i]])
    return resultado

# Devuelve los datos de la pelicula: descripcion, premios, calificacion y duracion
def obtener_datos_pelicula(href):
    url = href
    descripcion = []
    listaPremios = []
    pagina = requests.get(url)
    soup = BeautifulSoup(pagina.content, 'html.parser')
    duracion = soup.find('dd', itemprop="duration")
    if duracion is None:
        return -1, 0, 0, 0
    duracion = duracion.text

    calificacion = soup.find('div', id="movie-rat-avg")
    if calificacion is  None:
        return -1, 0, 0, 0
    calificacion = calificacion.text

    descr = soup.find('dd', attrs={'itemprop': 'description'})
    if descr is None:
        return -1, 0, 0, 0
    descr = descr.getText()

    descripcion.append(descr)
    award = soup.find('dd', class_='award')
    premios = []
    if award is not None:
        pr = award.findAll('div', class_='margin-bottom')
        for premio in pr:
            premios.append(premio.getText())
    listaPremios.append(premios)

    return descripcion, listaPremios, calificacion, duracion

# Funcion que se llama antes de salir. Guarda los datos en formato csv
def guardar_csv(titulo, referencia, duracion, imagen, descripcion, calificacion, listaPremios, listaCriticas):
    print("peliculas leidas: " + str(len(titulo)))
    caracteristicas = (
        'titulo', 'referencia', 'duracion', 'imagen', 'descripcion', 'calificacion', 'ListaPemios', 'listaCriticas')

    df = pd.DataFrame(
        list(zip(titulo, referencia, duracion, imagen, descripcion, calificacion, listaPremios, listaCriticas)),
        columns=(caracteristicas))

    df.to_csv('filmaffinity_' + str(año) + '.csv', index=False)


# Main

print("\nBienvenido a la aplicación de web scraping de Jose Cano y Raul Villaba")
print("Con esta aplicación puedes obtener los datos de un maximo de 200 peliculas del año que tu decidas")
print("Introducir año:")
año = input()

titulo = []
referencia = []
duracion = []
imagen = []
descripcion = []
calificacion = []
listaPremios = []
listaCriticas = []

for i in range(10):

    # Modificamos la url con la pagina y el año adecuados
    url = "https://www.filmaffinity.com/es/advsearch.php?page=" + str(i+1) + "stext=&stype%5B%5D=title&country=&genre=&fromyear=" + str(
        año) + "&toyear=" + str(año)

    print("Extrayendo datos de la siguiente url:" + str(url))
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    cards = soup.find_all("div", class_='movie-card movie-card-1')

    # Para cada pelicula:
    for card in cards:
        poster = card.find("div", class_='mc-poster')
        if poster is None:
            print("too many requests")
            guardar_csv(titulo, referencia, duracion, imagen, descripcion, calificacion, listaPremios, listaCriticas)
            exit()
        # Añadimos el titulo
        titulo.append(poster.a['title'])
        # Añadimos la referencia
        referencia.append(poster.a['href'])

        descr,prem, cal, dur = obtener_datos_pelicula(poster.a['href'])
        if descr == -1:
            print("too many requests")
            guardar_csv(titulo, referencia, duracion, imagen, descripcion, calificacion, listaPremios, listaCriticas)
            exit()
        # Añadimos descripcion, lista de premios, calificacion y duracion
        descripcion.append(descr)
        listaPremios.append(prem)
        calificacion.append(cal)
        duracion.append(dur)

        img = card.find('img')
        if img is None:
            print("too many requests")
            guardar_csv(titulo, referencia, duracion, imagen, descripcion, calificacion, listaPremios, listaCriticas)
            exit()
        # Añadimos la imagen del cartel
        imagen.append(img['src'])

        soup = BeautifulSoup(requests.get(referencia[-1]).content, 'html.parser')
        box = soup.find('div', attrs={'id': 'movie-reviews-box'})
        if box is None:
            print("too many requests")
            guardar_csv(titulo, referencia, duracion, imagen, descripcion, calificacion, listaPremios, listaCriticas)
            exit()

        criticas = obtener_criticas(box.a['href'])
        if criticas == -1:
            print("too many requests")
            guardar_csv(titulo, referencia, duracion, imagen, descripcion, calificacion, listaPremios, listaCriticas)
            exit()
        # Añadimos las criticas
        listaCriticas.append(criticas)

guardar_csv(titulo, referencia, duracion, imagen, descripcion, calificacion, listaPremios, listaCriticas)

