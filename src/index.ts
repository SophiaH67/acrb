import { Client, GatewayIntentBits } from "discord.js";
const client = new Client({
  intents: [
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
  ],
});

client.on("ready", () => {
  console.log(`Logged in as ${client.user?.tag}!`);
});

client.on("messageCreate", async (message) => {
  if (message.content.includes("Honeycam_.gif") || message.content.includes("Cockrubbing_.gif")) {
    await Promise.all([
      message.delete(),
      message.channel.send(
        `${message.author.username} posted the cock rubbing gif!`
      ),
    ]).catch((e) => {
      console.error("Nya :(", e);
    });
  }
});

client.login(process.env.TOKEN);
