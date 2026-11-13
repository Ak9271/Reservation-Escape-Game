DROP TABLE IF EXISTS avis CASCADE;
DROP TABLE IF EXISTS indice_consomme CASCADE;
DROP TABLE IF EXISTS reservation CASCADE;
DROP TABLE IF EXISTS indice CASCADE;
DROP TABLE IF EXISTS composition_equipe CASCADE;
DROP TABLE IF EXISTS equipe CASCADE;
DROP TABLE IF EXISTS joueur CASCADE;
DROP TABLE IF EXISTS enigme CASCADE;
DROP TABLE IF EXISTS salle CASCADE;

CREATE TABLE salle (
    id_salle INT GENERATED ALWAYS AS IDENTITY,
    code_salle VARCHAR(30) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    capacite_max INT NOT NULL,
    CONSTRAINT pk_salle PRIMARY KEY (id_salle),
    CONSTRAINT chk_capacite CHECK (capacite_max >= 2)
);

CREATE TABLE enigme (
    id_enigme INT GENERATED ALWAYS AS IDENTITY,
    titre VARCHAR(120) NOT NULL,
    difficulte INT NOT NULL,
    id_salle INT NOT NULL,
    CONSTRAINT pk_enigme PRIMARY KEY (id_enigme),
    CONSTRAINT fk_enigme_salle FOREIGN KEY (id_salle) REFERENCES salle(id_salle) ON DELETE CASCADE,
    CONSTRAINT chk_difficulte CHECK (difficulte BETWEEN 1 AND 5)
);

CREATE TABLE joueur (
    id_joueur INT GENERATED ALWAYS AS IDENTITY,
    email VARCHAR(255) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    telephone VARCHAR(30),
    CONSTRAINT pk_joueur PRIMARY KEY (id_joueur)
);

CREATE TABLE equipe (
    id_equipe INT GENERATED ALWAYS AS IDENTITY,
    nom_equipe VARCHAR(100) NOT NULL,
    CONSTRAINT pk_equipe PRIMARY KEY (id_equipe)
);

CREATE TABLE composition_equipe (
    id_equipe INT NOT NULL,
    id_joueur INT NOT NULL,
    date_adhesion DATE DEFAULT CURRENT_DATE,
    CONSTRAINT pk_composition_equipe PRIMARY KEY (id_equipe, id_joueur),
    CONSTRAINT fk_compo_equipe FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe) ON DELETE CASCADE,
    CONSTRAINT fk_compo_joueur FOREIGN KEY (id_joueur) REFERENCES joueur(id_joueur) ON DELETE RESTRICT
);

CREATE TABLE indice (
    id_indice INT GENERATED ALWAYS AS IDENTITY,
    code_indice VARCHAR(30) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    CONSTRAINT pk_indice PRIMARY KEY (id_indice)
);

CREATE TABLE reservation (
    id_reservation INT GENERATED ALWAYS AS IDENTITY,
    code_reservation VARCHAR(30) NOT NULL UNIQUE,
    date_heure_debut TIMESTAMP NOT NULL,
    statut VARCHAR(20) NOT NULL,
    montant_paye NUMERIC(8, 2) NOT NULL,
    id_salle INT NOT NULL,
    id_equipe INT NOT NULL,
    CONSTRAINT pk_reservation PRIMARY KEY (id_reservation),
    CONSTRAINT fk_res_salle FOREIGN KEY (id_salle) REFERENCES salle(id_salle) ON DELETE RESTRICT,
    CONSTRAINT fk_res_equipe FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe) ON DELETE RESTRICT,
    CONSTRAINT uk_salle_creneau UNIQUE (id_salle, date_heure_debut),
    CONSTRAINT chk_statut CHECK (statut IN ('EN_ATTENTE', 'CONFIRMEE', 'TERMINEE', 'ANNULEE')),
    CONSTRAINT chk_montant CHECK (montant_paye >= 0)
);

CREATE TABLE indice_consomme (
    id_reservation INT NOT NULL,
    id_indice INT NOT NULL,
    heure_demande TIME NOT NULL,
    penalite_minutes INT NOT NULL DEFAULT 3,
    CONSTRAINT pk_indice_consomme PRIMARY KEY (id_reservation, id_indice),
    CONSTRAINT fk_consomme_res FOREIGN KEY (id_reservation) REFERENCES reservation(id_reservation) ON DELETE CASCADE,
    CONSTRAINT fk_consomme_indice FOREIGN KEY (id_indice) REFERENCES indice(id_indice) ON DELETE RESTRICT
);

CREATE TABLE avis (
    id_avis INT GENERATED ALWAYS AS IDENTITY,
    id_reservation INT NOT NULL UNIQUE,
    note INT NOT NULL,
    commentaire TEXT,
    date_avis TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_avis PRIMARY KEY (id_avis),
    CONSTRAINT fk_avis_reservation FOREIGN KEY (id_reservation) REFERENCES reservation(id_reservation) ON DELETE CASCADE,
    CONSTRAINT chk_note CHECK (note BETWEEN 1 AND 5)
);

CREATE OR REPLACE FUNCTION verifier_taille_equipe()
RETURNS TRIGGER AS $$
DECLARE
    nb_joueurs INT;
BEGIN
    SELECT COUNT(*) INTO nb_joueurs
    FROM composition_equipe
    WHERE id_equipe = NEW.id_equipe;

    IF nb_joueurs >= 6 THEN
        RAISE EXCEPTION 'Une equipe ne peut pas contenir plus de 6 joueurs';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verifier_taille_equipe
BEFORE INSERT ON composition_equipe
FOR EACH ROW
EXECUTE FUNCTION verifier_taille_equipe();

CREATE OR REPLACE FUNCTION verifier_limite_indices()
RETURNS TRIGGER AS $$
DECLARE
    nb_indices INT;
BEGIN
    SELECT COUNT(*) INTO nb_indices
    FROM indice_consomme
    WHERE id_reservation = NEW.id_reservation;

    IF nb_indices >= 10 THEN
        RAISE EXCEPTION 'Une session ne peut pas consommer plus de 10 indices';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verifier_limite_indices
BEFORE INSERT ON indice_consomme
FOR EACH ROW
EXECUTE FUNCTION verifier_limite_indices();
