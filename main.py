# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 11:12:17 2021

@author: josec
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd


def obtener_criticas(href):
    # Devuelve el texto de la crítica y la puntuación asignada por el crítico'
    url = href
    criticas = []
    puntuaciones = []
    resultado = []
    pagina = requests.get(url)
    soup = BeautifulSoup(pagina.content, 'html.parser')
    reviews = soup.findAll('div', class_='review-text1')
    for item in reviews:
        criticas.append(item.getText())
    rating = soup.findAll('div', class_='user-reviews-movie-rating')
    for item in rating:
        puntuaciones.append(item.getText())

    for i in range(len(criticas)):
        resultado.append([criticas[i], puntuaciones[i]])
    return resultado


def obtener_descripcion_y_premios(href):
    url = href
    # url='https://www.filmaffinity.com/es/film344683.html'
    descripcion = []
    listaPremios = []
    pagina = requests.get(url)
    soup = BeautifulSoup(pagina.content, 'html.parser')
    descripcion.append(soup.find('dd', attrs={'itemprop': 'description'}).getText())
    award = soup.find('dd', class_='award')
    premios = []
    if award is not None:
        pr = award.findAll('div', class_='margin-bottom')
        for premio in pr:
            premios.append(premio.getText())
            # print(premio.getText())
    listaPremios.append(premios)

    return descripcion, listaPremios


url = 'https://www.filmaffinity.com/es/topcat.php?id=new_th_es'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
cards = soup.find_all("div", class_='movie-card movie-card-22')

titulo = []
referencia = []
duracion = []
imagen = []
descripcion = []
calificacion = []
listaPremios = []
listaCriticas = []
for card in cards:
    poster = card.find("div", class_='mc-poster')
    titulo.append(poster.a['title'])
    referencia.append(poster.a['href'])
    calificacion.append(card.find('div', class_='avg-rating').text)
    duracion.append(card.find('div', class_='duration').text)
    imagen.append(card.find('img')['src'])

    descripcion.append(obtener_descripcion_y_premios(referencia[-1])[0])
    listaPremios.append(obtener_descripcion_y_premios(referencia[-1])[1])

    # pagina=requests.get(referencia[-1])
    soup = BeautifulSoup(requests.get(referencia[-1]).content, 'html.parser')

    box = soup.find('div', attrs={'id': 'movie-reviews-box'})

    listaCriticas.append(obtener_criticas(box.a['href']))

caracteristicas = (
'titulo', 'referencia', 'duracion', 'imagen', 'descripcion', 'calificacion', 'ListaPemios', 'listaCriticas')
df = pd.DataFrame(
    list(zip(titulo, referencia, duracion, imagen, descripcion, calificacion, listaPremios, listaCriticas)),
    columns=(caracteristicas))
df.to_csv('filmaffinity.csv', index=False)

# films=pd.read_csv('D:/WebScraping/filmaffinity.csv')
