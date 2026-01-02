#!/bin/bash

echo "🛑 Encerrando aplicações..."
# Caminhos conferidos pela sua imagem
kubectl delete -f k8s/producer/deployment.yaml --ignore-not-found
kubectl delete -f k8s/consumer/deployment.yaml --ignore-not-found

echo "☕ Encerrando infraestrutura Kafka..."
# Ajustado para os nomes reais dos seus arquivos: kafka-cluster e a pasta strimzi
kubectl delete -f k8s/kafka/kafka-cluster.yaml --ignore-not-found
kubectl delete -f k8s/strimzi/ --ignore-not-found

echo "🗑️ Removendo namespace..."
kubectl delete namespace kafka --ignore-not-found

echo "✅ Ambiente limpo com sucesso!"