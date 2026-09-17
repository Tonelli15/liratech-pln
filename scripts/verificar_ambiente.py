"""Confere se o ambiente do motor de PLN do LiraTech está pronto."""

import sys

import fastapi
import pyphen
import spacy

print("Python:", sys.version.split()[0])
print("spaCy:", spacy.__version__, "| pyphen:", pyphen.__version__, "| FastAPI:", fastapi.__version__)

hifenizador = pyphen.Pyphen(lang="pt_BR", left=1, right=1)
print("pyphen separou 'amor' assim:", hifenizador.inserted("amor"))

nlp = spacy.load("pt_core_news_sm")
for token in nlp("Um verso de amor"):
    print(f"  {token.text} -> {token.pos_}")

print("Ambiente pronto!")