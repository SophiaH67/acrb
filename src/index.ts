import { Client, GatewayIntentBits } from 'discord.js';
import { getImagesFromMessage } from './extractor';
import { isImagePartOfThatGif } from './comparer';

const client = new Client({
  intents: [
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
  ],
});

client.on('ready', () => {
  console.log(`Logged in as ${client.user?.tag}!`);
});

client.on('messageCreate', async (message) => {
  const images = await getImagesFromMessage(message);

  if (images.some(isImagePartOfThatGif)) {
    await Promise.all([
      message.delete(),
      message.channel.send(
        `${message.author.username} posted the cock rubbing gif!`,
      ),
    ]).catch((e) => {
      console.error('Nya :(', e);
    });
  }
});

client.login(process.env.TOKEN);
