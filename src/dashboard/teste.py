import json
import random
from kafka import KafkaConsumer

print("🚀 Iniciando teste de conexão...")

try:
    consumer = KafkaConsumer(
        'monitor-cripto',
        bootstrap_servers=['127.0.0.1:9094'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        # Comentário: Garante um grupo único para forçar a leitura do início
        group_id=f"debug-group-{random.randint(1, 1000)}",
        # Comentário: Removido api_version para permitir auto-detecção do broker 4.0
        consumer_timeout_ms=10000 
    )
    
    print("✅ Conectado ao Broker. Lendo tópico...")
    
    # Comentário: Itera diretamente no consumer para evitar problemas com o poll() vazio
    found = False
    for message in consumer:
        print(f"📦 Dado recebido: {message.value}")
        found = True
        break # Comentário: Sai após a primeira mensagem para validar
        
    if not found:
        print("x Timeout: Nenhuma mensagem disponível no momento.")

except Exception as e:
    print(f"❌ Erro na conexão: {e}")