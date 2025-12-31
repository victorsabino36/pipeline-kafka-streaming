from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, ArrayType

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
    """Inicializa a sessão do Spark com suporte ao conector Kafka."""
    return SparkSession.builder \
        .appName("CryptoConsumerStreaming") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
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
    query = json_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .option("checkpointLocation", "/tmp/spark-checkpoints") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    run_streaming()