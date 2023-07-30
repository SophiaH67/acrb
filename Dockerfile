FROM archlinux:latest
WORKDIR /app
RUN pacman -Syu ffmpeg imagemagick python
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
