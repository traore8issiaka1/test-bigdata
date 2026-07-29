import re
from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import BooleanType

def unifier_manquants(df: DataFrame) -> DataFrame:
    """Remplace les valeurs '' et 'N/A' (insensible à la casse/espaces) par null,
    sur toutes les colonnes de type string."""
    string_cols = [c for c, t in df.dtypes if t == "string"]
    for c in string_cols:
        df = df.withColumn(
            c,
            F.when(
                F.trim(F.col(c)).isin("", "N/A", "n/a", "NA"),
                F.lit(None)
            ).otherwise(F.col(c))
        )
    return df

def normaliser_email(df: DataFrame) -> DataFrame:
    """Met l'email en minuscules/trim et ajoute une colonne booléenne
    email_valide (regex simple)."""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    df = df.withColumn("email", F.lower(F.trim(F.col("email"))))
    df = df.withColumn(
        "email_valide",
        F.col("email").isNotNull() & F.col("email").rlike(email_regex)
    )
    return df

def normaliser_ville(df: DataFrame) -> DataFrame:
    """trim + initcap sur 'ville' ; ajoute 'ville_norm' = clé sans accent
    (pour regrouper 'Thiès' et 'THIES')."""
    df = df.withColumn("ville", F.initcap(F.trim(F.col("ville"))))
    df = df.withColumn(
        "ville_norm",
        F.translate(
            F.lower(F.trim(F.col("ville"))),
            "àâäéèêëîïôöùûüç",
            "aaaeeeeiioouuuc"
        )
    )
    return df

def normaliser_telephone(df: DataFrame) -> DataFrame:
    """Nettoie le téléphone (retire +221, espaces, tirets) et ajoute
    telephone_valide (préfixe 70/75/76/77/78 + 9 chiffres)."""
    tel_clean = F.regexp_replace(F.col("telephone"), r"[\s\-\.]", "")
    tel_clean = F.regexp_replace(tel_clean, r"^\+221", "")
    tel_clean = F.regexp_replace(tel_clean, r"^00221", "")

    df = df.withColumn("telephone", tel_clean)
    df = df.withColumn(
        "telephone_valide",
        F.col("telephone").rlike(r"^(70|75|76|77|78)\d{7}$")
    )
    return df

def valider_naissance(df: DataFrame) -> DataFrame:
    """Ajoute naissance_valide : date_naissance doit être entre 1920-01-01
    et aujourd'hui. Ne supprime rien, juste un drapeau (on ne corrige pas
    avant d'avoir mesuré)."""
    df = df.withColumn(
        "naissance_valide",
        F.col("date_naissance").isNotNull()
        & (F.col("date_naissance") >= F.lit("1920-01-01"))
        & (F.col("date_naissance") <= F.current_date())
    )
    return df

def dedupliquer_clients(df: DataFrame) -> DataFrame:
    """Supprime les doublons exacts, puis les quasi-doublons sur
    (email, telephone) déjà normalisés."""
    df = df.dropDuplicates()  # doublons exacts sur toutes colonnes
    df = df.dropDuplicates(["email", "telephone"])  # quasi-doublons
    return df

def nettoyer_clients(df: DataFrame) -> DataFrame:
    """Pipeline complet de nettoyage, ordre imposé :
    normalisations d'abord, dédoublonnage en dernier."""
    return (
        df
        .transform(unifier_manquants)
        .transform(normaliser_email)
        .transform(normaliser_ville)
        .transform(normaliser_telephone)
        .transform(valider_naissance)
        .transform(dedupliquer_clients)
    )