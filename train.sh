#!/bin/bash
rm -f frames/*.png

wget https://media.discordapp.net/attachments/977197179477327903/1052649070587551824/Honeycam_.gif -O frames/source.gif
# Extract all frames from the source gif
convert frames/source.gif -resize 512x512 frames/frame%02d.png
# Clean up the source gif
rm frames/source.gif
