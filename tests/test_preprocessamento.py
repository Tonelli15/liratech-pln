"""Testes do pré-processamento (Figura 3a do TCC)."""

from motor_pln.preprocessamento import limpar_verso


def test_remove_pontuacao_e_converte_para_minusculas():
    assert limpar_verso("Ora (direis) ouvir estrelas! Certo") == "ora direis ouvir estrelas certo"


def test_mantem_o_hifen_dentro_da_palavra():
    assert limpar_verso("Transforma-se o amador") == "transforma-se o amador"


def test_remove_travessoes_e_hifens_soltos():
    assert limpar_verso("— Amor — -e-") == "amor e"


def test_junta_a_elisao_marcada_por_apostrofo():
    assert limpar_verso("Minh'alma é triste") == "minhalma é triste"


def test_normaliza_acentos_digitados_como_caractere_combinado():
    assert limpar_verso("Cafe\u0301") == "café"


def test_verso_sem_letras_vira_texto_vazio():
    assert limpar_verso("...!") == ""