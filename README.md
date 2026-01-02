![Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white)
![Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

# 1. Criar o Namespace novamente
kubectl create namespace kafka

# 2. Subir o Operador e o Cluster Kafka
kubectl apply -f k8s/kafka/operator.yaml
kubectl apply -f k8s/kafka/cluster.yaml

# 3. AGUARDAR o Kafka ficar pronto (isso leva uns 2-3 minutos)
# Verifique com: kubectl get pods -n kafka
# Só prossiga quando o pod do kafka estiver 'Running' e '1/1'