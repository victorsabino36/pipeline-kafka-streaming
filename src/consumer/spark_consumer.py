from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, ArrayType
from pyspark.sql.streaming import StreamingQueryListener
import os

# Comentário: Schema técnico para estruturação dos dados brutos
schema = ArrayType(StructType([
    StructField("id", StringType(), True),
    StructField("symbol", StringType(), True),
    StructField("name", StringType(), True),
    StructField("current_price", DoubleType(), True),
    StructField("last_updated", StringType(), True)
]))

# Comentário: Monitoramento exclusivo de persistência no S3
class S3PersistenceLogger(StreamingQueryListener):
    def onQueryStarted(self, event):
        print(f"🟢 Ingestão S3 Iniciada: {event.id}")

    def onQueryProgress(self, event):
        if event.progress.numInputRows > 0:
            # Comentário: Captura duração total do batch no Spark 3.5
            duration = event.progress.durationMs.get("total", 0)
            print(f"✅ [S3 COMMIT] Batch: {event.progress.batchId} | Rows: {event.progress.numInputRows} | Duration: {duration}ms")

    def onQueryIdle(self, event):
        pass

    def onQueryTerminated(self, event):
        print(f"🔴 Ingestão S3 Finalizada: {event.id}")

def create_spark_session():
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    return SparkSession.builder \
        .appName("Crypto-Landing-S3") \
        .config("spark.driver.host", "localhost") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.hadoop.fs.s3a.access.key", aws_access_key) \
        .config("spark.hadoop.fs.s3a.secret.key", aws_secret_key) \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()

def run_streaming():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    spark.streams.addListener(S3PersistenceLogger())

    # Comentário: Ingestão de dados brutos do Kafka
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "crypto-cluster-kafka-bootstrap.kafka.svc:9092") \
        .option("subscribe", "monitor-cripto") \
        .option("startingOffsets", "earliest") \
        .load()

    # Comentário: Transformação e enriquecimento com metadados do Kafka
    structured_df = kafka_df.select(
        col("topic"),
        col("partition"),
        col("offset"),
        col("timestamp").alias("kafka_timestamp"),
        from_json(col("value").cast("string"), schema).alias("parsed_data"),
        current_timestamp().alias("ingested_at")
    )

    # Comentário: Aplanamento (flattening) dos dados para o S3
    final_df = structured_df.select(
        "*", explode(col("parsed_data")).alias("crypto")
    ).select(
        "topic", "partition", "offset", "kafka_timestamp", "ingested_at", "crypto.*"
    )

    # Comentário: Sink único para S3 com checkpoint persistente
    query_s3 = final_df.writeStream \
        .format("json") \
        .outputMode("append") \
        .option("path", "s3a://aws-data-lakehouse/raw/kafka-crypto/") \
        .option("checkpointLocation", "/tmp/spark-checkpoints") \
        .trigger(processingTime='30 seconds') \
        .start()

    query_s3.awaitTermination()

if __name__ == "__main__":
    run_streaming()