# Liste des mots interdits
mots_interdits = [
    "fils de pute", "negro", "gay", "pd", "bougnoule", "feuj", "encule", "pute",
    "connard", "salope", "enculé", "merde", "trou du cul", "tapette", "sodomite",
    "salaud", "nazi", "nègre", "enculer", "cul", "bâtard", "connasse",
    "pédé", "tarlouze", "pouffiasse", "branleur", "crétin", "pétasse", "casse-couilles",
    "gueule", "bite", "bouseux", "pénis", "vagin", "bordel", "bouse", "couille",
    "crotte", "débile", "dégueulasse", "détritus", "étron", "facho", "fasciste",
    "flûte", "garce", "gogole", "gros con", "grosse merde", "lèche-cul", "mongol",
    "naze", "niais", "niaiseux", "niquer", "ordure", "pedzouille", "pignouf", "piné", "pipe",
    "plouc", "porc", "prout", "purée", "putain", "racaille", "sac à merde",
    "salopard", "sauvage", "sexe", "sperme", "tafiole", "taré", "tocard",
    "trou du cul", "vaurien", "viande à kebab", "vieux schnock", "youpin", "zigoto", "zizi", "nike ta mère", "Niques ta mère", "nique ta mère", "nikes ta mère", "koufar", "quoufar",
    "Négresse", "Boule de viande", "Gros lard", "Gros lardon", "Gros sac", "Gros sac à merde", "Grosse merde", "hijo de puta", "Enculé de tes morts", "Sale fils de pute", "sale batard",
    "hitler", "mussolini","Staline", "Sale enculé de tes morts", "eh va niquer ta mère enculé", "poufiasse"
]

def est_mot_interdit(mot):
    mot = mot.lower()  
    return any(mot in phrase.lower() for phrase in mots_interdits)
