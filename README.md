# Big Data Engineering — Travaux Pratiques

> Master 1 — DMI / FST / UCAD / ISI — Prof. Samba Ndiaye  
> Étudiant : Issiaka Traoré

Ce dépôt contient les travaux réalisés dans le cadre du module Big Data Engineering, couvrant l'analyse des limites du traitement local, l'introduction à PySpark et le nettoyage de données à grande échelle.

## Objectifs des TPs

### TP 1 — Analyse des limites du traitement local
L’objectif est de montrer que, au-delà d’un certain volume de données, un traitement local avec Pandas devient coûteux en mémoire, en temps et en stabilité. Analyse des fichiers `orders.csv` et `events.json`.

### TP 2 — Premiers pas avec PySpark
Introduction à l'écosystème Spark :
- Mise en place de l'environnement Spark local.
- Implémentation d'un WordCount avec Spark SQL/DataFrames.
- Exploration des données du fil rouge avec Spark.
- Analyse des performances et utilisation de la Spark UI (Jobs, Stages, Shuffles).
- Comparaison des performances Spark vs Pandas.

### TP 3 — Nettoyage et tests (Module de transformations)
Industrialisation du traitement de données avec PySpark :
- Création d'un module de transformations robuste (`src/transformations.py`).
- Nettoyage des données clients (emails, téléphones, villes, dates de naissance).
- Diagnostic de qualité avant/après traitement.
- Mise en place de tests unitaires avec `pytest` et `chispa`.
- Gestion des doublons et normalisation.

### TP (Optionnel/Avancé) — PySpark et MySQL : Fédération de bases de données
Fédération de sources hétérogènes (`notebooks/TP_pyspark_mysql_OK.ipynb`) :
- Configuration de la connexion JDBC vers MySQL.
- Lecture et écriture de DataFrames PySpark dans des bases relationnelles.
- Jointure de données issues de bases différentes (`ecommerce_crm` et `ecommerce_ventes`) et de fichiers plats (CSV).
- Mise en place d'un audit d'intégrité référentielle inter-bases.

### TP 4 — Spark SQL : Requêtage e-commerce
Exploration approfondie des données avec Spark SQL :
- Chargement de sources multiples (CSV, JSON) et création de vues temporaires.
- Analyse de la pollution de données (cas du suffixe "FCFA").
- Calcul d'indicateurs métier (CA par région, par canal, évolution mensuelle).
- Optimisation et analyse de plans d'exécution avec `explain()`.

### TP 5 — Jointures, Audit et Entonnoir de conversion
Techniques avancées de manipulation de données :
- Jointures multi-tables contrôlées (Comptage avant/après).
- Audit référentiel pour identifier les données orphelines.
- Analyse comportementale : construction d'un entonnoir de conversion (Sessions -> Views -> Add to Cart -> Purchase).
- Calcul des taux de conversion étape par étape.

## Structure du dépôt

```text
.
├── README.md
├── check_env.py            # Script de vérification de l'environnement
├── requirements.txt        # Dépendances Python
├── init_tp3.sql            # Script d'initialisation SQL
├── data/                   # Données (exclues du versionnement)
│   └── generate_data.py    # Générateur de données synthétiques
├── docs/
│   ├── DIAGNOSTIC.md        # Rapport TP1
│   └── QUALITE.md           # Rapport TP3
├── notebooks/
│   ├── TP1_exploration.ipynb
│   ├── TP1_exploration(Colab).ipynb
│   ├── TP2_wordcount.ipynb
│   ├── TP3_Nettoyage.ipynb
│   ├── TP4_spark_sql.ipynb
│   ├── TP5_jointures.ipynb
│   └── TP_pyspark_mysql_OK.ipynb
├── src/
│   └── transformations.py   # Module de nettoyage (TP3)
└── tests/
    ├── conftest.py
    └── test_transformations.py
```

## Prérequis

- Python 3.9 ou plus
- **Java JDK 17** (requis pour Spark)
- Pip
- Un environnement virtuel Python

## Installation sur Windows (PowerShell)

```powershell
# Création et activation de l'environnement
py -m venv venv-bigdata
.\venv-bigdata\Scripts\Activate.ps1

# Installation des dépendances
pip install -r requirements.txt
```

## Utilisation

1. **Génération des données** :
   ```powershell
   python .\data\generate_data.py --scale 0.1 --outdir .\data
   ```

2. **Vérifier l’environnement** :
   ```powershell
   python .\check_env.py
   ```

3. **Lancement des notebooks** :
   ```powershell
   jupyter notebook
   ```

4. **Exécution des tests (TP3)** :
   ```powershell
   pytest
   ```

## Livrables principaux

- **TP1** : Notebooks d'exploration (Local et Colab) et rapport `DIAGNOSTIC.md`.
- **TP2** : Notebook WordCount avec analyse Spark UI.
- **TP3** : Module `transformations.py`, tests unitaires et rapport `QUALITE.md`.
- **TP4** : Notebook `TP4_spark_sql.ipynb` avec analyses SQL et indicateurs.
- **TP5** : Notebook `TP5_jointures.ipynb` avec audit et entonnoir de conversion.

## Notes

Le dossier [data/](data/) contient les jeux de données générés localement et n'est pas versionné.
