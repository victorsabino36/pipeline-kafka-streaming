#!/bin/bash

# Carrega as variáveis do arquivo .env local
if [ -f .env ]; then
    export $(cat .env | xargs)
    echo " Credenciais carregadas"
else
    echo "❌ Erro: Arquivo .env não encontrado!"
    exit 1
fi

echo "🚀 Iniciando infraestrutura..."
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -

# Comentário: Cria o Secret usando as variáveis carregadas do .env
echo "🔑 Configurando acesso AWS no Kubernetes..."
kubectl create secret generic aws-credentials \
  --from-literal=AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  --from-literal=AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -n kafka --dry-run=client -o yaml | kubectl apply -f -

echo "⚙️ Aplicando Kafka e Aplicações..."
kubectl apply -f k8s/kafka/kafka-topic.yaml
kubectl apply -f k8s/kafka/kafka-cluster.yaml

echo "⏳ Aguardando estabilização..."
sleep 60

kubectl apply -f k8s/producer/deployment.yaml
kubectl apply -f k8s/consumer/deployment.yaml

echo "✅ Projeto rodando"