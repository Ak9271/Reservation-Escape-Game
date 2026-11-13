SELECT 
    r.code_reservation,
    s.nom AS nom_salle,
    e.nom_equipe,
    r.date_heure_debut,
    r.statut,
    r.montant_paye
FROM reservation r
JOIN salle s ON r.id_salle = s.id_salle
JOIN equipe e ON r.id_equipe = e.id_equipe
WHERE r.statut IN ('CONFIRMEE', 'TERMINEE')
ORDER BY r.date_heure_debut;

SELECT 
    s.nom AS nom_salle,
    COUNT(r.id_reservation) AS total_reservations,
    COALESCE(SUM(r.montant_paye), 0.00) AS chiffre_affaires_total
FROM salle s
LEFT JOIN reservation r ON s.id_salle = r.id_salle AND r.statut != 'ANNULEE'
GROUP BY s.id_salle, s.nom
ORDER BY chiffre_affaires_total DESC;

SELECT 
    r.code_reservation,
    e.nom_equipe,
    s.nom AS nom_salle,
    COUNT(ic.id_indice) AS nombre_indices_demandes,
    COALESCE(SUM(ic.penalite_minutes), 0) AS total_penalite_minutes
FROM reservation r
JOIN equipe e ON r.id_equipe = e.id_equipe
JOIN salle s ON r.id_salle = s.id_salle
LEFT JOIN indice_consomme ic ON r.id_reservation = ic.id_reservation
GROUP BY r.id_reservation, r.code_reservation, e.nom_equipe, s.nom
ORDER BY total_penalite_minutes DESC;

SELECT 
    s.nom AS nom_salle,
    ROUND(AVG(a.note), 2) AS note_moyenne,
    COUNT(a.id_avis) AS nombre_avis
FROM salle s
JOIN reservation r ON s.id_salle = r.id_salle
JOIN avis a ON r.id_reservation = a.id_reservation
GROUP BY s.id_salle, s.nom
ORDER BY note_moyenne DESC;

SELECT 
    e.nom_equipe,
    COUNT(ce.id_joueur) AS nombre_joueurs,
    STRING_AGG(j.nom, ', ') AS membres
FROM equipe e
JOIN composition_equipe ce ON e.id_equipe = ce.id_equipe
JOIN joueur j ON ce.id_joueur = j.id_joueur
GROUP BY e.id_equipe, e.nom_equipe
ORDER BY nombre_joueurs DESC;

SELECT 
    s.nom AS nom_salle,
    en.titre AS titre_enigme,
    en.difficulte
FROM salle s
JOIN enigme en ON s.id_salle = en.id_salle
ORDER BY s.nom, en.difficulte DESC;
