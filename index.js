const { Client, GatewayIntentBits, Collection } = require("discord.js");
const fs = require("node:fs");
const path = require("node:path");

require("dotenv").config();

const TOKEN = process.env.DISCORD_TOKEN;

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.commands = new Collection();
const folders_path = path.join(__dirname, "commands");
const command_folders = fs.readdirSync(folders_path);

for (const folder of command_folders) {
  const commands_path = path.join(folders_path, folder);
  const command_files = fs
    .readdirSync(commands_path)
    .filter((file) => file.endsWith(".js"));
  for (const file of command_files) {
    const file_path = path.join(commands_path, file);
    const command = require(file_path);
    if ("data" in command && "execute" in command) {
      client.commands.set(command.data.name, command);
    } else {
      console.log(
        `[WARNING] The command at ${file_path} is missing a required "data" or "execute" property.`,
      );
    }
  }
}

const events_path = path.join(__dirname, "events");
const event_files = fs
  .readdirSync(events_path)
  .filter((file) => file.endsWith(".js"));

for (const file of event_files) {
  const file_path = path.join(events_path, file);
  const event = require(file_path);
  if (event.once) {
    client.once(event.name, (...args) => event.execute(...args));
  } else {
    client.on(event.name, (...args) => event.execute(...args));
  }
}

client.login(TOKEN);
