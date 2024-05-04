#FROM apache/airflow:2.9.0-python3.9
#COPY requirements.txt /requirements.txt
## RUN pip install --user --upgrade pip
## RUN pip install --no-cache-dir --user -r /requirements.txt # --no-cache-dir good practise when installing packages using pip. It helps to keep the image lightweight
#RUN pip install --no-cache-dir -r /requirements.txt


# Use an Apache Airflow with a specific Python version
FROM apache/airflow:2.9.0-python3.9

# Copy the Python requirements file
COPY requirements.txt /requirements.txt


# Install Python dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# Switch to root to install system packages
USER root

# Install Google Chrome
RUN apt-get update && apt-get install -y wget gnupg2 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Switch back to the default user 'airflow'
USER airflow
