# Remove all .png files in the training folder
# and generate new ones from random tenor gifs
from os import listdir, remove
from gifpy import Gifpy
from os import getenv

tenor_token = getenv("GIF_TOKEN")
if not tenor_token:
    raise Exception("No gif token found")

gifpy = Gifpy(tenor_token, "en_US")

bad_gifs = [
    "https://media.discordapp.net/attachments/977197179477327903/1052649070587551824/Honeycam_.gif",
    "https://cdn.discordapp.com/attachments/1130985436228108331/1135273142705733783/20230730_191000.gif",
    "https://cdn.discordapp.com/attachments/1130985436228108331/1135273560265470042/20230730_191137.gif",
    "https://cdn.discordapp.com/attachments/1130985436228108331/1135272433729933402/ufyfyyfdhe.gif",
    # "https://cdn.discordapp.com/attachments/976210920911028264/1135275848077942784/image.png",
    "https://cdn.discordapp.com/attachments/1130985436228108331/1135331963725684766/20230730_191137.gif",
    "https://cdn.discordapp.com/attachments/1130985436228108331/1135288701774204969/invert.gif",
]
other_gifs = [
    "https://cdn.discordapp.com/attachments/1133898968665952337/1135306676736634910/VRChat_1920x1080_2021-03-13_00-26-51.314.png",
    "https://cdn.discordapp.com/attachments/1133898968665952337/1135306697024491520/VRChat_2023-07-30_22-17-54.369_7680x4320.png",
    "https://cdn.discordapp.com/attachments/1133898968665952337/1135308114246242344/VRChat_2023-07-30_22-26-33.150_4320x7680.jpg",
]


def get_gifs(query, limit=20):
    gifs = gifpy.search(query, limit=limit)
    for gif in gifs:
        other_gifs.append(gif.media.get_format("gif").url)


get_gifs("anime")
get_gifs("vrchat")
get_gifs("speech bubble")

# Download gifs to temp folder
import tempfile
import requests

other_temp_dir = tempfile.TemporaryDirectory()
for gif in other_gifs:
    r = requests.get(gif)
    with open(f"{other_temp_dir.name}/{gif.split('/')[-1]}", "wb") as f:
        f.write(r.content)

bad_temp_dir = tempfile.TemporaryDirectory()
for gif in bad_gifs:
    r = requests.get(gif)
    with open(f"{bad_temp_dir.name}/{gif.split('/')[-1]}", "wb") as f:
        f.write(r.content)

# Extract frames from gifs to training folder, with prefix
from sh import convert
from pathlib import Path

Path("other").mkdir(exist_ok=True)
Path("bad").mkdir(exist_ok=True)

for gif in listdir(other_temp_dir.name):
    convert(
        f"{other_temp_dir.name}/{gif}", "-resize", "256x256", f"other/{gif}-%02d.png"
    )

for gif in listdir(bad_temp_dir.name):
    convert(f"{bad_temp_dir.name}/{gif}", "-resize", "256x256", f"bad/{gif}-%02d.png")

# Remove temp folders
other_temp_dir.cleanup()
bad_temp_dir.cleanup()
