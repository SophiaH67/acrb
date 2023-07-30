import { Message } from 'discord.js';
import { PNG } from 'pngjs';
import { spawn } from 'child_process';
import { mkdtemp, readFile, readdir, rm, writeFile } from 'fs/promises';
import { join } from 'path';
import { tmpdir } from 'os';
import sharp from 'sharp';
import { THAT_IMAGE_HEIGHT, THAT_IMAGE_WIDTH } from './consts';
function fetchToBuffer(url: string): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    fetch(url)
      .then((res) => res.arrayBuffer())
      .then((buf) => resolve(Buffer.from(buf)))
      .catch((e) => reject(e));
  });
}

async function bufferToPng(buf: Buffer): Promise<PNG> {
  const image = await sharp(buf)
    .resize(THAT_IMAGE_WIDTH, THAT_IMAGE_HEIGHT)
    .png()
    .toBuffer();

  return PNG.sync.read(image);
}

async function getImagesFromDirectory(dir: string): Promise<PNG[]> {
  const images = [];
  const files = await readdir(dir);

  for (const file of files) {
    const img = await readFile(`${dir}/${file}`);
    const png = await bufferToPng(img);
    images.push(png);
  }

  return images;
}

async function getFramesFromVideo(url: string): Promise<PNG[]> {
  const tmpDir = await mkdtemp(join(tmpdir(), 'acrb-'));
  const videoFile = `${tmpDir}/video.mp4`;
  await fetchToBuffer(url).then((buf) => writeFile(videoFile, buf));

  const command = ['ffmpeg', '-i', videoFile, `${tmpDir}/%d.png`];

  console.log('Running', command.join(' '));

  const ffmpeg = spawn(command.shift()!, command);

  // wait for ffmpeg to finish
  await new Promise((resolve, reject) => {
    ffmpeg.on('close', (code) => {
      if (code === 0) {
        resolve(null);
      } else {
        reject(code);
      }
    });
  });

  const images = await getImagesFromDirectory(tmpDir);

  rm(tmpDir, { recursive: true, force: true });

  return images;
}

export async function getImagesFromMessage(message: Message): Promise<PNG[]> {
  const images = [];

  const urls: string[] = [];

  message.attachments.forEach((attachment) => urls.push(attachment.url));
  message.embeds
    .map((embed) => {
      if (embed.video) {
        //@ts-expect-error - Discord.js typings are wrong
        return embed.video.proxy_url || embed.video.proxyURL;
      }

      if (embed.image) {
        //@ts-expect-error - Discord.js typings are wrong
        return embed.image.proxy_url || embed.image.proxyURL;
      }

      return embed.url;
    })
    .filter((url) => url)
    .forEach((url) => urls.push(url));

  for (const url of urls) {
    // If it's a video or gif, extract all frames
    if (url.endsWith('.mp4') || url.endsWith('.gif')) {
      const frames = await getFramesFromVideo(url);
      images.push(...frames);
    }

    // If it's an image, just add it
    else if (
      url.endsWith('.png') ||
      url.endsWith('.jpg') ||
      url.endsWith('.jpeg')
    ) {
      const img = await fetchToBuffer(url);
      const png = await bufferToPng(img);
      images.push(png);
    }
  }

  return images;
}
