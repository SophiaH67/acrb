FROM node:18
WORKDIR /app
COPY package.json .
COPY yarn.lock .
COPY . .
RUN yarn build
CMD ["yarn", "start"]
