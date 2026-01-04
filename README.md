# 🚀 Crypto Streaming Pipeline: Kafka, Spark, AWS S3 & Databricks

## 📝 Objetivo
Este projeto implementa uma arquitetura de dados fim-a-fim para monitoramento de criptoativos em tempo real. O pipeline consome dados de uma API de mercado em intervalos de 1 minuto, processa o fluxo via Kafka e distribui os dados para duas frentes distintas:

- **Processamento Analítico**: Persistência no Amazon S3 e transformações distribuídas via Spark/Databricks seguindo a Arquitetura Medallion.
- **Monitoramento Real-time**: Dashboard interativo em Streamlit para visualização imediata da volatilidade do mercado.

## 🏗 Arquitetura e Tecnologias
- **Ingestion**: Producer em Python coletando dados de APIs e enviando para o Kafka (orquestrado pelo Strimzi Operator no Kubernetes).
- **Real-Time**: Streamlit para consumo de tópicos com baixa latência e indicadores de variação.
- **Storage & ETL**: Apache Spark para persistência no S3 e processamento em camadas (Bronze, Silver e Gold) no Databricks.
- **Infrastructure**: Docker e Kubernetes (K8s) garantindo portabilidade e resiliência.

## 📂 Estrutura do Repositório
```
├── docs/               # Documentação técnica e diagramas de arquitetura
├── k8s/                # Manifestos Kubernetes (Kafka, Producer, Strimzi)
│   ├── kafka/          # Configurações do Cluster Kafka e Tópicos
│   ├── producer/       # Deployment do Producer no cluster
│   └── strimzi/        # Instalação do Strimzi Operator
├── src/                # Código-fonte da aplicação
│   ├── consumer/       # Consumers Spark e lógica de escrita no S3
│   ├── dashboard/      # Aplicação Streamlit
│   ├── databricks/     # Notebooks de transformação (Bronze -> Gold)
│   └── producer/       # Script Python de coleta da API
└── requirements.txt    # Dependências do projeto
```

## 🛠️ Guia de Configuração (macOS)

### 1. Preparação do Ambiente Local
- **Ferramentas de Compilação**: Instale o Xcode Command Line Tools:
```bash
  xcode-select --install
```
- **Docker Desktop**: Instale a versão oficial e habilite o Kubernetes nas configurações.
- **Recursos**: Aloque no mínimo 4 CPUs e 4GB de RAM no Docker para suportar o cluster Kafka.

### 2. Configuração do Storage AWS
- No Amazon S3, crie um bucket com as pastas: `raw/`, `bronze/`, `silver/` e `gold/`.
- Configure um usuário IAM com a política `AmazonS3FullAccess` para as chaves de acesso.

### 3. Setup do Código e Dependências
```bash
# Navega até o diretório raiz e isola o ambiente Python
cd pipeline-kafka-streaming
python3 -m venv venv
source venv/bin/activate

# Instalação das bibliotecas necessárias
pip install -r requirements.txt
```

### 4. Configuração de Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```
AWS_ACCESS_KEY=SUA_CHAVE_AQUI
AWS_SECRET_KEY=SEU_SECRET_AQUI
DATABRICKS_TOKEN=SEU_TOKEN_AQUI
```

## 🐳 Build e Deploy (Docker & K8s)

### 1. Construção das Imagens
```bash
# Build das imagens locais para o Producer e Consumer Spark
docker build -t crypto-producer:latest -f src/producer/Dockerfile .
docker build -t spark-crypto-consumer:latest -f src/consumer/Dockerfile .
```

### 2. Provisionamento do Cluster Kafka
```bash
# Criação do namespace e instalação do Strimzi Operator
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f k8s/kafka/cluster.yaml -n kafka
```

## 🏃 Execução do Pipeline

### 1. Túneis de Conexão (Port-Forward)
Necessário para expor o broker Kafka rodando internamente no cluster para o host local:
```bash
kubectl port-forward svc/crypto-cluster-kafka-external-bootstrap -n kafka 9094:9094 & 
kubectl port-forward svc/crypto-cluster-kafka-nodes-0 -n kafka 9095:9094
```

### 2. Dashboard Streamlit
```bash
# Inicializa a visualização em tempo real
streamlit run src/dashboard/dashboard.py
```

## 📊 Camada Analítica (Databricks)
- **Cluster**: Configure um cluster (Spark 3.5+) e aponte a fonte de dados externa para o S3.
- **Notebooks**: Importe os scripts de `src/databricks/` e ajuste os caminhos para o bucket.
- **Fluxo**: Após a escrita no S3 iniciar, execute os notebooks na ordem:
```
  raw_to_bronze >> bronze_to_silver >> silver_to_gold >> ml_predictions
```
