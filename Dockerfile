FROM artemisfowl004/vid-compress
WORKDIR /app
COPY requirements.txt .
RUN apt-get update
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
CMD ["bash","start.sh"]

