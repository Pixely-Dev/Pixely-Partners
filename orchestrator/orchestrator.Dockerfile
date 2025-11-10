### Dockerfile para el Orquestador de Pipelines
### Usamos una imagen de Python ligera
FROM python:3.11-slim
### 1. Instalamos cron
RUN apt-get update && apt-get -y install cron
### Establecemos el directorio de trabajo
WORKDIR /app
### Copiamos el archivo de dependencias principal
COPY requirements.txt .
### Instalamos las dependencias de Python desde el archivo principal
RUN pip install --no-cache-dir -r requirements.txt --timeout=120
### Copiamos los archivos de la aplicación
COPY run_pipelines.py . 
COPY pipelines/ pipelines/ 
COPY inputs/ inputs/ 
COPY pixely-cron .

### 2. Copiamos y configuramos el cron job
COPY pixely-cron /etc/cron.d/pixely-cron 
RUN chmod 0644 /etc/cron.d/pixely-cron && \
    crontab /etc/cron.d/pixely-cron && \
    touch /var/log/cron.log

### 3. El comando por defecto ahora inicia el servicio cron en primer plano
CMD ["cron", "-f"]
