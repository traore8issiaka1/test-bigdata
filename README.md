# TP1 — Big Data Engineering — Analyse des limites du traitement local

> Master 1 — DMI / FST / UCAD — Prof. Samba Ndiaye  
> Étudiant : Issiaka Traoré

Ce dépôt contient le travail réalisé dans le cadre du TP 1 sur l’environnement Python, la génération de données synthétiques, l’exploration avec Pandas et l’analyse des limites du traitement local.

## Objectif du projet

L’objectif de ce TP est de montrer que, au-delà d’un certain volume de données, un traitement local avec Pandas devient coûteux en mémoire, en temps et en stabilité. Le projet analyse notamment la charge de fichiers comme `orders.csv`, `orders+items` et `events.json` à différentes échelles.

## Contenu du dépôt

- [notebooks/TP1_exploration.ipynb](notebooks/TP1_exploration.ipynb) : notebook principal d’exploration et de mesures.
- [notebooks/TP1_exploration(Colab).ipynb](notebooks/TP1_exploration(Colab).ipynb) : version du notebook adaptée à Google Colab.
- [docs/DIAGNOSTIC.md](docs/DIAGNOSTIC.md) : rapport de diagnostic sur les limites du traitement local.
- [data/](data/) : données générées localement à partir du script fourni.
- [requirements.txt](requirements.txt) : dépendances Python nécessaires.
- [check_env.py](check_env.py) : vérification de l’environnement.

## Structure du dépôt

```text
.
├── README.md
├── check_env.py
├── requirements.txt
├── data/
├── docs/
│   └── DIAGNOSTIC.md
├── notebooks/
│   └── TP1_exploration.ipynb
└── src/
```

## Prérequis

- Python 3.9 ou plus
- Pip
- Un environnement virtuel Python

## Installation sur Windows (PowerShell)

```powershell
py -m venv venv-bigdata
.\venv-bigdata\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Génération des données

Les données sont générées de manière déterministe avec une graine fixe. Elles ne sont pas versionnées et peuvent être régénérées à tout moment.

```powershell
python .\data\generate_data.py --scale 0.1 --outdir .\data
```

## Utilisation

1. Vérifier l’environnement :
   ```powershell
   python .\check_env.py
   ```
2. Ouvrir le notebook :
   ```powershell
   jupyter notebook .\notebooks\TP1_exploration.ipynb
   ```
3. Consulter le rapport final :
   - [docs/DIAGNOSTIC.md](docs/DIAGNOSTIC.md)

## Livrables

- Notebook d’exploration complété
- Rapport de diagnostic final
- Analyse des limites mémoire, temps et scalabilité locale

## Notes

Le dossier [data/](data/) est exclu du versionnement et contient les jeux de données générés localement.
