#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Fonty COLO BE
"""

from pandas import DataFrame, Series, concat
import pickle
import re
from math import log
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

# Définition des fonctions
def getTokens(doc):
    regex = r"""\w+"""
    tokens = [word.strip().lower() for word in re.findall(regex, doc)]
    return tokens

# Définition des classes
class DTM:
    def __init__(self, liste_tuple, mots_vides):
        #Récupération des titres et des URLS
        les_url = []
        les_titres = []

        for tuple in liste_tuple :
            les_url.append(tuple[0])
            les_titres.append(tuple[1])

        self.url = les_url
        self.title = les_titres
        self.stopWords = mots_vides
        #Construction du dataframe de mots

        termes_docs = []  #Liste de dictionnaires, qui compte de le nombre d'occurrences de chaque terme dans chaque doc
        for tuple in liste_tuple :
            texte = tuple[2]
            les_mots = getTokens(texte)
            dico = {} #Dictionnaire qui va compter le nombre d'occurrences de chaque mot
            for mot in les_mots :
                if mot not in self.stopWords : #gestion des mots vides
                    dico[mot] = dico.get(mot,0)+1
            termes_docs.append(dico)
        self.data = DataFrame(termes_docs).fillna(0)

        #Calcul du df : il faut connaitre le nombre de documents qui contiennent chauqe terme
        df = self.data.astype('bool').sum()
        nbdoc = self.data.shape[0]
        log_idf = [log(nbdoc/value) for value in df]
        self.data = self.data.div(self.data.max(axis=1),axis=0)
        self.data = self.data.mul(log_idf,axis=1)
        #sur un dataframe, div et mul multiplient ou divisent sur toute la ligne (axis=0) ou sur la colonne(axis=1)

    def __repr__(self):
        return self.data.__repr__()

    def queryScore(self, chaine, N):
        chaine = chaine.lower()
        mots_valides = [mot for mot in chaine.split() if mot not in self.stopWords]
        scores = self.data[mots_valides].sum(axis=1)
        resultat =  concat({'score':scores,'url':Series(self.url)},axis=1).sort_values(by='score',ascending=False)[0:N]
        return resultat["url"]
    
    def wordCloud(self, numDoc):
        nuage = WordCloud(background_color="white", max_words=50).generate_from_frequencies(self.data.loc[numDoc])
        plt.imshow(nuage, interpolation='bilinear')
        plt.axis("off")
        plt.show()
        
    def nMostSimilar(self, numDoc, N):
        csim = cosine_similarity(self.data, self.data)
        docs_sim = DataFrame(csim).sort_values(by=numDoc, ascending=False).loc[:,numDoc][0:N]
        titre_docs_sim = [self.title[ind] for ind in docs_sim.index]
        return ", ".join(titre_docs_sim)
        

# Programme principal
with open("protests_and_strikes.pick", 'rb') as pickFile :
    doc = pickle.load(pickFile)
    
with open("english_stopwords.txt",'r') as textFile :
    mots_vides = [ligne.strip() for ligne in textFile]
            
#print(mots_vides)

maDTM = DTM(doc,mots_vides)
#print(maDTM)

# Exemples queryScore
print(maDTM.queryScore("Protests and Strikes", 5))
print("*"*50)
print(maDTM.queryScore("discrimination against minorities", 10))
print("*"*50)
print(maDTM.queryScore("Political law", 7))
print("*"*50)

# Exemples wordCloud
maDTM.wordCloud(0)
maDTM.wordCloud(1)
maDTM.wordCloud(3)

# Exemples nMostSimilar
print(maDTM.nMostSimilar(0, 5))
print("*"*50)
print(maDTM.nMostSimilar(10, 7))
print("*"*50)
print(maDTM.nMostSimilar(1, 10))
print("*"*50)