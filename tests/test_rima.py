"""Testes da terminação sonora e da análise de rima (Seção 3.3.3 do TCC)."""

import pytest 

from motor_pln.rima import analisar_rima, terminacao_sonora


# --- Extração da terminação a partir da vogal tônica -----------------------

@pytest.mark.parametrize("palavra, terminacao", [
    ("amor", "or"),            # oxítona
    ("estrelas", "elas"),      # paroxítona
    ("lâmpada", "ampada"),     # proparoxítona
    ("palmeiras", "eiras"),    # ditongo decrescente na tônica
    ("história", "oria"),      # ditongo crescente depois da tônica
    ("cheguei", "ei"),         # o u de "gue" é mudo
    ("aqui", "i"),             # o u de "qui" é mudo
    ("entendê-las", "elas"),   # a tônica fica no verbo, não no pronome
    ("transforma-se", "ormase"),
])
def test_terminacao_sonora(palavra, terminacao):
    assert terminacao_sonora(palavra) == terminacao


# --- Normalização fonética -------------------------------------------------

@pytest.mark.parametrize("primeira, segunda", [
    ("voz", "após"),        # s e z neutralizam-se em final de palavra
    ("cruz", "conduz"),     # exemplo de rima rica do TCC (Seção 2.3)
    ("massa", "taça"),      # ss e ç representam o mesmo som
    ("passo", "braço"),
    ("mesa", "beleza"),     # s entre vogais soa como z
    ("caso", "prazo"),
    ("história", "glória"), # o acento marca tonicidade, não timbre distinto
    ("estrelas", "entendê-las"),
])
def test_palavras_que_rimam_tem_a_mesma_terminacao(primeira, segunda):
    assert terminacao_sonora(primeira) == terminacao_sonora(segunda)


@pytest.mark.parametrize("primeira, segunda", [
    ("casa", "caça"),       # /z/ entre vogais contra /s/ de ç
    ("rosa", "nossa"),
    ("água", "égua"),       # timbres distintos da vogal tônica
    ("estrela", "estrelas"),  # singular e plural não rimam
    ("pão", "pau"),         # o til marca nasalidade, que é distintiva
    ("amor", "amar"),
])
def test_palavras_que_nao_rimam_tem_terminacoes_diferentes(primeira, segunda):
    assert terminacao_sonora(primeira) != terminacao_sonora(segunda)


def test_palavra_sem_vogal_gera_erro():
    with pytest.raises(ValueError):
        terminacao_sonora("psst")


# --- Análise completa do verso --------------------------------------------

@pytest.mark.parametrize("verso, palavra, fonema, classe", [
    ("Minha terra tem palmeiras,", "palmeiras", "eiras", "substantivo"),
    ("Onde canta o Sabiá;", "Sabiá", "a", "substantivo"),
    ("Amor é fogo que arde sem se ver;", "ver", "er", "verbo"),
    ("Última flor do Lácio, inculta e bela,", "bela", "ela", "adjetivo"),
])
def test_analisar_rima(verso, palavra, fonema, classe):
    analise = analisar_rima(verso)
    assert analise.palavra_final == palavra
    assert analise.fonema_tonico == fonema
    assert analise.classe_gramatical == classe


def test_os_versos_rimados_do_soneto_recebem_a_mesma_terminacao():
    """Par de rima do soneto "Via Láctea XIII", de Olavo Bilac.

    A terminação só coincide porque o pronome enclítico de "entendê-las" é
    tratado como átono, deixando a tônica no verbo.
    """
    primeiro = analisar_rima('E eu vos direi: "Amai para entendê-las!"')
    segundo = analisar_rima("Capaz de ouvir e de entender estrelas.")
    assert primeiro.fonema_tonico == segundo.fonema_tonico == "elas"
    assert primeiro.classe_gramatical != segundo.classe_gramatical


def test_verso_sem_palavras_gera_erro():
    with pytest.raises(ValueError):
        analisar_rima("...!")