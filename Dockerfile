FROM node:18
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg bash imagemagick
COPY package.json .
COPY yarn.lock .
COPY . .
RUN yarn
RUN yarn build
CMD ["yarn", "start"]
