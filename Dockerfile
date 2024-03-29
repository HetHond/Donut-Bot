FROM python:3.11

WORKDIR /usr/src/donut-bot

COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-u", "-m", "src", "--service-account"]
