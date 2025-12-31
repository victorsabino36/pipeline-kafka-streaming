# Imagem base compatível com Spark 3.5.x e Java
FROM apache/spark:3.5.0-python3

USER root

WORKDIR /app

# Instalando dependências de sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Configurando os pacotes EXATOS que você usa no Dataproc (Kafka + Delta)
# Adicionamos o conector do Kafka na mesma versão do Spark
ENV PYSPARK_SUBMIT_ARGS="--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.2.0 pyspark-shell"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY spark_consumer.py .

# Variável de ambiente para habilitar o Delta Lake no Spark
ENV SPARK_CONF="spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"

CMD ["python3", "spark_consumer.py"]