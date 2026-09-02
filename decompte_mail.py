"""
Script d'envoi automatique d'un mail quotidien avec :
- décompte des jours restants jusqu'à la fin de l'année scolaire
- alerte quand un conseil de classe / une fin de trimestre approche

Utilise Gmail (SMTP) avec un "mot de passe d'application".
Pensé pour tourner via GitHub Actions (gratuit) une fois par jour.
"""

import smtplib
from email.mime.text import MIMEText
from datetime import date
import os

# ============ CONFIG A PERSONNALISER ============

EMAIL_EXPEDITEUR = "kirito.uhq@gmail.com"
EMAIL_DESTINATAIRE = "ethanboulenc@gmail.com"

# Le mot de passe d'application est lu depuis une variable d'environnement
# (jamais écrit en clair dans le code, voir instructions de setup)
MOT_DE_PASSE_APP = os.environ["GMAIL_APP_PASSWORD"]

FIN_ANNEE_SCOLAIRE = date(2027, 7, 5)  # <-- à ajuster

# Liste de tes échéances importantes : (nom, date)
ECHEANCES = [
    ("Conseil de classe - Trimestre 1", date(2026, 12, 15)),
    ("Fin du Trimestre 1", date(2026, 12, 19)),
    ("Conseil de classe - Trimestre 2", date(2027, 3, 16)),
    ("Fin du Trimestre 2", date(2027, 3, 20)),
    ("Conseil de classe - Trimestre 3", date(2027, 6, 15)),
    ("Fin du Trimestre 3 / Année", date(2027, 7, 5)),
]

JOURS_ALERTE = 14  # affiche une échéance si elle est dans les X prochains jours

# ==================================================


def construire_message():
    aujourdhui = date.today()
    jours_restants = (FIN_ANNEE_SCOLAIRE - aujourdhui).days

    lignes = [
        f"📅 Nous sommes le {aujourdhui.strftime('%d/%m/%Y')}",
        f"🎓 Il reste {jours_restants} jour(s) avant la fin de l'année scolaire ({FIN_ANNEE_SCOLAIRE.strftime('%d/%m/%Y')})",
        "",
    ]

    echeances_proches = []
    for nom, d in ECHEANCES:
        delta = (d - aujourdhui).days
        if 0 <= delta <= JOURS_ALERTE:
            echeances_proches.append((nom, d, delta))

    if echeances_proches:
        lignes.append("⚠️ Échéances qui approchent :")
        for nom, d, delta in sorted(echeances_proches, key=lambda x: x[2]):
            lignes.append(f"  - {nom} : dans {delta} jour(s) (le {d.strftime('%d/%m/%Y')})")
    else:
        lignes.append("Aucune échéance dans les 14 prochains jours.")

    return "\n".join(lignes)


def envoyer_mail():
    corps = construire_message()
    msg = MIMEText(corps)
    msg["Subject"] = f"Décompte du {date.today().strftime('%d/%m/%Y')}"
    msg["From"] = EMAIL_EXPEDITEUR
    msg["To"] = EMAIL_DESTINATAIRE

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as serveur:
        serveur.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_APP)
        serveur.sendmail(EMAIL_EXPEDITEUR, [EMAIL_DESTINATAIRE], msg.as_string())

    print("Mail envoyé avec succès.")


if __name__ == "__main__":
    envoyer_mail()
