FROM python:3.11-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg imagemagick
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
