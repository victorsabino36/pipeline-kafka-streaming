# Imagem base compatível com Spark 3.5.x e Java
FROM apache/spark:3.5.0-python3

USER root

WORKDIR /app

# Instalando dependências de sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Configurando os pacotes EXATOS que você usa no Dataproc (Kafka + Delta)
# Adicionamos o conector do Kafka na mesma versão do Spark
ENV PYSPARK_SUBMIT_ARGS="--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262 pyspark-shell"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY spark_consumer.py .

CMD ["python3", "spark_consumer.py"]