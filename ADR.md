# ADR 0001 : Choix du SGBD principal pour le système d'Escape Game

* **Statut** : Accepté
* **Date** : 10 novembre 2026
* **Auteurs** : Équipe TP CAD B3

---

## 1. Contexte et Problématique

Notre projet concerne la gestion complète d'une enseigne d'escape game : planification des créneaux, enregistrement des équipes, réservation sans risque de surréservation, suivi en temps réel des indices consommés par session et collecte d'avis clients.

Le modèle repose sur des données fortement structurées et interconnectées :
* **Anti-surréservation critique** : Une même salle ne peut en aucun cas être réservée deux fois sur le même créneau horaire (RG4, RG5). Deux transactions concurrentes essayant de réserver le même créneau doivent être arbitrées avec certitude.
* **Relations denses** : Des cardinalités multi-entités (équipes composées de plusieurs joueurs, sessions liées aux indices et aux salles).
* **Traçabilité financière** : Chaque réservation porte un montant payé et un statut contractuel (RG10).
* **Volumétrie modérée mais intégrité absolue** : Nous privilégions la consistance immédiate et l'isolation transactionnelle plutôt que le passage à l'échelle horizontal massif.

---

## 2. Options envisagées

Nous avons comparé trois familles de bases de données :

1. **Option 1 : PostgreSQL (SGBD Relationnel / SQL)**
2. **Option 2 : MongoDB (Orienté Document / NoSQL)**
3. **Option 3 : Neo4j (Orienté Graphe / NoSQL)**

---

## 3. Matrice d'évaluation et Comparaison

| Critère d'évaluation | PostgreSQL (Relationnel) | MongoDB (Document) | Neo4j (Graphe) |
| :--- | :--- | :--- | :--- |
| **Forme des données** | Tables relationnelles normalisées (3NF). Clés étrangères et contraintes d'unicité naturelles. | Documents JSON hiérarchiques. Obligation de choisir entre imbrication ou référencement manuel (`$lookup`). | Nœuds et relations typées. Idéal pour les réseaux, verbeux pour les simples tables de faits. |
| **Garanties ACID & Écritures** | ACID complet et éprouvé. Verrous de ligne, isolation `SERIALIZABLE`, contraintes d'exclusion temporelle natives (`EXCLUDE USING gist`). | ACID multi-documents supporté mais coûteux. Risque d'incohérence si modélisé par documents dénormalisés. | Transactions ACID respectées, mais l'arbitrage de concurrence sur créneaux d'horaires n'est pas son cœur de métier. |
| **Prévention de la survente** | Immédiate et infaillible via contraintes SQL d'unicité (`UNIQUE(id_salle, date_heure_debut)`). | Difficile : nécessite des transactions distribuées ou un contrôle optimiste manuel sujet aux conflits. | Faisable via verrou sur nœud créneau, mais surdimensionné et complexe à paramétrer. |
| **Lectures & Requêtes** | Jointures SQL très performantes pour regrouper Équipe, Joueurs, Salle et Indices consommés. | Excellente lecture si tout est imbriqué dans la réservation, mais redondance forte des données de joueurs/salles. | Requêtes Cypher optimales pour parcourir des liens profonds ("joueurs ayant fait les mêmes salles"), moins pertinent pour un planning. |

### Détail des alternatives écartées :

* **Pourquoi pas MongoDB ?**  
  Bien que l'imbrication d'un avis ou de la liste des indices dans le document d'une session soit séduisante, la gestion des créneaux et des réservations concurrentes est plus vulnérable. Si un joueur modifie ses coordonnées ou fait partie de plusieurs équipes, la redondance dans les documents impose des mises à jour en cascade. Les jointures inter-collections (`$lookup`) restent moins performantes et moins naturelles qu'en relationnel.
  
* **Pourquoi pas Neo4j ?**  
  Le moteur graphe est excellent pour recommander une salle en fonction des énigmes déjà résolues par un joueur ("les amis de X qui ont aimé l'énigme Y ont réservé la salle Z"). Cependant, notre besoin primaire est transactionnel, centré sur la réservation, les statuts de paiement et les plannings. Employer Neo4j comme base principale complexifierait inutilement les règles de validation et l'écriture des données tabulaires simples.

---

## 4. Décision retenue

Nous retenons **PostgreSQL** comme base de données principale.

PostgreSQL offre la rigueur relationnelle indispensable pour respecter nos règles de gestion (clés étrangères, contraintes de vérification `CHECK` sur les notes et les seuils de joueurs, contraintes d'unicité sur les créneaux). De plus, son support natif des types temporels et des colonnes `JSONB` permet, si nécessaire, d'adopter une approche hybride pour stocker les métadonnées flexibles d'une énigme.

---

## 5. Stratégie de Normalisation et Dénormalisation

* **Normalisation (3NF retenue par défaut) :**  
  Toutes les entités de base (`JOUEUR`, `EQUIPE`, `SALLE`, `ENIGME`, `RESERVATION`) sont normalisées pour garantir zéro anomalie de mise à jour (ex. l'adresse email d'un joueur n'est stockée qu'à un seul endroit).
* **Dénormalisation ciblée et justifiée :**  
  Nous dénormalisons le champ `penalite_minutes` et le montant total dans la table `RESERVATION` :
  * *Raison :* Le prix payé d'une session et les pénalités calculées au moment où la session s'achève doivent être figés historiquement, même si les tarifs de la salle ou les barèmes d'indices changent ultérieurement.
  * *Gouvernance :* Ce n'est pas une simple copie vivante ; c'est un instantané métier scellé par transaction au moment de la validation de la réservation et de la clôture du chronomètre.

---

## 6. Conséquences et Limites

### Ce que ce choix facilite :
* Intégrité stricte garantie dès la couche de données (impossibilité d'enregistrer deux réservations au même moment dans la même salle).
* Requêtes d'analyse et de reporting simples en SQL standard (taux d'occupation des salles, note moyenne, nombre d'indices moyens par salle).

### Ce que ce choix rend plus difficile :
* **Évolution dynamique des énigmes** : Si chaque énigme intègre des éléments matériels ou technologiques très disparates (capteurs IoT, RFID, cadenas), le modèle relationnel figé imposera des colonnes à valeurs nulles ou une table d'attributs clés/valeurs (EAV).
* **Scalabilité en écriture temps réel** : Si le système devait un jour capter les données de capteurs en salle à la milliseconde, PostgreSQL nécessiterait une infrastructure de réplication plus lourde qu'une base orientée colonnes larges ou séries temporelles.

### Ce qui nous ferait revoir notre décision :
* Un pivot du produit vers une plateforme sociale de matching de joueurs ou un moteur de recommandation basé sur les affinités et l'historique complet des parcours : nous introduirions alors **Neo4j** en base secondaire.
* L'ajout d'une télémétrie en direct des capteurs de la salle pendant le jeu : nous ajouterions un cache en mémoire (**Redis**) pour le live et une base time-series (**TimescaleDB** ou **Cassandra**) pour les métriques.