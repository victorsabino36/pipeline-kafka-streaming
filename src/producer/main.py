import time
import json
import requests
from kafka import KafkaProducer

# Configurações
API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=brl&ids=bitcoin,ethereum,solana"
# Ajustado para o nome real do seu cluster no K8s
KAFKA_BROKER = "crypto-cluster-kafka-bootstrap.kafka.svc:9092" 
TOPIC = "monitor-cripto"

# Inicializa o Producer
# value_serializer converte o dicionário Python para JSON em bytes automaticamente
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_and_send():
    """Busca dados da API e envia para o tópico do Kafka."""
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Envia para o Kafka
            producer.send(TOPIC, value=data)
            producer.flush() # Garante o envio
            print(f"[{time.strftime('%H:%M:%S')}] Dados enviados para o Kafka.")
        else:
            print(f"Erro na API: {response.status_code}")
    except Exception as e:
        print(f"Falha na execução: {e}")

if __name__ == "__main__":
    while True:
        fetch_and_send()
        time.sleep(70) # Intervalo de 2 minutos