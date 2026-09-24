# 🏎️ OpenF1 Data Explorer

Aplicação web interativa construída com **Streamlit** para explorar dados de corridas de Fórmula 1 armazenados em um banco **MongoDB**, populado a partir da API pública [OpenF1](https://openf1.org/).

O projeto foi desenvolvido como parte da **Prática 04 — Manipulação dos Dados em Banco MongoDB**.

---

## 📋 Sobre o projeto

O **OpenF1 Data Explorer** oferece uma interface gráfica que traduz interações do usuário (seleção de ano, corrida e pilotos) em consultas MongoDB em tempo real, exibindo os resultados em métricas, gráficos e tabelas — sem necessidade de escrever consultas diretamente no banco.

**Dentro do escopo:**
- Leitura e visualização de dados das coleções `sessions`, `drivers` e `laps`.
- Filtro de dados por ano e sessão de corrida.
- Comparação visual do desempenho (tempo de volta) de múltiplos pilotos.

**Fora do escopo:**
- Ingestão ou modificação de dados pela interface (responsabilidade do script `f1_data_collector.py`).
- Análise preditiva ou modelagem estatística avançada.
- Autenticação de usuários.

## 🗂️ Estrutura do projeto

```
Directory structure:
└── walterlimtrajano-openf1-data-explorer/
    ├── README.md
    ├── db_utils.py		# Conexão e consultas ao MongoDB (com fallback mockado)
    ├── f1_data_collector.py		# Script de coleta: busca dados na API OpenF1 e popula o MongoDB
    ├── Prática 04 - Manipulação dos Dados em Banco MongoDB Consultas MongoDB.docx
    ├── requirements.txt		# Dependências do projeto
    ├── streamlit_app.py		# Interface Streamlit (UI, filtros, gráficos)
    └── .env.example		# Exemplo de configuração do .env
```

## 🔧 Pré-requisitos

- Python 3.9+
- MongoDB rodando localmente (via Docker ou instalação nativa) ou um cluster no MongoDB Atlas

## 🚀 Como rodar

### 1. Criar e ativar um ambiente virtual

```bash
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar as variáveis de ambiente

Copie `.env.example` para `.env` e ajuste os valores conforme necessário:

```bash
cp .env.example .env
```

Variáveis usadas:

| Variável | Descrição | Padrão |
|---|---|---|
| `MONGO_URI` | String de conexão do MongoDB | `mongodb://localhost:27017` |
| `DB_NAME` | Nome do banco de dados | `openf1_data` |
| `API_BASE_URL` | URL base da API OpenF1 | `https://api.openf1.org/v1` |
| `SESSION_KEY` | Chave da sessão de corrida a coletar | `9159` (GP da Itália 2023) |
| `MEETING_KEY` | Chave do evento/fim de semana de corrida | `1219` (GP da Itália 2023) |

### 4. Subir o MongoDB local (se ainda não tiver um)

```bash
docker run -d -p 27017:27017 --name mongo-openf1 mongo
```

### 5. Popular o banco com dados reais

```bash
python f1_data_collector.py
```

Esse script busca os dados de `sessions`, `drivers` e `laps` da sessão configurada (`SESSION_KEY`) na API OpenF1 e salva no MongoDB, usando `upsert` para evitar duplicatas — pode ser executado quantas vezes forem necessárias.

### 6. Rodar a aplicação

```bash
streamlit run streamlit_app.py
```

Acesse `http://localhost:8501` no navegador. Selecione o ano e a corrida na barra lateral para explorar os dados.

> ℹ️ Caso o MongoDB esteja indisponível ou uma coleção não tenha dados para os filtros selecionados, a aplicação usa automaticamente **dados mockados** (fictícios) como fallback, permitindo testar a interface mesmo sem um banco populado.

## 📊 Coleções do MongoDB

| Coleção | Conteúdo | Chave única |
|---|---|---|
| `sessions` | Metadados da sessão de corrida (ano, país, circuito, data) | `session_key` |
| `drivers` | Pilotos participantes de cada sessão | `session_key` + `driver_number` |
| `laps` | Tempos de volta por piloto | `session_key` + `driver_number` + `lap_number` |

## 🧪 Estudo de caso

**GP da Itália de 2023** (Monza, `session_key=9159`): comparação de tempo de volta entre Charles Leclerc e Carlos Sainz Jr., permitindo validar a consistência dos dados ingeridos e identificar paradas nos boxes e degradação de pneus ao longo da corrida.

## 🛠️ Tecnologias

- [Streamlit](https://streamlit.io/) — interface web
- [PyMongo](https://pymongo.readthedocs.io/) — driver MongoDB
- [Pandas](https://pandas.pydata.org/) — manipulação de dados
- [Plotly](https://plotly.com/python/) — gráficos interativos
- [Requests](https://docs.python-requests.org/) — consumo da API OpenF1
- [python-dotenv](https://pypi.org/project/python-dotenv/) — variáveis de ambiente