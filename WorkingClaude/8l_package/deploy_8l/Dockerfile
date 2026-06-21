# 8L all-in-one image: bq CLI (from cloud-sdk) + python deps + app code.
FROM google/cloud-sdk:slim
RUN apt-get update && apt-get install -y --no-install-recommends cron python3-pip tzdata \
 && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Ho_Chi_Minh
WORKDIR /opt/8l
COPY deploy_8l/requirements.txt deploy_8l/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r deploy_8l/requirements.txt
COPY . /opt/8l
RUN chmod +x deploy_8l/*.sh
ENV WORKDIR_8L=/opt/8l BQ_BIN=bq DNA_PYEXE=python3 CLOUDSDK_PYTHON=python3 \
    GOOGLE_APPLICATION_CREDENTIALS=/opt/8l/sa-key.json
ENTRYPOINT ["/opt/8l/deploy_8l/docker-entrypoint.sh"]
CMD ["python3","telegram_8l_bot.py"]
