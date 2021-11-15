# -*- coding: utf-8 -*-

import math
import urllib
import json
import datetime
from haversine import haversine
import operator
from py2neo import Graph, Node, Relationship


##########################################################################
### CONNECT TO DATABASE
##########################################################################

#Sur la vm ubuntu@pact-5.r2.enst.fr, on se connecte à la BDD (Neo4j)
secure_graph = Graph("bolt://localhost:7687", auth = ("neo4j", "aterredechine"))
secure_graph.begin()



    
##########################################################################
### CLASS USER
##########################################################################

#Seule variable globale du programme, donne le nombre de recommandations par utilisateur
recommandationNumber = 2
      
class User: # Définition de notre classe User


#Fait appel à la bdd pour chercher les info de l'utilisateur d'ID u_id.
    def getUser(u_id):
        list = {}
        for e in secure_graph.nodes.match("Person"):
            if (e["u_id"] == u_id):
                list["u_id"] = u_id
                list["username"] = e["username"]
                list["mail"] = e["mail"]
                list["profile_creation_date"] = e["profile_creation_date"]
                list["address"] = e["address"]
        return list

#Renvoie les dix derniers évènements auxquels l'utilisateur userID a participé.
    def getLatestsEvents(userID):
        list_year = []
        list_month = []
        list_day = []
        list_hour = []
        list_min = []
        list_date = []
        statement = "MATCH (s:Sector)<-[r:ABOUT]-(e:Event)<-[a:PARTICIPATED]-(p:Person) WHERE p.u_id =~ {u_id} RETURN e.date, s.type LIMIT 10"
        data = secure_graph.run(statement, {"u_id": userID}).data()
        for i in range (len(data)):
            date_i = data[i]["e.date"]
            list_date.append(date_i)
            day_i = int(date_i[0] + date_i[1])
            if date_i[0] == "0":
                day_i = int(date_i[1])
            month_i = int(date_i[3] + date_i[4])
            if date_i[3] == "0":
                month_i = int(date_i[4])
            year_i = int(date_i[6] + date_i[7] + date_i[8] + date_i[9])
            hour_i = int(date_i[11] + date_i[12])
            if date_i[11] == "0":
                hour_i = int(date_i[12])
            min_i = int(date_i[14] + date_i[15])
            if date_i[14] == "0":
                min_i = int(date_i[15])
            list_year.append(year_i)
            list_month.append(month_i)
            list_day.append(day_i)
            list_hour.append(hour_i)
            list_min.append(min_i)
        list_year_sorted = sorted(list_year)
        for i in range (len(list_year_sorted)): #on fait le tri selon l'année
            for j in range (i, len(list_date)):
                if str(list_year_sorted[i]) in data[j]["e.date"]:
                    data[j], data[i] = data[i], data[j]
                    list_date[j], list_date[i] = list_date[i], list_date[j]

        j = 0
        list_indices = []
        while (j < len(list_year_sorted)): #on partitionne la liste triée des années par valeurs identiques
            m = list_year_sorted[0]
            if (list_year_sorted[j] != m and j not in list_indices):
                list_indices.append(j)
            j+= 1

        list_month_sorted_by_year = []
        for i in range (len(list_year_sorted)):
            list_month_sorted_by_year.append(Month(list_year_sorted[i], list_date[i]))

        month_data = []
        day_data = []
        hour_data = []
        minute_data = []
        for i in range (len(data)):
            month_data.append(int(data[i]["e.date"][3] + data[i]["e.date"][4]))
            if (data[i]["e.date"][3] == "0"):
                month_data[i] = int(data[i]["e.date"][4])
            day_data.append(int(data[i]["e.date"][0] + data[i]["e.date"][1]))
            if (data[i]["e.date"][0] == "0"):
                day_data[i] = int(data[i]["e.date"][1])
            hour_data.append(int(data[i]["e.date"][11] + data[i]["e.date"][12]))
            if (data[i]["e.date"][11] == "0"):
                hour_data[i] = int(data[i]["e.date"][12])
            minute_data.append(int(data[i]["e.date"][14] + data[i]["e.date"][15]))
            if (data[i]["e.date"][14] == "0"):
                minute_data[i] = int(data[i]["e.date"][15])



        month_data = sorted(month_data)
        if (list_indices != []):
            for k in range (len(list_indices)-1): #on fait le tri selon les mois
                for i in range (list_indices[k], list_indices[k+1] + 1):
                    for l in range (i, list_indices[k+1] + 1):
                        if str(list_month_sorted_by_year[i]) in str(month_data[l]):
                            data[i], data[l] = data[l], data[i]
                            list_date[i], list_date[l] = list_date[l], list_date[i]
                            day_data[l], day_data[i] = day_data[i], day_data[l]
                            hour_data[l], hour_data[i] = hour_data[i], hour_data[l]
                            minute_data[l], minute_data[i] = minute_data[i], minute_data[l]


            if (list_indices[0] == 0):
                for i in range (0, list_indices[0]+1):
                    for l in range (i, list_indices[0] + 1):
                        if str(list_month_sorted_by_year[i]) in str(month_data[l]):
                            data[i], data[l] = data[l], data[i]
                            list_date[i], list_date[l] = list_date[l], list_date[i]
                            day_data[l], day_data[i] = day_data[i], day_data[l]
                            hour_data[l], hour_data[i] = hour_data[i], hour_data[l]
                            minute_data[l], minute_data[i] = minute_data[i], minute_data[l]


        else:
            for i in range (len(list_year_sorted)):
                for l in range (i, len(list_year_sorted)):
                    if str(list_month_sorted_by_year[i]) in str(month_data[l]):
                        data[i], data[l] = data[l], data[i]
                        list_date[i], list_date[l] = list_date[l], list_date[i]
                        day_data[l], day_data[i] = day_data[i], day_data[l]
                        hour_data[l], hour_data[i] = hour_data[i], hour_data[l]
                        minute_data[l], minute_data[i] = minute_data[i], minute_data[l]



        j = 0
        while (j < len(list_month_sorted_by_year)): #on partitionne la liste triée des mois par valeurs identiques
            m = list_month_sorted_by_year[0]
            if (list_month_sorted_by_year[j] != m and j not in list_indices):
                list_indices.append(j)
            j+= 1

        list_indices = sorted(list_indices)


        list_day_sorted_by_year_and_month = []
        for i in range (len(list_date)):
            list_day_sorted_by_year_and_month.append(Day(list_month_sorted_by_year[i], list_date[i]))


        day_data = sorted(day_data)
        if (list_indices != []):
            for k in range (len(list_indices)-1): #on fait le tri selon les jours
                for i in range (list_indices[k], list_indices[k+1] + 1):
                    for l in range (i, list_indices[k+1] + 1):
                        if str(list_day_sorted_by_year_and_month[i]) in str(day_data[l]):
                            data[i], data[l] = data[l], data[i]
                            list_date[i], list_date[l] = list_date[l], list_date[i]
                            hour_data[l], hour_data[i] = hour_data[i], hour_data[l]
                            minute_data[l], minute_data[i] = minute_data[i], minute_data[l]

            if (list_indices[0] == 0):
                for i in range (0, list_indices[0]+1):
                    for l in range (i, list_indices[0] + 1):
                        if str(list_day_sorted_by_year_and_month[i]) in str(day_data[l]):
                            data[i], data[l] = data[l], data[i]
                            list_date[i], list_date[l] = list_date[l], list_date[i]
                            hour_data[l], hour_data[i] = hour_data[i], hour_data[l]
                            minute_data[l], minute_data[i] = minute_data[i], minute_data[l]


        else:
            for i in range (len(list_year_sorted)):
                for l in range (i, len(list_year_sorted)):
                    if str(list_day_sorted_by_year_and_month[i]) in str(day_data[l]):
                        data[i], data[l] = data[l], data[i]
                        list_date[i], list_date[l] = list_date[l], list_date[i]
                        hour_data[l], hour_data[i] = hour_data[i], hour_data[l]
                        minute_data[l], minute_data[i] = minute_data[i], minute_data[l]
        j = 0
        while (j < len(list_day_sorted_by_year_and_month)): #on partitionne la liste triée des jours par valeurs identiques
            m = list_day_sorted_by_year_and_month[0]
            if (list_day_sorted_by_year_and_month[j] != m and j not in list_indices):
                list_indices.append(j)
            j+= 1

        list_indices = sorted(list_indices)
        list_hours_sorted_by_year_and_month_and_day = []
        for i in range (len(list_date)):
            list_hours_sorted_by_year_and_month_and_day.append(Hour(list_day_sorted_by_year_and_month[i], list_date[i]))

        hour_data = sorted(hour_data)
        if (list_indices != []):
            for k in range (len(list_indices)-1): #on fait le tri selon les heures
                for i in range (list_indices[k], list_indices[k+1] + 1):
                    for l in range (i, list_indices[k+1] + 1):
                        if str(list_hours_sorted_by_year_and_month_and_day[i]) in str(hour_data[l]):
                            data[i], data[l] = data[l], data[i]
                            list_date[i], list_date[l] = list_date[l], list_date[i]
                            minute_data[l], minute_data[i] = minute_data[i], minute_data[l]
            if (list_indices[0] == 0):
                for i in range (0, list_indices[0]+1):
                    for l in range (i, list_indices[0] + 1):
                        if str(list_hours_sorted_by_year_and_month_and_day[i]) in str(hour_data[l]):
                            data[i], data[l] = data[l], data[i]
                            list_date[i], list_date[l] = list_date[l], list_date[i]
                            minute_data[l], minute_data[i] = minute_data[i], minute_data[l]


        else:
            for i in range (len(list_year_sorted)):
                for l in range (i, len(list_year_sorted)):
                    if str(list_hours_sorted_by_year_and_month_and_day[i]) in str(hour_data[l]):
                        data[i], data[l] = data[l], data[i]
                        list_date[i], list_date[l] = list_date[l], list_date[i]
                        minute_data[l], minute_data[i] = minute_data[i], minute_data[l]
        j = 0
        while (j < len(list_hours_sorted_by_year_and_month_and_day)): #on partitionne la liste triée des heures par valeurs identiques
            m = list_hours_sorted_by_year_and_month_and_day[0]
            if (list_day_sorted_by_year_and_month[j] != m and j not in list_indices):
                list_indices.append(j)
            j+= 1

        list_indices = sorted(list_indices)


        list_minutes_sorted_by_year_and_month_and_day_and_hour = []
        for i in range (len(list_date)):
            list_minutes_sorted_by_year_and_month_and_day_and_hour.append(Minute(list_hours_sorted_by_year_and_month_and_day[i], list_date[i]))

        minute_data = sorted(minute_data)
        if (list_indices != []):
            for k in range (len(list_indices)-1): #on fait le tri selon les minutes
                for i in range (list_indices[k], list_indices[k+1] + 1):
                    for l in range (i, list_indices[k+1] + 1):
                        if str(list_minutes_sorted_by_year_and_month_and_day_and_hour[i]) in str(minute_data[l]):
                            data[i], data[l] = data[l], data[i]
                            list_date[i], list_date[l] = list_date[l], list_date[i]

            if (list_indices[0] == 0):
                for i in range (0, list_indices[0]+1):
                    for l in range (i, list_indices[0] + 1):
                        if str(list_minutes_sorted_by_year_and_month_and_day_and_hour[i]) in str(minute_data[l]):
                            data[i], data[l] = data[l], data[i]
                            list_date[i], list_date[l] = list_date[l], list_date[i]


        else:
            for i in range (len(list_year_sorted)):
                for l in range (i, len(list_year_sorted)):
                    if str(list_minutes_sorted_by_year_and_month_and_day_and_hour[i]) in str(minute_data[l]):
                        data[i], data[l] = data[l], data[i]
                        list_date[i], list_date[l] = list_date[l], list_date[i]
        lastthemes = []
        for i in range (len(data)):
            lastthemes.append(data[i]["s.type"])

        for i in range (math.floor(len(data)//2)):
            lastthemes[i], lastthemes[len(data)-1-i] = lastthemes[len(data)-1-i], lastthemes[i]

        return lastthemes




#Constructeur de la classe User
    def __init__(self, userID):
        
#La fonction getUser(userID) fait appel à la BDD, elle renvoie un objet de type dict contenant les attributs ID, address.        
        user = User.getUser(userID)
        
#On définit les attributs de la classe User, on récupère les données de la BDD et on les convertis avec les formats utilisés par notre programme.
        self.username = user["username"]
        self.userID = userID
        self.address = Address(user["address"])

#La fonction getLatestsEvents(userID) fait appel à la BDD, elle renvoie une liste de dix stringTheme de la forme : "[0110]".
#Ces thèmes sont ceux des dix derniers événements auxquels l'utilisateur a participé.
        latestsEvents = []
        stringLatestsEvents = User.getLatestsEvents(userID)

#On convertit cette liste en liste d'éléments de la classe Theme, l'attribut latestsEvents contient donc une liste de Theme
        for i in range(len(stringLatestsEvents)):
            latestsEvents.append(Theme(stringLatestsEvents[i]))    
        self.latestsEvents = latestsEvents

#On initialise les recommandations faites à un l'utilisateur avec une liste vide, c'est à nous de remplir cet attribut.
        self.recommandations = [] 
    
    

    def updateRecommandations(self): #La fonction updateRecommandations met à jour l'attribut "recommandations". 

#getAllEvents fait appel à la BDD, elle renvoie un objet de type dict listant tous les événements de la BDD.        
        events = Recommandations.getAllEvents()

        newRecommandations = []
        eventList = []

#On parcours la liste des événements de la bdd, on construit une liste d'éléments de la classe Event.
        for i in range (len(events)):
            event = Event(events[i]["e.id"])
#On ne garde dans cette liste que les évènements futurs.
            if event.date.bitTemporalDistanceToCurrentTime(event.theme.temporalPrecision) >=0 :
                eventList.append(event)

#Cette fonction va nous servir à trier la liste des événements selon la distance totale en bits à l'utilisateur.
        def bitTotalDistance(event):
            return int(event.bitTotalDistanceToUser(self))

#On trie la liste en utilisant comme clé la fonction précédente, les évènements sont triés selon leur distance à l'utilisateur.
        eventList.sort(key=bitTotalDistance)
        

#On ajoute n=recommandationNumber éléments de la liste trié des événements dans l'attribut self.recommandations
        for i in range(recommandationNumber):
            newRecommandations.append(str(eventList[i].eventID))
        
        self.recommandations = newRecommandations
##        print("Nouvelles recommandations : "+str(newRecommandations)+"\n")





##########################################################################
### CLASS EVENT
##########################################################################
        
class Event: # Définition de notre classe Event

    def __init__(self, eventID): # Notre méthode constructeur

# getEvent(eventID) fait appel à la BDD, elle renvoie un objet de type dict contenant les attributs address, date et theme
        event = Event.getEvent(eventID)

# Les classes Address, Theme et Date nous permette de convertir le contenu de la bdd au bon format dans les attributs de la classe Event
        self.eventID = eventID
        self.address = Address(event["address"])
        self.date = Date(event["date"])
        self.theme = Theme(event["theme"])



# Calcule la distance thématique en bits séparant d'un utilisateur
    def bitThemeDistanceToUser(self, user):
        bitDistance = 0
#On calcule la somme des distance thématique en bit avec les 10 derniers événements de l'utilisateur.
        for i in range(len(user.latestsEvents)):
            bitDistance += self.theme.bitThemeDistance(user.latestsEvents[i])
        
#Si l'utilisateur n'a jamais participé à un évenement, la distance thématique est nulle.       
        if len(user.latestsEvents) <= 0:
            return 0

#La distance thématique en bit est la partie entière de la moyenne des distances avec les dix derniers événements auxquels l'utilisateur a participé.
        bitDistance = math.ceil(bitDistance/len(user.latestsEvents))
        
        return bitDistance

    

# Calcule la distance totale en bits avec un utilisateur.
    def bitTotalDistanceToUser(self, user):

        totalBitDistance = 0
        
#On ajoute la distance thématique
        totalBitDistance += self.bitThemeDistanceToUser(user)
##        print("Distance thematique : " + str(self.bitThemeDistanceToUser(user)))

#On ajoute la distance temporelle
        totalBitDistance += self.date.bitTemporalDistanceToCurrentTime(self.theme.temporalPrecision)
##        print("Distance temporelle : " + str(self.date.bitTemporalDistanceToCurrentTime(self.theme.temporalPrecision)))

#On ajoute la distance spatiale
        totalBitDistance += self.address.bitSpatialDistance(user.address, self.theme.spatialPrecision)
##        print("Distance spatiale : " + str(self.address.bitSpatialDistance(user.address, self.theme.spatialPrecision)))

##        print("event ID :"+self.eventID)
##        print("Distance totale : " + str(totalBitDistance)+"\n") 
        return totalBitDistance



#Donne le contenu de la bdd pour l'événement d'id eventID.
    def getEvent(eventId):
        statement = "MATCH (e:Event)-[r:ABOUT]->(s:Sector) WHERE e.id =~ {id} RETURN s.type, e.date, e.location"
        data = secure_graph.run(statement, {"id": eventId}).data()[0]

        date_data = data["e.date"]
        e_day = int(date_data[0] + date_data[1])
        if date_data[0] == "0":
            e_day = int(date_data[1])
        e_month = int(date_data[3] + date_data[4])
        if date_data[3] == "0":
            e_month = int(date_data[4])
        e_year = int(date_data[6] + date_data[7] + date_data[8] + date_data[9])
        e_hour = int(date_data[11] + date_data[12])
        if date_data[11] == "0":
            e_hour = int(date_data[12])
        e_min = int(date_data[14] + date_data[15])
        if date_data[14] == "0":
            e_min = int(date_data[15])

        dictionnaire = {}
        dictionnaire["theme"] = data["s.type"]
        dictionnaire["date"] = datetime.datetime(e_year, e_month, e_day, e_hour, e_min)
        dictionnaire["address"] = data["e.location"]

        return dictionnaire





##########################################################################   
### CLASS DATE
##########################################################################

class Date:
   
    def __init__(self, date): # Notre méthode constructeur

# La date est stockée au format "06-05-20 12:33" dans la bdd, le constructeur fragmente cette chaîne de caractères pour récupérer les informations utiles.
        List = str(date).split()

        time = List[1]
        date = List[0]
        
        date = date.split("-")
        time = time.split(":")

        year=int(date[0])

#On s'assure que le mois 09 soit convertit en 9 par exemple.
        month=date[1]
        if(month[0]=="0"):    
            month=month[1]
        month = int(month)

#Même chose que pour le mois
        day = date[2]
        if(day[0]=="0"):
            day=day[1]
        day = int(day)    

#Même chose
        hour = time[0]
        if(hour[0]=="0"):
            hour=hour[1]
        hour = int(hour)

#Même chose
        minute = time[1]
        if(minute[0]=="0"):
            minute = minute[1]
        minute = int(minute)

#Ensuite, on stocke la date au format datetime, qui nous permetra de faire des calculs aisement.
        self.date = datetime.datetime(year, month, day, hour, minute)



#Calcule la distance temporelle en bit qui sépare la date du temps présent.
    def bitTemporalDistanceToCurrentTime(self, precision):

#Datetime nous donne accès à la date présente.
        currentDate = datetime.datetime.now()
        eventDate = self.date

#Datetime nous permet ce genre d'opération sur les dates, le résultat est au format timedelta (des jours et des secondes)
        temporalDistance = eventDate - currentDate
        
        if temporalDistance <= datetime.timedelta(minutes=0):
            return -1 

#On reconvertit le timedelta en minutes, la plus petite unité de temps sur notre application.
        temporalDistanceMinutes = math.ceil(temporalDistance.days*24*60 + temporalDistance.seconds/60)
        
#On calcule la distance en bits en fonction de la précision.
        bitTemporalDistance = math.ceil(math.log(temporalDistanceMinutes/precision, 2))
    
        return bitTemporalDistance        
        
        




##########################################################################
### CLASS ADDRESS
##########################################################################

class Address:
    
    def __init__(self, stringAddress):

#Dans la bdd les adresses sont stockées sous la forme "43, avenue de Paris, Vincennes, 94300", le constructeur récupère les différentes partie de l'adresse.        
        address = stringAddress.split(", ")
        
        self.streetNumber = address[0]
        self.streetName = address[1]
        self.cityName = address[2]
        self.zipCode = address[3]
        


#Calcule la distance en bit avec une autre adresse en fonction de la précision demandée.
    def bitSpatialDistance(self, address, precision):

#Appel à la fonction getCoordinates pour obtenir deux jeux de coordonnées à partir des deux adresses utilisées.
        coordinates1 = self.getCoordinates(self)
        coordinates2 = self.getCoordinates(address)
        
        distance = haversine(coordinates1, coordinates2) #on utilise la formule de haversine (module haversine) pour obtenir la distance en km entre deux jeux de coordonnées.

#Pour ne pas faire beuger la formule suivante + si la distance est plus faible que la précision exigée, la distance spatiale en bits est bien nulle.
        if(distance < precision):
            return 0

#On applique la formule de la distance en bits.
        return math.ceil(math.log((distance/precision)**2,2)) #ceil : partie entière supérieure
        #Attention, l'unité utilisée est le kilomètre, la précision doit donc être indiquée en kilomètres



#Renvoie un jeu de coordonnées grace à l'API Google Maps.
    def getCoordinates(address):
#On met l'adresse au bon format pour l'API  Google
        address = str(address.streetNumber) + '+' + str(address.streetName).replace(' ','+') + '+' + str(address.cityName).replace(' ','+') + '+' + str(address.zipCode)

#Clé APi à ne pas utiliser abondamment sans mon autorisation ;)
        api_key='AIzaSyB3LCRwYBu5MAwIlMrWw2jNfKOhdc9yXn8'
        
#On met l'adress et la clé API dans l'url et on envoie la requête.
        url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (address, api_key)
        data = urllib.request.urlopen(url).read()
        statut = json.loads(data)['status']

#On extrait la latitude et la longitude du json renvoyé par Google Maps
        if statut=='OK':
            lat = json.loads(data)['results'][0]['geometry']['location']['lat']
            lng = json.loads(data)['results'][0]['geometry']['location']['lng']
        
        return [lat, lng]
#Méthode statique pour pouvoir la laisser dans la classe sans qu'elle utilise aucun objet de la classe.
    getCoordinates = staticmethod(getCoordinates)
        





##########################################################################
### CLASS THEME
##########################################################################

class Theme:
    
    def __init__(self, stringTheme):


#Les thèmes sont stockés dans la bdd sous la forme "[0110]", le constructeur convertit cette string en une liste [0,1,1,0].
        listTheme = []
        for i in range(len(stringTheme)):
            if stringTheme[i] == '0':
                listTheme += [0]
            elif stringTheme[i] == '1':
                listTheme += [1]
        
        self.list = listTheme

#Les précision temporelles et spatiales sont lié au thème, elles sont fixées par un appel à la bdd, on règle ces précisions sans toucher au programme.
        self.temporalPrecision = float(Theme.getTemporalPrecision(stringTheme))
        self.spatialPrecision = float(Theme.getSpatialPrecision(stringTheme))

    

#Renvoie la distance thematique en bits avec un autre thème (nombre de bits nécessaire pour passer d'un thème à l'autre dans le graphe).      
    def bitThemeDistance(self, theme): 
        
#On s'assure que les deux thèmes sont bien définis
        if len(self.list) == 0 or len(theme.list)==0 :
##            print("Error, events not defined correctly")
            return -1


#On cherche le sous arbre le plus petit qui contient les deux thèmes, par exemple pour [0110] et [0101] le sous arbre est [01].
        i=0
        while(i<len(self.list) and i<len(theme.list) and self.list[i] == theme.list[i]):
            i+=1

#On calcule la longueur du chemin séparant les deux thèmes (profondeur du thème1 + profondeur du thème2 - 2*profondeur de la racine du sous arbre contenant les deux)
        l1 = len(self.list)
        l2 = len(theme.list)
        numberBit=l1+l2-2*i
    
        return numberBit


#Renvoie la précision temporelle associée au thème (en minutes).    
    def getTemporalPrecision(theme):
        statement = "MATCH (s:Sector) WHERE s.type = {type} RETURN s.temporal_precision"
        data = secure_graph.run(statement, {"type": theme}).data()[0]["s.temporal_precision"]
        return data

#Renvoie la précision spatiale associée au thème (en kilomètres).
    def getSpatialPrecision(theme):
        statement = "MATCH (s:Sector) WHERE s.type = {type} RETURN s.spatial_precision"
        data = secure_graph.run(statement, {"type": theme}).data()[0]["s.spatial_precision"]
        return data




##########################################################################
### CLASS FREQUENCY
##########################################################################


#ébouche sur la fréquence, cf rapport pour les explications, dans la pratique, cette classe n'est pas utilisée.
class Frequency:

    def __init__(self, stringTheme):
        self.list = listTheme
    

     
    def bitFrequencyDistance(self, theme, n):
        fe #fréquence de mise en ligne de l'événement
        fp #fréquence de participation de l'utilisateur
        c = fp/fe
        sigma #variance de la fréquence de participation au type d'événement
        if(c==0 or n==0): #s'il n'y a pas de participation antérieure 
            return 0
        else:
            if (sigma > 1/(2*fp)) : 
#si l'écart type est trop grand la participation n'est pas considérée comme régulière une fréquence de participation n'a pas de sens.
                return 0
            else:
                return math.ceil(-math.log(1-(1-c)**(n*fe, 2))) #cf rapport 






##########################################################################
### RECOMMANDATIONS
##########################################################################

#La classe Recommandations implémente la fonction upadte qui met à jour la bdd avec le calcul des nouvelles recommandations.
class Recommandations:

#Ajoute une recommandation à un utilisateur dans la bdd: l'événement d'id e_id est recommandé à l'utilisateur d'id u_id
    def create_reco(e_id, u_id):
        statement = "MATCH (p:Person) WHERE p.u_id = {u_id} MATCH (e:Event) WHERE e.id = {e_id} CREATE (p)<-[r:SUGGESTED]-(e)"
        secure_graph.run(statement, {'u_id' : u_id, "e_id" : e_id})

#Efface une recommandation de la bdd: la recommandation de l'événement d'id e_id recommandé à l'utilisateur d'id u_id est effacée
    def erase_reco(e_id, u_id):
        statement = "MATCH (p:Person)<-[r:SUGGESTED]-(e:Event) WHERE p.u_id = {u_id} AND e.id = {e_id} DETACH DELETE r"
        secure_graph.run(statement, {'u_id' : u_id, "e_id" : e_id})

#Donne l'id des évènements recommanndés à l'utilisateur d'id u_id
    def get_reco(u_id):
        statement = "MATCH (p:Person)<-[r:SUGGESTED]-(e:Event) WHERE p.u_id = {u_id} RETURN e.id"
        result = secure_graph.run(statement, {'u_id' : u_id}).data()
        list = []
        for i in range(len(result)):
            list.append(result[i]['e.id'])
        return list
 
#Renvoie la totalité des événements de la bdd
    def getAllEvents():
        statement = "MATCH (e:Event)-[r:ABOUT]->(s:Sector) RETURN e.name, e.id, e.nb_max, e.nb_courant, e.location, e.date, s.type"
        events = secure_graph.run(statement).data()

        return events

#Renvoie la totalité des utilisateurs de la bdd.
    def getAllUsers():
        statement = "MATCH (p:Person) RETURN p.username, p.u_id, p.address"
        users = secure_graph.run(statement).data()

        return users


#Met à jour la bdd avec le calcul des nouvelles recommandations.
    def update():
    
        users = Recommandations.getAllUsers()

#On parcours la liste de tous les utilisateurs de la bdd, on construit à chaque fois un objet de la classe User.
        for i in range(len(users)):
            user_id = users[i]['p.u_id']
            user = User(user_id)

    #On efface toutes les recommandations existantes de l'utilisateur.
            recommandations = Recommandations.get_reco(user_id)
            for j in range(len(recommandations)):
                Recommandations.erase_reco(str(recommandations[j]), str(user_id))
            ##print("Utilisateur : "+user.username+"\n")
    
    #On met à jour l'attribut user.recommandations avec la fonction updateRecommandations de la classe User.
            user.updateRecommandations()
            
    #On parcours la liste des nouvelles recommandations et on les ajoutes à la bdd.
            for j in range(len(user.recommandations)):
                Recommandations.create_reco(str(user.recommandations[j]), str(user_id))





##########################################################################
### PROGRAM
##########################################################################

#On lance la fonction update qui met à jour la bdd, l'intégration du module avec la crontab de Linux déclenche automatiquement le programme toutes les 24h.
Recommandations.update()







##########################################################################
### FONCTION ANNEXES
##########################################################################

#Fonctions utilisées par les fonctions qui communiquent avec la base de données.

def Date(a, L):
    for i in range (len(L)):
        if str(a) in L[i]:
            return L[i]

def Month(a, L):
    month = None
    if (str(a) in L):
        month = int(L[3] + L[4])
        if int(L[3]) == 0:
            month = int(L[4])
    return month

def Day(a,L):
    day = None
    if (str(a) in L):
        day = int(L[0] + L[1])
        if int(L[0]) == 0:
            day = int(L[1])
    return day

def Hour(a,L):
    hour = None
    if (str(a) in L):
        hour = int(L[11] + L[12])
        if int(L[11]) == 0:
            hour = int(L[12])
    return hour



def Minute(a,L):
    minute = None
    if (str(a) in L):
        minute = int(L[14] + L[15])
        if int(L[14]) == 0:
            minute = int(L[15])
    return minute

