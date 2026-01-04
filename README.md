🚀 Crypto Streaming Pipeline: Kafka, Spark, AWS S3 & Databricks
📝 Objetivo
Este projeto implementa uma arquitetura de dados fim-a-fim para monitoramento de criptoativos em tempo real. O pipeline consome dados de uma API de mercado a cada 1 minuto, processa o fluxo via Kafka e distribui os dados para duas frentes:

Processamento Analítico: Persistência no Amazon S3 e transformações via Spark/Databricks (Arquitetura Medallion).

Monitoramento Real-time: Dashboard interativo em Streamlit para visualização imediata da oscilação de mercado.

🏗 Arquitetura e Tecnologias
Ingestion: Python Producer coletando dados de APIs e enviando para o Kafka (Orquestrado por Strimzi Operator no Kubernetes).

Real-Time: Streamlit consumindo tópicos para dashboards de baixa latência e indicadores de variação diária.

Storage & ETL: Apache Spark persistindo dados brutos no Amazon S3, seguidos por transformações em camadas (Bronze, Silver e Gold) no Databricks.

Intelligence: Camada Gold alimentando modelos de Machine Learning para predição de preços e tendências.

Infrastructure: Docker e Kubernetes (K8s) garantindo a containerização e resiliência dos serviços.

📂 Estrutura do Repositório
Plaintext

├── docs/               # Documentação e diagramas de arquitetura
├── k8s/                # Manifestos Kubernetes (YAML)
│   ├── kafka/          # Configurações do Cluster Kafka e Tópicos
│   ├── producer/       # Deployment do Producer no cluster
│   └── strimzi/        # Instalação do Strimzi Operator
├── src/                # Código fonte do projeto
│   ├── consumer/       # Consumers Spark e lógica de ingestão S3
│   ├── dashboard/      # Aplicação Streamlit
│   ├── databricks/     # Notebooks de transformação (Bronze -> Gold)
│   └── producer/       # Script Python de coleta da API
└── requirements.txt    # Dependências do projeto
--

# 🛠 Guia de Configuração (macOS)

1. Preparação do Ambiente Local
Ferramentas de Compilação: xcode-select --install

Docker Desktop: Instale a versão oficial e habilite o Kubernetes nas configurações.

Resources: Aloque no mínimo 4 CPUs e 8GB de RAM no Docker para suportar o cluster Kafka.

2. Configuração Cloud (AWS & Databricks)
AWS S3: Crie um bucket com as pastas raw/, bronze/, silver/ e gold/. Configure um usuário IAM com permissão AmazonS3FullAccess.

Databricks: Configure um cluster (Spark 3.5+) e adicione suas AWS_ACCESS_KEY e AWS_SECRET_KEY nas configurações de Spark para montagem do bucket.

3. Setup do Projeto
Bash

# Ativação do ambiente
cd pipeline-kafka-streaming
python3 -m venv venv
source venv/bin/activate

# Instalação de dependências
pip install -r requirements.txt
Crie um arquivo .env na raiz:

Snippet de código

AWS_ACCESS_KEY=SUA_CHAVE
AWS_SECRET_KEY=SEU_SECRET
DATABRICKS_TOKEN=SEU_TOKEN
4. Build e Deploy (Docker & K8s)
Bash

# Build das imagens locais
docker build -t crypto-producer:latest -f src/producer/Dockerfile .
docker build -t spark-crypto-consumer:latest -f src/consumer/Dockerfile .

# Instalação do Strimzi e Kafka
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f k8s/kafka/cluster.yaml -n kafka
🏃 Execução do Pipeline
Túneis de Conexão:

Bash

kubectl port-forward svc/crypto-cluster-kafka-external-bootstrap -n kafka 9094:9094 & 
kubectl port-forward svc/crypto-cluster-kafka-nodes-0 -n kafka 9095:9094
Dashboard:

Bash

streamlit run src/dashboard/dashboard.py
Processamento Databricks: Execute os notebooks em ordem (Bronze -> Silver -> Gold) para processar os dados históricos.