import speech_recognition as sr
import pyttsx3
import pygame
import random
from threading import Timer
import requests
import datetime
import time
import sys
import re
import os
from dotenv import load_dotenv
from translate import Translator

script_folder = os.path.dirname(os.path.abspath(__file__))

# Supprimer les anciens fichiers spécifiques s'ils existent
files_to_delete = ["api.env", "quiz.py", "recette.py", "responses.py", "responses_heure.py", "responses_inapproprié.py"]

# Liste des fichiers à télécharger avec leurs URLs sur GitHub
files_to_download = {
    "api.env": "https://github.com/Nolek0/Chatbox-project/raw/main/api.env",
    "quiz.py": "https://github.com/Nolek0/Chatbox-project/raw/main/quiz.py",
    "recette.py": "https://github.com/Nolek0/Chatbox-project/raw/main/recette.py",
    "responses.py": "https://github.com/Nolek0/Chatbox-project/raw/main/responses.py",
    "responses_heure.py": "https://github.com/Nolek0/Chatbox-project/raw/main/responses_heure.py",
    "responses_inapproprié.py": "https://github.com/Nolek0/Chatbox-project/raw/main/responses_inapproprié.py"
}



for file_name in files_to_delete:
    file_path = os.path.join(script_folder, file_name)
    if os.path.exists(file_path):
        print(f"Suppression de l'ancien fichier {file_name}...")
        os.remove(file_path)

# Téléchargement des nouveaux fichiers depuis GitHub
for file_name, url in files_to_download.items():
    output_file = os.path.join(script_folder, file_name)
    print(f"Téléchargement de {file_name} depuis {url}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"{file_name} téléchargé avec succès.")
    else:
        print(f"Échec du téléchargement de {file_name}. Statut {response.status_code}")

# Importer et utiliser les modules si nécessaire
from recette import recettes
from responses import responses
from responses_heure import phrases_heure
from responses_inapproprié import mots_interdits
from quiz import quiz_questions

# Utiliser les modules importés selon vos besoins
print("Tous les fichiers ont été téléchargés et les modules ont été importés avec succès.")

load_dotenv('api.env')
weather_api_key = os.getenv('WEATHER_API_KEY')
football_api_key = os.getenv('FOOTBALL_API_KEY')



engine = pyttsx3.init()
pygame.init()

# Délai d'inactivité en secondes
INACTIVITY_TIMEOUT = 30  # Réinitialisation après 30 secondes d'inactivité
last_interaction_time = datetime.datetime.now()

# Fichier pour la liste de courses
course_file = "course.txt"

# Sons
SON_REVEIL = "reveil.mp3"

def play_sound_entree():
    pygame.mixer.music.load('sons-repere.mp3')
    pygame.mixer.music.play()

def play_sound_sortie():
    pygame.mixer.music.load('sons-sortant.mp3')
    pygame.mixer.music.play()
    
def play_sound_demarrage():
    pygame.mixer.init()  # Initialisation de pygame mixer
    pygame.mixer.music.load('demarrage.mp3')
    pygame.mixer.music.play()    

def play_sound_reveil():
    pygame.mixer.music.load(SON_REVEIL)
    pygame.mixer.music.play()

def reconnaissance_vocale(timeout=10):
    global last_interaction_time
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("En attente d'une réponse...")
            audio = r.listen(source, timeout=timeout)
            query = r.recognize_google(audio, language='fr-FR')
            print(f"Vous avez dit: {query}")
            last_interaction_time = datetime.datetime.now()  # Met à jour le temps de la dernière interaction
            return query.lower()
        except sr.UnknownValueError:
            print("Désolé, je n'ai pas compris ce que vous avez dit.")
        except sr.RequestError as e:
            print(f"Erreur lors de la demande à Google : {str(e)}")
        except sr.WaitTimeoutError:
            print("Délai d'attente écoulé. Aucune phrase détectée.")
        return None  # Retourner None si aucune réponse n'a été capturée
    



def faire_quiz(nombre_questions):
    questions_selectionnees = random.sample(list(quiz_questions.items()), nombre_questions)
    score = 0

    for question, reponses in questions_selectionnees:
        engine.say(question)
        engine.runAndWait()

        user_input = reconnaissance_vocale(timeout=10)

        if user_input and any(reponse.lower() in user_input.lower() for reponse in reponses):
            score += 1
            engine.say("Correct !")
            engine.runAndWait()
        else:
            engine.say("Incorrect. La bonne réponse était " + ", ".join(reponses))
            engine.runAndWait()

    engine.say(f"Quiz terminé ! Votre score est de {score}/{nombre_questions}.")
    engine.runAndWait()

    print(f"IA: Quiz terminé ! Votre score est de {score}/{nombre_questions}.")

# Intégration dans votre boucle principale

def est_mot_interdit(mot):
    return mot in mots_interdits


def obtenir_score_match(equipe1, equipe2):
    date_match = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f'https://api.football-data.org/v2/matches'
    
    headers = {
        'X-Auth-Token': football_api_key
    }
    params = {
        'dateFrom': date_match,
        'dateTo': date_match,
        'team1': equipe1,
        'team2': equipe2
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if response.status_code == 200:
            for match in data['matches']:
                if (equipe1.lower() in match['homeTeam']['name'].lower() and 
                    equipe2.lower() in match['awayTeam']['name'].lower()) or \
                   (equipe2.lower() in match['homeTeam']['name'].lower() and 
                    equipe1.lower() in match['awayTeam']['name'].lower()):
                    home_team = match['homeTeam']['name']
                    away_team = match['awayTeam']['name']
                    home_score = match['score']['fullTime']['homeTeam']
                    away_score = match['score']['fullTime']['awayTeam']
                    return f"Le score du match entre {home_team} et {away_team} est {home_score} à {away_score}."
            return f"Aucun match trouvé entre {equipe1} et {equipe2} aujourd'hui."
        else:
            return f"Erreur: {data['message']} (Code: {response.status_code})"
    except Exception as e:
        return f"Une erreur s'est produite : {str(e)}"






def ajouter_evenement_a_agenda(evenement):
    with open('agenda.txt', 'a', encoding='utf-8') as f:
        f.write(evenement + "\n")

def lister_agenda():
    if not os.path.exists('agenda.txt'):
        return "L'agenda est vide."

    with open('agenda.txt', 'r', encoding='utf-8') as f:
        evenements = f.readlines()

    if not evenements:
        return "L'agenda est vide."

    return "Voici les événements dans votre agenda :\n" + "".join(evenement.strip() + "\n" for evenement in evenements)

def supprimer_agenda():
    if os.path.exists('agenda.txt'):
        os.remove('agenda.txt')
        return "L'agenda a été supprimé."
    else:
        return "Il n'y a pas d'agenda à supprimer."




def reset_script():
    global last_interaction_time
    print("Réinitialisation du script...")
    last_interaction_time = datetime.datetime.now()  # Réinitialise le temps de la dernière interaction

def check_inactivity():
    global last_interaction_time
    current_time = datetime.datetime.now()
    elapsed_time = (current_time - last_interaction_time).total_seconds()
    if elapsed_time >= INACTIVITY_TIMEOUT:
        reset_script()

def ajouter_a_liste_course(item):
    with open(course_file, 'a') as f:
        f.write(item + "\n")

def lire_liste_course():
    if not os.path.exists(course_file):
        return "La liste de courses est vide."
    
    with open(course_file, 'r') as f:
        items = f.readlines()
    
    if not items:
        return "La liste de courses est vide."
    
    return "Voici les éléments dans votre liste de courses : " + ", ".join(item.strip() for item in items)

def supprimer_liste_course():
    if os.path.exists(course_file):
        os.remove(course_file)
        return "La liste de courses a été supprimée."
    else:
        return "Il n'y a pas de liste de courses à supprimer."

def obtenir_meteo_ville(ville):
    base_url = 'http://api.weatherapi.com/v1/current.json'
    params = {
        'key': weather_api_key,
        'q': ville,
        'lang': 'fr'
    }
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if 'error' in data:
            message = f"Erreur: {data['error']['message']}"
        else:
            condition = data['current']['condition']['text']
            temperature = data['current']['temp_c']
            message = f"A {ville}, il fait actuellement {temperature} degrés Celsius avec un ciel {condition}."
    except Exception as e:
        message = f"Une erreur s'est produite : {str(e)}"
    
    return message

def demarrer_minuteur(minutes):
    print(f"Démarrage d'un minuteur de {minutes} minutes...")
    timer = Timer(minutes * 60, on_minuteur_termine)
    timer.start()

def on_minuteur_termine():
    print("Minuteur terminé !")
    play_sound_reveil()
    
def check_intro_file():
    intro_file_path = "intro.txt"
    if not os.path.exists(intro_file_path):
        with open(intro_file_path, "w") as f:
            f.write("intro = true\n")
        return True
    else:
        with open(intro_file_path, "r") as f:
            line = f.readline().strip()
            if line == "intro = true":
                return True
            else:
                return False

def traduire_phrase(phrase, langue_cible):
    translator = Translator(to_lang=langue_cible, from_lang='fr')
    try:
        traduction = translator.translate(phrase)
        return traduction
    except Exception as e:
        print(f"Erreur de traduction : {str(e)}")
        return None

def demander_epellation(reponse):
    engine.say(f"Voulez-vous que je l'épelle ?")
    engine.runAndWait()

    user_input = reconnaissance_vocale(timeout=10)

    if user_input:
        if "oui" in user_input.lower() or "ouais" in user_input.lower():
            engine.runAndWait()
            for lettre in reponse:
                engine.say(lettre)
                engine.runAndWait()
        elif "non" in user_input.lower() or "no" in user_input.lower():
            pass  # Ne fait rien si l'utilisateur dit non
        else:
            engine.say("Je n'ai pas compris votre réponse. Je vais passer à la question suivante.")
            engine.runAndWait()
    else:
        engine.say("Désolé, je n'ai pas entendu de réponse. Je vais passer à la question suivante.")
        engine.runAndWait()

def calculer_expression(expression):
    # Cette fonction évalue une expression mathématique simple
    # par exemple "calcule 5 + 3" ou "divise 10 par 2"
    mots = expression.split()
    if len(mots) != 3:
        return None
    
    nombre1 = mots[0]
    operateur = mots[1]
    nombre2 = mots[2]

    try:
        # Remplacement des mots clés par les symboles mathématiques correspondants
        if operateur == 'plus':
            operateur = '+'
        elif operateur == 'moins':
            operateur = '-'
        elif operateur == 'multiplié':
            operateur = '*'
        elif operateur == 'divisé':
            operateur = '/'
        
        # Évaluation de l'expression
        resultat = eval(nombre1 + operateur + nombre2)
        
        return str(resultat)
    
    except ValueError:
        return None
    except ZeroDivisionError:
        return "Division par zéro impossible."
    except Exception as e:
        print(f"Erreur lors du calcul de l'expression : {str(e)}")
        return None

def parler_plus_vite():
    vitesse_actuelle = engine.getProperty('rate')
    engine.setProperty('rate', vitesse_actuelle + 50)
    engine.say("Je parle maintenant plus vite.")
    engine.runAndWait()

def parler_moins_vite():
    vitesse_actuelle = engine.getProperty('rate')
    engine.setProperty('rate', vitesse_actuelle - 50)
    engine.say("Je parle maintenant moins vite.")
    engine.runAndWait()

def parler_normalement():
    engine.setProperty('rate', 200)  # Remplacez 200 par la valeur de votre vitesse de base
    engine.say("Je parle maintenant normalement.")
    engine.runAndWait()

def main():
    play_sound_demarrage()
    global engine  # Déclare engine comme variable globale
    
    time.sleep(2)
    
    # Vérifie si l'introduction doit être jouée
    play_intro = check_intro_file()

    if play_intro:
        # Initialisation du moteur de synthèse vocale
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)  # Sélectionne la première voix par défaut
        engine.say("Bienvenue sur le chatbot. Pour me parler, dites 'OK Assistant' suivi de votre question.")
        engine.runAndWait()

        # Met à jour intro.txt pour indiquer que l'introduction a été jouée
        with open("intro.txt", "w") as f:
            f.write("intro = false\n")

    global last_interaction_time
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    print("Bienvenue ! Posez-moi des questions.")
    listening = False
    timer = None

    phrase_traduire = None
    attente_langue = False

    # Mapping des noms de langues en français aux codes de langues
    langues_supportees = {
        "anglais": "en",
        "espagnol": "es",
        "allemand": "de",
        "italien": "it",
        "portugais": "pt",
        "néerlandais": "nl",
        "russe": "ru",
        "chinois": "zh-cn",
        "japonais": "ja",
        "arabe": "ar"
    }

    while True:
        user_input = reconnaissance_vocale()

        if not user_input:
            check_inactivity()  # Vérifie le temps d'inactivité

        if not user_input:
            continue
        if timer:
            timer.cancel()  
            timer = None

        if user_input and "ok assistant" in user_input:
            print("Activation de l'assistant...")
            play_sound_entree() 
            listening = True
            last_interaction_time = datetime.datetime.now()  # Met à jour le temps de la dernière interaction
            continue

        if not listening:
            continue

        if user_input:
            if est_mot_interdit(user_input):
                print("IA: Je ne répondrai pas à cela.")
                engine.say("Je ne répondrai pas à cela. Le mot utilisé peut être à usage inaproprié")
                play_sound_sortie()
                engine.runAndWait()
                listening = False 
                continue

            if "parle plus vite" in user_input:
                parler_plus_vite()
                listening = False
                continue

            if "parle plus lentement" in user_input:
                parler_moins_vite()
                listening = False
                continue

            if "parle normalement" in user_input:
                parler_normalement()
                listening = False
                continue


            if attente_langue:
                langue_cible = user_input.strip()
                if langue_cible in langues_supportees:
                    code_langue = langues_supportees[langue_cible]
                    if phrase_traduire:
                        traduction = traduire_phrase(phrase_traduire, code_langue)
                        if traduction:
                            print(f"Traduction en {langue_cible}: {traduction}")
                            engine.say(f"Traduction en {langue_cible}: {traduction}")
                            engine.runAndWait()
                            demander_epellation(traduction)
                        else:
                            print(f"IA: Désolé, je n'ai pas pu traduire en '{langue_cible}'.")
                            engine.say(f"Désolé, je n'ai pas pu traduire en '{langue_cible}'.")
                            engine.runAndWait()
                        play_sound_sortie()
                    else:
                        print("IA: Désolé, je n'ai pas compris la demande de traduction.")
                        engine.say("Désolé, je n'ai pas compris la demande de traduction.")
                        engine.runAndWait()
                    attente_langue = False
                    listening = False
                    continue
                else:
                    print("IA: Désolé, je n'ai pas compris la langue spécifiée.")
                    engine.say("Désolé, je n'ai pas compris la langue spécifiée.")
                    engine.runAndWait()
                    attente_langue = False
                    listening = False
                    continue
                
           # À ajouter dans la boucle principale où vous traitez les commandes utilisateur
            if "score du match entre" in user_input.lower():
                        match = re.search(r"score du match entre (.+) et (.+)", user_input.lower())
                        if match:
                            equipe1 = match.group(1).strip()
                            equipe2 = match.group(2).strip()
                            score = obtenir_score_match(equipe1, equipe2)
                            print(f"IA: {score}")
                            engine.say(score)
                            engine.runAndWait()
                        else:
                            print("IA: Désolé, je n'ai pas compris la demande de score de match.")
                            engine.say("Désolé, je n'ai pas compris la demande de score de match.")
                            engine.runAndWait()
            

            if re.search(r"\bmétéo\b|\btemps\b", user_input.lower()):
                match = re.search(r"\b(?:météo|temps)\b(?:\s+(?:de|à)?\s+)?(\w+)", user_input.lower())
                if match:
                    ville = match.group(1)
                    meteo = obtenir_meteo_ville(ville)
                    if "erreur" in meteo.lower():
                        print(f"IA: {meteo}")  
                        engine.say(meteo)
                    else:
                        print(f"IA: {meteo}")
                        engine.say(meteo)
                    play_sound_sortie() 
                    engine.runAndWait()
                else:
                    print("IA: Désolé, je n'ai pas compris la demande de météo.")
                listening = False  
                continue

            if "quelle heure" in user_input.lower() or "l'heure" in user_input.lower():
                current_time = datetime.datetime.now().strftime("%H:%M")
                print(f"Heure actuelle: {current_time}")
                phrase = random.choice(phrases_heure).format(heure=current_time)
                print(f"IA: {phrase}")
                engine.say(phrase)
                play_sound_sortie() 
                engine.runAndWait()
                listening = False 
                continue

            # Commande pour obtenir la date du jour
            if re.search(r"\bdate\b|\bjour\b", user_input.lower()):
                current_date = datetime.datetime.now().strftime("%A %d %B %Y")
                print(f"Date du jour: {current_date}")
                
                # Demander la langue pour la traduction
                if phrase_traduire:
                    engine.say("En quelle langue souhaitez-vous la date ?")
                    engine.runAndWait()
                    attente_langue = True
                    continue
                
                # Si aucune traduction n'est demandée, dire la date directement
                engine.say(f"Aujourd'hui, nous sommes le {current_date}.")
                engine.runAndWait()
                play_sound_sortie()
                listening = False
                continue
            
            
            if re.search(r"\brecette\s+de\b", user_input.lower()):
                match = re.search(r"\brecette\s+de\b\s+(.+)", user_input.lower())
                if match:
                    plat = match.group(1).strip()
                    if plat in recettes:
                        recette = recettes[plat]
                        pre_requis = ", ".join(recette["pre_requis"])
                        instructions = "\n".join(recette["instructions"])

                        engine.say(f"Pour faire {plat}, vous avez besoin de {pre_requis}. Voici les instructions détaillées : {instructions}")
                        engine.runAndWait()
                    else:
                        engine.say(f"Désolé, je n'ai pas la recette pour {plat}.")
                        engine.runAndWait()
                    listening = False
                    continue
            
            
            # Commande pour démarrer un minuteur
            if re.search(r"\bminuteur\b.*(\d+)\s+minutes?", user_input.lower()):
                match = re.search(r"\bminuteur\b.*(\d+)\s+minutes?", user_input.lower())
                if match:
                    minutes = int(match.group(1))
                    demarrer_minuteur(minutes)
                    engine.say(f"Minuteur démarré pour {minutes} minutes.")
                    engine.runAndWait()
                    listening = False
                else:
                    print("IA: Désolé, je n'ai pas compris la demande de minuterie.")
                continue

            # Commande pour traduire
            if re.search(r"\btraduction\b.*", user_input.lower()):
                match = re.search(r"\btraduction\b(.+)", user_input.lower())
                if match:
                    phrase_traduire = match.group(1).strip()
                    print(f"Traduction de '{phrase_traduire}'...")
                    engine.say("En quelle langue souhaitez-vous traduire ?")
                    engine.runAndWait()
                    attente_langue = True
                else:
                    print("IA: Désolé, je n'ai pas compris la demande de traduction.")
                continue

            # Commande pour calculer
            if re.search(r"\bcalcule\b.*", user_input.lower()):
                match = re.search(r"\bcalcule\b(.+)", user_input.lower())
                if match:
                    expression = match.group(1).strip()
                    resultat = calculer_expression(expression)
                    if resultat:
                        print(f"IA: Le résultat de '{expression}' est {resultat}.")
                        engine.say(f"Le résultat est {resultat}.")
                        engine.runAndWait()
                    else:
                        print("IA: Désolé, je n'ai pas compris l'expression mathématique.")
                    play_sound_sortie()
                else:
                    print("IA: Désolé, je n'ai pas compris la demande de calcul.")
                listening = False
                continue
            
            


            # Commandes spécifiques pour la gestion de la liste de courses
            if re.search(r"\bajoute\s+.*\s+à\s+ma\s+liste\s+de\s+courses\b", user_input.lower()):
                match = re.search(r"\bajoute\s+(.*)\s+à\s+ma\s+liste\s+de\s+courses\b", user_input.lower())
                if match:
                    item = match.group(1).strip()
                    ajouter_a_liste_course(item)
                    print(f"IA: '{item}' a été ajouté à votre liste de courses.")
                    engine.say(f"'{item}' a été ajouté à votre liste de courses.")
                    engine.runAndWait()
                    play_sound_sortie()
                else:
                    print("IA: Désolé, je n'ai pas compris la demande d'ajout à la liste de courses.")
                listening = False
                continue

            if "lis ma liste de courses" in user_input.lower() or "quelle est ma liste de courses" in user_input.lower():
                liste_courses = lire_liste_course()
                print(f"IA: {liste_courses}")
                engine.say(liste_courses)
                engine.runAndWait()
                continue

            if "supprime ma liste de courses" in user_input.lower():
                message = supprimer_liste_course()
                print(f"IA: {message}")
                engine.say(message)
                engine.runAndWait()
                continue
            if "ajoute un événement à mon agenda" in user_input.lower():
                        match = re.search(r"ajoute un événement à mon agenda (.+)", user_input.lower())
                        if match:
                            evenement = match.group(1).strip()
                            ajouter_evenement_a_agenda(evenement)
                            print(f"IA: '{evenement}' a été ajouté à votre agenda.")
                            engine.say(f"'{evenement}' a été ajouté à votre agenda.")
                            engine.runAndWait()
                        else:
                            print("IA: Désolé, je n'ai pas compris la demande d'ajout à l'agenda.")
                        continue


            if "liste mon agenda" in user_input.lower() or "quels sont mes événements" in user_input.lower():
                        agenda = lister_agenda()
                        print(f"IA: {agenda}")
                        engine.say(agenda)
                        engine.runAndWait()
                        continue

            if "supprime mon agenda" in user_input.lower():
                        message = supprimer_agenda()
                        print(f"IA: {message}")
                        engine.say(message)
                        engine.runAndWait()
                        continue


            for key in responses:
                if user_input.startswith(key.lower()):
                    response = random.choice(responses[key])
                    play_sound_sortie()
                    print("IA: ", response)
                    engine.say(response)
                    engine.runAndWait()
                    listening = False 
                    break
            else:
                print("IA: Désolé, je ne comprends pas bien. Pouvez-vous reformuler votre question ?")
                engine.runAndWait()
        

                

if __name__ == "__main__":
    main()