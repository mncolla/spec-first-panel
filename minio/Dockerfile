FROM minio/minio:latest

# Railway injects PORT; the upstream image entrypoint does not expand it.
ENTRYPOINT ["sh", "-c", "exec minio server /data --address :$PORT"]
