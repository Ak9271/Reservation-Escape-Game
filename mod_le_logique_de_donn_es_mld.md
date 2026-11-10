# Modèle Logique de Données (MLD) - PostgreSQL

Ce document détaille le passage du MCD au MLD relationnel (PostgreSQL) conformément aux règles de dérivation de la séance 1, les données scellées/recopiées exprès, ainsi que les contraintes que le schéma SQL ne garantit pas nativement et les mécanismes retenus pour y remédier.

## 1. Schéma Relationnel Textuel

* **`salle`** (
  **`id_salle`** INT GENERATED ALWAYS AS IDENTITY,
  `code_salle` VARCHAR(30) NOT NULL UNIQUE,
  `nom` VARCHAR(100) NOT NULL,
  `capacite_max` INT NOT NULL,
  CONSTRAINT `pk_salle` PRIMARY KEY (`id_salle`),
  CONSTRAINT `chk_capacite` CHECK (`capacite_max` >= 2)
  )

* **`enigme`** (
  **`id_enigme`** INT GENERATED ALWAYS AS IDENTITY,
  `titre` VARCHAR(120) NOT NULL,
  `difficulte` INT NOT NULL,
  *`id_salle`* INT NOT NULL,
  CONSTRAINT `pk_enigme` PRIMARY KEY (`id_enigme`),
  CONSTRAINT `fk_enigme_salle` FOREIGN KEY (`id_salle`) REFERENCES `salle`(`id_salle`) ON DELETE CASCADE,
  CONSTRAINT `chk_difficulte` CHECK (`difficulte` BETWEEN 1 AND 5)
  )

* **`joueur`** (
  **`id_joueur`** INT GENERATED ALWAYS AS IDENTITY,
  `email` VARCHAR(255) NOT NULL UNIQUE,
  `nom` VARCHAR(100) NOT NULL,
  `telephone` VARCHAR(30),
  CONSTRAINT `pk_joueur` PRIMARY KEY (`id_joueur`)
  )

* **`equipe`** (
  **`id_equipe`** INT GENERATED ALWAYS AS IDENTITY,
  `nom_equipe` VARCHAR(100) NOT NULL,
  CONSTRAINT `pk_equipe` PRIMARY KEY (`id_equipe`)
  )

* **`composition_equipe`** (
  ***`id_equipe`*** INT NOT NULL,
  ***`id_joueur`*** INT NOT NULL,
  `date_adhesion` DATE DEFAULT CURRENT_DATE,
  CONSTRAINT `pk_composition_equipe` PRIMARY KEY (`id_equipe`, `id_joueur`),
  CONSTRAINT `fk_compo_equipe` FOREIGN KEY (`id_equipe`) REFERENCES `equipe`(`id_equipe`) ON DELETE CASCADE,
  CONSTRAINT `fk_compo_joueur` FOREIGN KEY (`id_joueur`) REFERENCES `joueur`(`id_joueur`) ON DELETE RESTRICT
  )

* **`indice`** (
  **`id_indice`** INT GENERATED ALWAYS AS IDENTITY,
  `code_indice` VARCHAR(30) NOT NULL UNIQUE,
  `description` TEXT NOT NULL,
  CONSTRAINT `pk_indice` PRIMARY KEY (`id_indice`)
  )

* **`reservation`** (
  **`id_reservation`** INT GENERATED ALWAYS AS IDENTITY,
  `code_reservation` VARCHAR(30) NOT NULL UNIQUE,
  `date_heure_debut` TIMESTAMP NOT NULL,
  `statut` VARCHAR(20) NOT NULL,
  `montant_paye` NUMERIC(8, 2) NOT NULL,
  *`id_salle`* INT NOT NULL,
  *`id_equipe`* INT NOT NULL,
  CONSTRAINT `pk_reservation` PRIMARY KEY (`id_reservation`),
  CONSTRAINT `fk_res_salle` FOREIGN KEY (`id_salle`) REFERENCES `salle`(`id_salle`) ON DELETE RESTRICT,
  CONSTRAINT `fk_res_equipe` FOREIGN KEY (`id_equipe`) REFERENCES `equipe`(`id_equipe`) ON DELETE RESTRICT,
  CONSTRAINT `uk_salle_creneau` UNIQUE (`id_salle`, `date_heure_debut`),
  CONSTRAINT `chk_statut` CHECK (`statut` IN ('EN_ATTENTE', 'CONFIRMEE', 'TERMINEE', 'ANNULEE')),
  CONSTRAINT `chk_montant` CHECK (`montant_paye` >= 0)
  )

* **`indice_consomme`** (
  ***`id_reservation`*** INT NOT NULL,
  ***`id_indice`*** INT NOT NULL,
  `heure_demande` TIME NOT NULL,
  `penalite_minutes` INT NOT NULL DEFAULT 3,
  CONSTRAINT `pk_indice_consomme` PRIMARY KEY (`id_reservation`, `id_indice`),
  CONSTRAINT `fk_consomme_res` FOREIGN KEY (`id_reservation`) REFERENCES `reservation`(`id_reservation`) ON DELETE CASCADE,
  CONSTRAINT `fk_consomme_indice` FOREIGN KEY (`id_indice`) REFERENCES `indice`(`id_indice`) ON DELETE RESTRICT
  )

* **`avis`** (
  **`id_avis`** INT GENERATED ALWAYS AS IDENTITY,
  *`id_reservation`* INT NOT NULL UNIQUE,
  `note` INT NOT NULL,
  `commentaire` TEXT,
  `date_avis` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `pk_avis` PRIMARY KEY (`id_avis`),
  CONSTRAINT `fk_avis_reservation` FOREIGN KEY (`id_reservation`) REFERENCES `reservation`(`id_reservation`) ON DELETE CASCADE,
  CONSTRAINT `chk_note` CHECK (`note` BETWEEN 1 AND 5)
  )

## 2. Traduction de chaque association du MCD (Règles de passage)

Chaque association du MCD a été intégrée dans le schéma relationnel en respectant rigoureusement les règles de dérivation vues en TD :

| Association MCD | Entités reliées | Cardinalités | Traduction dans le MLD | Justification / Règle de passage | 
| ----- | ----- | ----- | ----- | ----- | 
| **contient** (RG1) | `SALLE` - `ENIGME` | `1,N` – `1,1` | Clé étrangère `id_salle` dans `enigme` | Côté `1,1` : la table `enigme` absorbe la clé primaire de la table `salle`. Pas de table intermédiaire nécessaire. | 
| **compose** (RG3) | `JOUEUR` - `EQUIPE` | `1,N` – `2,N` | Table de liaison `composition_equipe` | Côté `N,N` (plusieurs à plusieurs) : éclatement obligatoire en une table d'association dont la clé primaire est composite (`(id_equipe, id_joueur)`). | 
| **accueille / effectue** (RG4, RG5, RG6) | `SALLE` - `EQUIPE` - `RESERVATION` | `1,N` – `0,N` – `1,1` | Clés étrangères `id_salle` et `id_equipe` dans `reservation` | Une réservation représente l'instance d'un créneau : chaque réservation est rattachée à 1 et 1 seule salle et 1 seule équipe. Ces deux clés migrent donc comme clés étrangères dans `reservation`. | 
| **consomme** (RG7, RG8) | `RESERVATION` - `INDICE` | `0,N` – `0,N` | Table de liaison `indice_consomme` avec données propres | Relation `N,N` porteuse de données métier (`heure_demande`, `penalite_minutes`). Elle devient une table dont la clé primaire est le couple `(id_reservation, id_indice)`. | 
| **donne lieu a** (RG9) | `RESERVATION` - `AVIS` | `0,1` – `1,1` | Clé étrangère unique `id_reservation` dans `avis` | Association `0,1` vers `1,1`. La table `avis` porte la référence vers `reservation` avec une contrainte `UNIQUE` sur `id_reservation` pour interdire plusieurs avis pour une même session. | 

## 3. Ce que l'on recopie exprès (Dénormalisation & Données scellées)

Dans une modélisation purement normalisée, certains montants ou pénalités pourraient être recalculés dynamiquement depuis le catalogue des tarifs ou la table de configuration des indices. Nous avons fait le choix délibéré de **dénormaliser et sceller** deux informations :

1. **`montant_paye` dans `reservation` (RG10)** :

   * **Ce qui est stocké :** Le montant effectif facturé au moment de la réservation.

   * **Pourquoi :** Même si le prix de location de la salle varie dans le temps (heures pleines, promotion, inflation), la transaction passée doit rester immuable sur le plan comptable et juridique.

   * **Gouvernance :** Aucun processus de mise à jour n'existe. La donnée est écrite une seule fois à la validation de la commande.

2. **`penalite_minutes` dans `indice_consomme` (RG8)** :

   * **Ce qui est stocké :** Le barème de pénalité appliqué lors de la distribution de l'indice.

   * **Pourquoi :** Si l'équipe pédagogique ou le maître du jeu réajuste plus tard la pénalité par défaut d'un indice (ex: passer de 3 à 5 minutes), le classement historique de la session ne doit pas être rétroactivement faussé.

   * **Gouvernance :** Donnée figée à l'insertion de la ligne.

## 4. Ce que le schéma SQL ne garantit pas (et où on le garantit)

Le schéma relationnel garantit l'intégrité référentielle et l'unicité des créneaux, mais il existe des contraintes métier complexes (cardinalités minimales, volumétries dynamiques) qu'un SGBD SQL standard ne peut pas contraindre par de simples clauses `NOT NULL` ou `CHECK` statiques.

| Contrainte métier non garantie par le DDL | Règle | Risque / Pourquoi le schéma SQL ne suffit pas | Où et comment on la garantit | 
| ----- | ----- | ----- | ----- | 
| **Taille minimale de l'équipe (au moins 2 joueurs)** | RG3 | En SQL, une clé étrangère `(id_equipe, id_joueur)` empêche les doublons mais ne peut pas exiger l'existence préalable d'au moins 2 lignes pour un `id_equipe`. | **Code applicatif + Transaction** : L'inscription d'une équipe exige dans le formulaire la saisie conjointe d'au moins 2 joueurs insérés dans la même transaction. Un **Trigger `AFTER COMMIT` / contrôle applicatif** bloque la validation si `COUNT(*) < 2`. | 
| **Plafond de 6 joueurs maximum par équipe** | RG3 | Une table de liaison n'impose pas de cardinalité maximale (`<= 6`) sans une vérification multi-lignes. | **Trigger PostgreSQL** (`BEFORE INSERT OR UPDATE` sur `composition_equipe`) qui compte le nombre de membres existants et déclenche une exception (`RAISE EXCEPTION`) si le quota de 6 joueurs est dépassé. | 
| **Plafond de 10 indices maximum par session** | RG7 | Une contrainte de table locale ne peut pas compter dynamiquement le nombre d'enregistrements rattachés à un parent. | **Trigger PostgreSQL** (`BEFORE INSERT` sur `indice_consomme`) vérifiant que `SELECT COUNT(*) FROM indice_consomme WHERE id_reservation = NEW.id_reservation` reste inférieur à 10. | 
| **Cohérence temporelle de la demande d'indice** | Métier | L'heure d'un indice consommé doit obligatoirement se situer entre l'heure de début de la session et la fin de l'heure de jeu. | **Trigger SQL ou vérification dans le code du service de chronométrage** lors de l'appel API du Game Master. | 
