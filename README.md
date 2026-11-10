# LiraTech: motor de PLN

Microsserviço em Python que realiza a escansão de versos em português e extrai os dados de rima usados pelo LiraTech. Faz parte do Trabalho de Conclusão de Curso de Tecnologia em Análise e Desenvolvimento de Sistemas do IFSul, Câmpus Camaquã.

## Requisitos

- Windows 10 ou 11
- Python 3.14, instalado pelo Python Install Manager

## Instalação

```powershell
py -V:3.14 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Verificação do ambiente

```powershell
python scripts\verificar_ambiente.py
```

## Executar o microsserviço

```powershell
fastapi dev servico\main.py
```

A documentação interativa fica em http://127.0.0.1:8000/docs.

## Reproduzir o ambiente exato

```powershell
python -m pip install -r requirements-lock.txt
```

O `requirements.txt` lista as dependências escolhidas; o `requirements-lock.txt`
registra as versões exatas de todas as bibliotecas instaladas.

## Avaliar o motor sobre o corpus anotado

```powershell
python -m pip install -r requirements-avaliacao.txt
python -m avaliacao --corpus corpus\corpus.csv --modelos sm md lg
```

Os resultados ficam na pasta `resultados`: as métricas em `metricas.json` e as
divergências em três arquivos CSV, com uma coluna `causa` para a análise manual.