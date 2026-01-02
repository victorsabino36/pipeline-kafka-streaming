from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, ArrayType
import os

# Definição do Schema para os dados da CoinGecko
# Garante a integridade dos dados durante o processamento
schema = ArrayType(StructType([
    StructField("id", StringType(), True),
    StructField("symbol", StringType(), True),
    StructField("name", StringType(), True),
    StructField("current_price", DoubleType(), True),
    StructField("last_updated", StringType(), True)
]))

def create_spark_session():
    """Inicializa a sessão do Spark focada em ingestão Raw para o S3."""
    
    # Comentário: Captura credenciais para autenticação no S3
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    return SparkSession.builder \
        .appName("Crypto-Landing-Raw") \
        .config("spark.hadoop.fs.s3a.access.key", aws_access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", aws_secret_key) \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()


def run_streaming():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    # Configuração da leitura do stream do Kafka
    # Usamos o endpoint interno do Kubernetes
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "crypto-cluster-kafka-bootstrap.kafka.svc:9092") \
        .option("subscribe", "monitor-cripto") \
        .option("startingOffsets", "earliest") \
        .load()

    # Conversão do valor binário do Kafka para JSON estruturado
    # O cast para String e posterior aplicação do Schema é fundamental
    json_df = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select(explode(col("data")).alias("crypto")) \
        .select("crypto.*")

    # Escrita do stream para o console (ou futuramente para um banco/datalake)
    # O checkpointLocation permite que o Spark retome de onde parou em caso de falha
    df_log = json_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .option("checkpointLocation", "/tmp/spark-checkpoints") \
        .start()

    raw_df = df.selectExpr("CAST(value AS STRING) as payload") \
    .withColumn("ingested_at", current_timestamp())

    query = raw_df.writeStream \
    .format("json") \
    .option("path", "s3a://aws-data-lakehouse/raw/kafka-crypto/") \
    .option("checkpointLocation", "s3a://aws-data-lakehouse/checkpoints/raw-crypto/") \
    .start()

    spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    run_streaming()