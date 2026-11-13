import os
import random
from datetime import datetime, timedelta

def generer_script_sql():
    random.seed(42)

    lignes = []

    salles = [
        ("SALLE-MAYA", "Le Mystere du Temple Maya", 6),
        ("SALLE-LABO", "Le Laboratoire Clandestin", 6),
        ("SALLE-MANOIR", "Les Secrets du Manoir Noir", 5),
        ("SALLE-PRISON", "L Evasion d Alcatraz", 6)
    ]
    for code, nom, cap in salles:
        lignes.append(f"INSERT INTO salle (code_salle, nom, capacite_max) VALUES ('{code}', '{nom}', {cap});")

    enigmes = [
        ("Le disque d or aztèque", 3, 1),
        ("Le rébus des hiéroglyphes", 2, 1),
        ("La porte du sanctuaire", 4, 1),
        ("La fiole d antidote", 4, 2),
        ("Le code du séquenceur ADN", 3, 2),
        ("L alarme laser", 5, 2),
        ("Le journal intime du comte", 2, 3),
        ("Le mécanisme de l horloge", 3, 3),
        ("Le passage secret de la bibliothèque", 4, 3),
        ("Le conduit de ventilation", 3, 4),
        ("Le digicode du gardien", 2, 4),
        ("Le tunnel d évacuation", 4, 4)
    ]
    for titre, diff, id_s in enigmes:
        lignes.append(f"INSERT INTO enigme (titre, difficulte, id_salle) VALUES ('{titre}', {diff}, {id_s});")

    joueurs = [
        ("alice.martin@example.com", "Alice Martin", "0601020304"),
        ("bob.durand@example.com", "Bob Durand", "0611223344"),
        ("charlie.leroy@example.com", "Charlie Leroy", "0622334455"),
        ("diane.morel@example.com", "Diane Morel", "0633445566"),
        ("etienne.petit@example.com", "Etienne Petit", "0644556677"),
        ("fanny.roux@example.com", "Fanny Roux", "0655667788"),
        ("gabriel.mercier@example.com", "Gabriel Mercier", "0666778899"),
        ("helene.blanc@example.com", "Helene Blanc", "0677889900"),
        ("igor.guerin@example.com", "Igor Guerin", "0688990011"),
        ("julie.faure@example.com", "Julie Faure", "0699001122"),
        ("kevin.dupont@example.com", "Kevin Dupont", "0612345678"),
        ("lea.bonnet@example.com", "Lea Bonnet", "0623456789")
    ]
    for email, nom, tel in joueurs:
        lignes.append(f"INSERT INTO joueur (email, nom, telephone) VALUES ('{email}', '{nom}', '{tel}');")

    equipes = [
        "Les Detectives du Dimanche",
        "Escape Masters",
        "La Bande du Casse",
        "Team Chrono"
    ]
    for nom_eq in equipes:
        lignes.append(f"INSERT INTO equipe (nom_equipe) VALUES ('{nom_eq}');")

    compositions = [
        (1, 1), (1, 2), (1, 3),
        (2, 4), (2, 5), (2, 6), (2, 7),
        (3, 8), (3, 9), (3, 10),
        (4, 11), (4, 12), (4, 1), (4, 2)
    ]
    for eq, jo in compositions:
        lignes.append(f"INSERT INTO composition_equipe (id_equipe, id_joueur) VALUES ({eq}, {jo});")

    indices = [
        ("IND-01", "Regardez sous la dalle centrale."),
        ("IND-02", "Les chiffres sont l inverse de l annee d or."),
        ("IND-03", "La fiole bleue annule le reactif rouge."),
        ("IND-04", "Le commutateur est dissimule derriere le tableau."),
        ("IND-05", "L aiguille s arrete toujours sur le chiffre 7."),
        ("IND-06", "La grille s ouvre par une pression simultanee."),
        ("IND-07", "La cle en cuivre correspond au cadenas gauche."),
        ("IND-08", "Le mot de passe se lit en miroir.")
    ]
    for code_ind, desc in indices:
        lignes.append(f"INSERT INTO indice (code_indice, description) VALUES ('{code_ind}', '{desc}');")

    reservations = [
        ("RES-2026-001", "2026-11-14 10:00:00", "TERMINEE", 120.00, 1, 1),
        ("RES-2026-002", "2026-11-14 14:00:00", "TERMINEE", 120.00, 1, 2),
        ("RES-2026-003", "2026-11-14 16:30:00", "CONFIRMEE", 140.00, 2, 3),
        ("RES-2026-004", "2026-11-15 11:00:00", "EN_ATTENTE", 130.00, 3, 4),
        ("RES-2026-005", "2026-11-15 15:00:00", "ANNULEE", 0.00, 4, 1),
        ("RES-2026-006", "2026-11-15 18:00:00", "CONFIRMEE", 140.00, 2, 2)
    ]
    for code_res, date_h, statut, mt, id_s, id_eq in reservations:
        lignes.append(f"INSERT INTO reservation (code_reservation, date_heure_debut, statut, montant_paye, id_salle, id_equipe) VALUES ('{code_res}', '{date_h}', '{statut}', {mt:.2f}, {id_s}, {id_eq});")

    indices_consommes = [
        (1, 1, "10:22:00", 3),
        (1, 2, "10:45:00", 5),
        (2, 3, "14:15:00", 3),
        (2, 4, "14:38:00", 3),
        (3, 5, "16:50:00", 4)
    ]
    for id_res, id_ind, hd, pen in indices_consommes:
        lignes.append(f"INSERT INTO indice_consomme (id_reservation, id_indice, heure_demande, penalite_minutes) VALUES ({id_res}, {id_ind}, '{hd}', {pen});")

    avis = [
        (1, 5, "Decors immersifs magnifiques et superbes enigmes !"),
        (2, 4, "Tres bonne experience mais quelques indices un peu trop complexes.")
    ]
    for id_res, note, comm in avis:
        lignes.append(f"INSERT INTO avis (id_reservation, note, commentaire) VALUES ({id_res}, {note}, '{comm}');")

    dossier = os.path.dirname(os.path.abspath(__file__))
    fichier_sortie = os.path.join(dossier, "donnees.sql")
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        for ligne in lignes:
            f.write(ligne + "\n")

if __name__ == "__main__":
    generer_script_sql()
