from math import floor
import time
import discord
import tempfile
import requests
from sh import convert, ffmpeg
from tensorflow.keras.models import load_model
import tensorflow as tf
import numpy as np
import asyncio

model = load_model("./model.keras", compile=True)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


class PerformanceTimer:
    def __init__(self):
        self.start_time = time.time()
        self.time_since_last_marker = time.time()

    def marker(self, name):
        diff_in_ms = int(floor((time.time() - self.time_since_last_marker) * 1000))
        print(f"{name}: {diff_in_ms}ms")
        self.time_since_last_marker = time.time()

    def end(self, name):
        diff_in_ms = int(floor((time.time() - self.start_time) * 1000))
        print(f"{name}: {diff_in_ms}ms")


@client.event
async def on_ready():
    print(f"Logged in as {client.user} :3")


@client.event
async def on_message(message):
    pt = PerformanceTimer()
    # Get all images, videos and gifs from message
    media_urls = []
    for attachment in message.attachments:
        media_urls.append(attachment.url)
    for embed in message.embeds:
        embed_dict = embed.to_dict()

        if "video" in embed_dict:
            media_urls.append(embed.video.url)
        elif "image" in embed_dict:
            media_urls.append(embed.image.url)
        elif "thumbnail" in embed_dict:
            media_urls.append(embed.thumbnail.url)
        else:
            print(f"Unknown embed: {embed_dict}")

    print(media_urls)

    pt.marker("Got media urls")

    # Download media to temp folder
    temp_dir = tempfile.TemporaryDirectory()
    for media in media_urls:
        r = requests.get(media)
        with open(f"{temp_dir.name}/{media.split('/')[-1]}", "wb") as f:
            f.write(r.content)

    pt.marker("Downloaded media")

    # Extract frames from media to new array
    frames = []
    for media in os.listdir(temp_dir.name):
        new_temp_dir = tempfile.TemporaryDirectory()
        if media.endswith(".gif") or media.endswith(".mp4"):
            ffmpeg(
                "-i",
                f"{temp_dir.name}/{media}",
                "-vf",
                "scale=256:256",
                f"{new_temp_dir.name}/{media}-%02d.png",
            )
        else:
            convert(
                f"{temp_dir.name}/{media}",
                "-resize",
                "256x256",
                f"{new_temp_dir.name}/{media}-%02d.png",
            )
        for frame in os.listdir(new_temp_dir.name):
            frames.append(f"{new_temp_dir.name}/{frame}")

        pt.marker(f"Extracted frames from {media}")

    # Remove temp folder
    temp_dir.cleanup()

    pt.marker("Removed temp folder")

    # Figure out if media is good or bad
    for frame in frames:
        img = tf.keras.preprocessing.image.load_img(frame, target_size=(256, 256))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create batch axis

        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        print("Prediction: ", end="")
        print(score)
        prediction = "bad" if np.argmax(score) == 0 else "other"
        confidence = 100 * np.max(score)
        print(
            "This image most likely {}, confidence: {:.2f}%.".format(
                prediction, confidence
            )
        )

        pt.marker(f"Predicted {frame}")

        if prediction == "bad":
            if confidence < 80:
                await message.channel.send(
                    f"{message.author.mention} is involved with a potential cock rubbing. Confidence: {confidence:.2f}%."
                )
                pt.end(
                    "Bad prediction, but medium confidence: {:.2f}%".format(confidence)
                )
                return

            try:
                await message.delete()
            except discord.errors.NotFound:
                pass

            await message.channel.send(
                "{} posted the cock rubbing gif! Confidence: {:.2f}%.".format(
                    message.author.mention, confidence
                )
            )

            pt.end("Sent requests to discord")

            return

    pt.end("No bad predictions")


import os

TOKEN = os.getenv("TOKEN")
client.run(TOKEN)
