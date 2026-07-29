from chispa import assert_df_equality
from pyspark.sql import functions as F
from src.transformations import (
    unifier_manquants,
    normaliser_email,
    normaliser_ville,
    normaliser_telephone,
    valider_naissance,
    dedupliquer_clients,
)


def test_unifier_manquants(spark):
    entree = spark.createDataFrame(
        [("C1", "N/A"), ("C2", ""), ("C3", "amy@x.com")],
        ["customer_id", "email"],
    )
    res = unifier_manquants(entree)
    valeurs = [r["email"] for r in res.select("email").collect()]
    assert valeurs.count(None) == 2
    assert "amy@x.com" in valeurs


def test_normaliser_email(spark):
    entree = spark.createDataFrame(
        [("C1", "  AMY@X.COM "), ("C2", "pas-un-email")],
        ["customer_id", "email"],
    )
    res = normaliser_email(entree)
    rows = {r["email"]: r["email_valide"] for r in res.select("email", "email_valide").collect()}
    assert rows["amy@x.com"] is True
    assert rows["pas-un-email"] is False


def test_normaliser_ville(spark):
    entree = spark.createDataFrame(
        [("C1", " DAKAR "), ("C2", "thies"), ("C3", "Thiès")],
        ["customer_id", "ville"],
    )
    res = normaliser_ville(entree)
    normes = {r["ville_norm"] for r in res.select("ville_norm").collect()}
    # Thies et Thiès doivent donner la même clé normalisée
    assert normes == {"dakar", "thies"}


def test_normaliser_telephone(spark):
    entree = spark.createDataFrame(
        [("C1", "+221 77 123 45 67"), ("C2", "77-123-4567"), ("C3", "12345")],
        ["customer_id", "telephone"],
    )
    res = normaliser_telephone(entree)
    rows = {r["customer_id"]: r["telephone_valide"] for r in res.collect()}
    assert rows["C1"] is True
    assert rows["C2"] is True
    assert rows["C3"] is False


def test_valider_naissance(spark):
    entree = spark.createDataFrame(
        [("C1", "1990-05-01"), ("C2", "1850-01-01"), ("C3", None)],
        ["customer_id", "date_naissance"],
    ).withColumn("date_naissance", F.to_date("date_naissance"))
    res = valider_naissance(entree)
    rows = {r["customer_id"]: r["naissance_valide"] for r in res.collect()}
    assert rows["C1"] is True
    assert rows["C2"] is False
    assert rows["C3"] is False


def test_dedupliquer_clients(spark):
    entree = spark.createDataFrame(
        [
            ("C1", "amy@x.com", "771234567"),
            ("C2", "amy@x.com", "771234567"),  # quasi-doublon après normalisation
            ("C3", "bob@x.com", "781112222"),
        ],
        ["customer_id", "email", "telephone"],
    )
    res = dedupliquer_clients(entree)
    assert res.count() == 2