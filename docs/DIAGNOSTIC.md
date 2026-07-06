# Diagnostic technique — Les limites du traitement local

> **Livrable de la séance 1** — Big Data Engineering — ISI
> Auteur : <Issiaka Traoré> — Date : <JJ/MM/AAAA>  
> Longueur attendue : 1 à 2 pages. Toute affirmation doit s'appuyer sur une  
> **mesure** issue de votre notebook ([notebooks/TP1_exploration.ipynb](../notebooks/TP1_exploration.ipynb)).

## Extrapolation

1. L'extrapolation linéaire est optimiste car elle suppose que les ressources (temps de calcul, mémoire) augmentent directement en fonction de la taille des données. Cela signifie que, lorsque les données grossissent, d'autres facteurs tels que la gestion de la mémoire peuvent faire augmenter les besoins en ressources de manière beaucoup plus drastique que la simple augmentation linéaire.
2. Pour traiter de plus grandes données sur une seule machine sans système distribué, on peut utiliser :

- Le chargement par morceaux (chunks), qui permet de lire et traiter les données par petites sections au lieu de tout charger en une fois, ce qui réduit la mémoire utilisée à un instant donné.
- Les dtypes optimisés, qui permettent de charger les colonnes avec des types plus économes, par exemple des chaînes de caractères en catégories ou des entiers plus petits, ce qui réduit considérablement l'empreinte mémoire d'un DataFrame.
- L'échantillonnage, qui permet de travailler uniquement avec un sous-ensemble représentatif des données, utile pour l'exploration rapide lorsque la précision totale n'est pas nécessaire.
- Les formats binaires (Parquet, Feather), qui sont plus compacts que CSV ou JSON et permettent un chargement plus rapide et plus efficace en mémoire.

Remarque : ces techniques peuvent repousser le mur de 5 à 10 fois, voire plus, selon les optimisations. Cependant, elles ne peuvent pas dépasser les limites physiques de la RAM et de la puissance de calcul d'une seule machine.

3. Le scale-out (passer à plusieurs machines ou à des systèmes distribués) devient inévitable lorsque :
- La RAM d'une seule machine est saturée : même avec les optimisations mentionnées, si la taille des données ou les exigences de traitement dépassent la mémoire disponible, le scale-out est la seule solution.
- Le temps de traitement est trop long : même avec une machine puissante et des optimisations, le calcul prend trop de temps pour répondre aux besoins, par exemple pour des analyses en temps réel ou des rapports quotidiens devant être prêts avant l'aube.
- La complexité des données ou des traitements augmente : certaines opérations, comme les jointures complexes sur de très grandes tables ou les algorithmes de Machine Learning gourmands, sont intrinsèquement plus efficaces et plus rapides sur des architectures distribuées.
- Le besoin de haute disponibilité et de tolérance aux pannes : une seule machine est un point de défaillance unique. Les systèmes distribués sont conçus pour continuer à fonctionner même si une partie du système tombe en panne.

Enfin le scale-out s'impose dès qu'une seule machine ne peut plus répondre efficacement et fiablement aux exigences de performance, de volume ou de complexité des données.

## Diagnostique

### a. constats

Le traitement local sur une machine comme Colab (RAM standard d'environ 12 Go) atteint ses limites de manière flagrante avec l'échelle 1.0 et certains types de fichiers :
- Mémoire pour events.json (échelle 1.0) : events.json à l'échelle 0.1 occupe 1346,5 Mo de RAM pour un fichier de 653,3 Mo sur disque (ratio mémoire/disque ~2,1:1). Par extrapolation linéaire, à l'échelle 1.0, events.json (fichier de 685 Mo sur disque) est estimé occuper environ 13,5 Go de RAM. Cette estimation dépasse la RAM standard d'une instance Colab, ce qui est confirmé par le crash mémoire ou l'avertissement sévère lors de la tentative de chargement, rendant son traitement intégral impossible sur une seule machine.
- Impact des jointures sur la mémoire : la jointure entre orders et order_items à l'échelle 0.1 a fait passer la consommation mémoire de 377 Mo (DataFrames séparés) à 538 Mo (DataFrame joint), augmentant le nombre de lignes à 1 129 775. Pour des échelles plus grandes, cette augmentation serait encore plus critique.
- Performance du chargement events.json : charger events.json à l'échelle 0.1 prend déjà 35,1 secondes. Par extrapolation linéaire, à l'échelle 1.0, cela prendrait environ 351 secondes (près de 6 minutes). Bien que techniquement possible si la mémoire le permettait, ce temps de chargement devient rapidement impraticable pour des analyses interactives ou des pipelines de données réguliers.
- Incohérence des types de données : la colonne montant_total_fcfa dans orders.csv est de type object et contient 5000 valeurs non numériques (par exemple « 7000 FCFA »). Cela empêche les calculs directs, comme la somme, et nécessite une étape de nettoyage coûteuse, limitant l'efficacité du traitement local pour des opérations numériques.

### b. Analyse

Les limites observées s'expliquent par plusieurs facteurs :
- Mémoire vs disque : Pandas charge les données en mémoire sous forme d'objets Python, ce qui est beaucoup moins compact que leur stockage sur disque (CSV, JSON). Par exemple, customers.csv pèse 5,7 Mo sur disque mais occupe 29,6 Mo en RAM. Les fichiers JSON, avec leur structure semi-ordonnée et leurs chaînes de caractères, sont particulièrement gourmands en mémoire une fois parsés en DataFrame, d'où le ratio élevé et l'explosion à l'échelle 1.0 (685 Mo sur disque deviennent environ 13,5 Go en RAM).
- Coût des jointures : les jointures comme celle entre orders et order_items créent de nouvelles lignes en dupliquant des informations. Si une commande a plusieurs articles, les informations de la commande sont répétées pour chaque article. Cela mène à une augmentation du nombre de lignes et, par conséquent, de l'empreinte mémoire du DataFrame résultant. C'est un facteur majeur de consommation de ressources lorsque les relations sont de type 1-à-plusieurs.
- Croissance des volumes et extrapolation linéaire : l'extrapolation linéaire est souvent optimiste. Elle suppose que les coûts (temps, mémoire) augmentent directement proportionnellement à la taille des données. En réalité, au-delà d'un certain seuil, d'autres facteurs comme la surcharge de la gestion mémoire, les accès disque non contigus et la complexité des algorithmes peuvent faire en sorte que les coûts augmentent de manière super-linéaire (plus vite que prévu). Charger des fichiers JSON de plus en plus grands est un exemple typique où la gestion de l'indexation et du parsing entraîne des coûts supplémentaires non pris en compte par une simple multiplication par 10.
- Types de données non optimisés : l'utilisation du dtype object pour des colonnes qui devraient être numériques (montant_total_fcfa) ou catégorielles (ville avec des variations de casse) empêche Pandas d'utiliser des structures de données plus efficaces en mémoire et plus rapides pour les calculs. Chaque chaîne de caractères est stockée séparément, augmentant la fragmentation et la consommation mémoire.

### c. Besoin

Pourquoi utiliser une architecture distribuée ?
Lorsque les données deviennent très volumineuses, une seule machine ne suffit plus. Une architecture distribuée permet de répartir le travail sur plusieurs ordinateurs afin de traiter les données plus rapidement et plus efficacement.
- Gérer de très grandes quantités de données : traiter des fichiers trop grands pour la mémoire d'un seul ordinateur, par exemple un fichier de 13,5 Go, 50 Go ou même 1 To.
- Améliorer les performances : réduire le temps nécessaire pour effectuer les calculs. Plusieurs machines travaillent en même temps (traitement parallèle), et si le volume de données augmente, il suffit d'ajouter de nouvelles machines au cluster. Cette méthode est appelée scalabilité horizontale (scale-out).
- Assurer la fiabilité : continuer le traitement même si une machine tombe en panne. Les données sont copiées sur plusieurs machines, et si une machine ne fonctionne plus, une autre reprend automatiquement son travail. Cela garantit une haute disponibilité et une meilleure résilience.

## 1. Constats — où le traitement local atteint-il ses limites ?

Observation principale : les fichiers `orders.csv`, `orders + items` et `events.json` restent traitables à l'échelle 0.1, mais l'échelle 1.0 montre très clairement la limite du traitement local. `orders.csv` se charge correctement et rapidement, la jointure `orders × items` reste possible, mais `events.json` devient problématique dès que le volume augmente. À l'échelle 1.0, le chargement est très lourd, avec saturation mémoire, avertissement de mémoire insuffisante et risque de crash du noyau.

Le tableau ci-dessous résume les observations principales.

| Opération                | Échelle |    Lignes | Temps (s) | Mémoire (Mo) | Observation         |
| ------------------------ | ------- | --------: | --------: | -----------: | ------------------- |
| Chargement `orders.csv`  | 0.1     |   50000.0 |      0.26 |         17.7 | Chargé correctement |
| Jointure orders × items  | 0.1     |  112750.0 |      0.06 |         53.7 | Chargé correctement |
| Chargement `events.json` | 0.1     |  329976.0 |      4.44 |        137.7 | Chargé correctement |
| Chargement `events.json` | 1.0     | 3301501.0 |     35.10 |       1346.5 | risque de crash     |

Points à couvrir :
- Le ratio mémoire / taille disque constaté, et son explication : le fichier `events.json` occupe environ 65 Mo sur disque, tandis que son chargement dans un DataFrame Pandas consomme environ 1,35 Go en mémoire à l'échelle 1.0, soit un ratio d'environ 20:1. Cette amplification s'explique par le fait que Pandas ne stocke pas seulement les valeurs brutes, mais aussi des objets Python, des index, des métadonnées de colonnes et des structures internes d'allocation qui sont beaucoup plus coûteuses qu'un simple fichier texte. En pratique, un DataFrame est donc beaucoup plus gourmand en RAM qu'un fichier JSON ou CSV stocké sur disque, lorsque les champs sont des chaînes, des objets imbriqués ou des types non optimisés.
- Ce qui s'est passé (précisément) lors du chargement de `events.json` à l'échelle 1.0 : le notebook a tenté de charger 3 301 501 lignes en une seule fois dans un DataFrame Pandas. La mémoire a monté jusqu'à environ 1,35 Go, soit bien au-delà de ce que l'environnement pouvait gérer proprement, ce qui a provoqué une forte saturation mémoire, puis un avertissement de mémoire insuffisante ou un arrêt de l'opération. En pratique, le chargement n'a pas été traité de façon progressive : tout le jeu de données a été chargé en mémoire d'un coup, ce qui a fait dépasser la capacité disponible.
- L'extrapolation à 50 Go puis 1 To (hypothèse linéaire — dites pourquoi elle est optimiste ou pessimiste) : si l'on applique une hypothèse linéaire à partir des mesures observées, un jeu de 50 Go nécessiterait environ 50 fois plus de mémoire qu'un jeu de 1 Go, soit autour de 67,5 Go de RAM, et 1 To demanderait environ 1 350 Go de RAM. Cette extrapolation est très optimiste, car elle suppose que la consommation mémoire reste proportionnelle à la taille du fichier, alors qu'en réalité, les coûts liés aux objets Python, aux index, aux copies temporaires et aux opérations de transformation augmentent souvent plus vite que linéairement. En pratique, la limite serait atteinte beaucoup plus tôt, surtout dès qu'il faut faire des jointures, des aggregations ou des opérations intermédiaires.

## 2. Analyse — pourquoi ça casse ?

- Pourquoi un DataFrame Pandas occupe plus de mémoire que le fichier source : parce qu'un fichier stocké sur disque est simplement enregistré sous forme de texte ou de données brutes, tandis qu'un DataFrame Pandas crée une structure complète en mémoire avec les colonnes, les index, les types de données et d'autres informations internes. Cela demande beaucoup plus de place que le fichier original. En plus, Pandas utilise des objets Python et des structures de stockage plus lourdes, ce qui augmente encore la consommation de RAM.
- Pourquoi la jointure aggrave le problème (pic mémoire, duplication) : parce que la jointure crée des correspondances entre plusieurs lignes des deux tables, ce qui peut produire beaucoup plus de lignes que dans les données initiales. Pendant cette opération, Pandas doit garder en mémoire les deux tables et parfois des structures temporaires supplémentaires pour faire les correspondances, ce qui provoque un pic de mémoire. En plus, si une ligne correspond à plusieurs lignes dans l'autre table, on obtient de la duplication, donc encore plus de données à traiter.
- En quoi le scale-up (acheter plus de RAM) n'est pas une stratégie durable : parce que cela coûte très cher, surtout si l'on doit acheter beaucoup de mémoire. Il existe aussi un plafond physique, car une machine ne peut pas contenir une quantité de RAM infinie. De plus, si la machine tombe en panne, tout le traitement est arrêté, ce qui est un vrai risque. Enfin, les données continuent de grossir, donc il faut sans cesse augmenter la capacité, et si plusieurs personnes ou traitements veulent accéder en même temps au système, la machine devient rapidement saturée.
- Quelles parades locales existent (chunks, dtypes optimisés, formats binaires, échantillonnage) et jusqu'où elles repoussent le mur : on peut d'abord utiliser des chunks pour lire les données par petits blocs au lieu de tout charger d'un coup. On peut aussi réduire la mémoire en choisissant des dtypes optimisés, par exemple en convertissant les colonnes texte en catégories ou en utilisant des types plus petits pour les nombres. Un autre moyen consiste à stocker les données dans des formats binaires comme Parquet ou Feather, qui sont plus compacts que CSV ou JSON. Enfin, on peut faire un échantillonnage pour tester rapidement des traitements sur une partie des données. Ces solutions repoussent le mur, mais seulement jusqu'à un certain point : elles permettent de traiter des volumes plus grands sans dépasser la RAM, mais elles ne résolvent pas complètement le problème quand les données deviennent vraiment très volumineuses.

Solutions possibles :
- Utiliser des chunksize pour charger `events.json` par blocs plutôt que d'un seul coup.
- Convertir les colonnes textuelles en catégories et réduire les types numériques pour économiser la mémoire.
- Stocker les données en Parquet ou Feather pour diminuer l'empreinte disque et accélérer le chargement.
- Passer à une architecture distribuée avec PySpark ou Dask lorsque les données dépassent la RAM d'une machine.
- Séparer le nettoyage et l'analyse en plusieurs étapes pour éviter les pics de mémoire.

## 3. Besoins — ce qu'une architecture distribuée doit apporter

Formulations de 4 à 6 exigences précises par rapport à la condition posée :

- Le système doit pouvoir traiter des volumes de données plus grands que la mémoire RAM d'une seule machine.
- Le système doit exécuter simultanément les calculs sur plusieurs machines.
- Le système doit tolérer la panne d'un nœud sans arrêter l'ensemble du traitement.
- Le système doit lire différents formats de données, tels que CSV et JSON.
- Le système doit rester pilotable depuis Python.
- Le système doit s'adapter à une croissance du volume sans nécessiter une réécriture complète du code.
Pandas reste néanmoins le bon outil pour l'exploration locale, la préparation des données et les analyses sur de petits à moyens volumes.

## 4. (Optionnel) Questions ouvertes

Ce que vous n'avez pas compris ou aimeriez approfondir — discuté en séance 2.
