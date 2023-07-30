import { PNG } from 'pngjs';
import { readFileSync, readdirSync } from 'fs';
import pixelmatch from 'pixelmatch';
import { THAT_IMAGE_HEIGHT, THAT_IMAGE_WIDTH } from './consts';

const THOSE_IMAGES: PNG[] = [];

for (const file of readdirSync(__dirname + '/../frames')) {
  if (!file.endsWith('.png')) {
    continue;
  }

  const img = readFileSync(__dirname + '/../frames/' + file);
  const png = PNG.sync.read(img);
  THOSE_IMAGES.push(png);
}

export function isImagePartOfThatGif(image: PNG) {
  for (const thatImage of THOSE_IMAGES) {
    const diff = pixelmatch(
      image.data,
      thatImage.data,
      null,
      THAT_IMAGE_WIDTH,
      THAT_IMAGE_HEIGHT,
      { threshold: 0.2 },
    );

    console.log('diff', diff);

    const pixelsInThatImage = thatImage.width * thatImage.height;

    if (diff / pixelsInThatImage < 0.1) {
      return true;
    }

    return false;
  }

  return false;
}
