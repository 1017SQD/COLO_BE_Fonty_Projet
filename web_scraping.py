#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Fonty COLO BE
"""

import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup, Tag, NavigableString
import pickle
from multiprocessing import Pool, cpu_count

# Définition des fonctions
def validTag(tag):

    if "class" in tag.attrs:
        for c in tag.attrs["class"]:
            if c in ["article-summary-new"] :
                return False
            
    return True

def getSelectedText(tag):
    
    texte = ""
    
    if validTag(tag):
        for child in tag.children:
            if type(child) == NavigableString:
                texte += " " + (child.string).strip()
            
            if type(child) == Tag:
                texte += getSelectedText(child)
                
    return texte

def parseURL(url):
    user_agent = "Mozilla/5.0 (Macintosh; IntelMac OS X 10_9_3) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/35.0.1916.47 Safari/537.36"
    req = Request(url, headers={"User-Agent":user_agent})

    try: # gestion des exceptions avec un bloc try/except
        response = urlopen(req)

    except (HTTPError, URLError) as e:
        sys.exit(e) # sortie du programme avec affichage de l’erreur
               
    bsObj = BeautifulSoup(response, "lxml")
    
    titre = bsObj.find("article", class_="article").find("h1").text
    
    div_article = bsObj.find("div", class_="article-content")
    texte = getSelectedText(div_article)
                
    return(url, titre, texte)

# Programme principal
if __name__ == '__main__':
    
    url_pagination= "https://www.thecanadianencyclopedia.ca/en/browse/things/politics-law/protests-and-strikes"
    user_agent = "Mozilla/5.0 (Macintosh; IntelMac OS X 10_9_3) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/35.0.1916.47 Safari/537.36"
    req = Request(url_pagination, headers={"User-Agent":user_agent})
    
    try: # gestion des exceptions avec un bloc try/except
        response = urlopen(req)
            
    except (HTTPError, URLError) as e:
        sys.exit(e) # sortie du programme avec affichage de l’erreur

    page_url = "https://www.thecanadianencyclopedia.ca/en/browse/things/politics-law/protests-and-strikes?page={}"
    bsObj = BeautifulSoup(response, "lxml")
    # nb de pages de pagination 
    nb_page = bsObj.find('ul', class_='pagination').find_all('li')[-2].a["href"].split('=')[1]
    # liste de l'ensemble des pages de pagination 
    liste_url = [page_url.format(i) for i in range(1, int(nb_page) +1)]

    liste_req  = []    
    for url in liste_url :
        user_agent = "Mozilla/5.0 (Macintosh; IntelMac OS X 10_9_3) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        liste_req.append(Request(url, headers={"User-Agent":user_agent}))
            
    url_article = []
    for req in liste_req:
        try: # gestion des exceptions avec un bloc try/except
            response = urlopen(req)
            
        except (HTTPError, URLError) as e:
            sys.exit(e) # sortie du programme avec affichage de l’erreur
            
        bsObj = BeautifulSoup(response, "lxml")
        div1 = bsObj.find_all("article", class_="calloutList-item")

        for article in div1:
            url_article.append(article.a["href"])
                    
    liste_tuple = []
    with Pool(cpu_count()-1) as p :
        liste_tuple = p.map(parseURL, url_article)
    
    with open("protests_and_strikes.pick", "wb") as pickFile:
        pickle.dump(liste_tuple, pickFile)
     
    print(liste_tuple)