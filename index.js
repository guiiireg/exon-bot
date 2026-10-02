const {
  Client,
  GatewayIntentBits,
  Events,
  Collection,
  MessageFlags,
} = require("discord.js");
const fs = require("node:fs");
const path = require("node:path");
require("dotenv").config();

const TOKEN = process.env.DISCORD_TOKEN;

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

client.once(Events.ClientReady, (readyClient) => {
  console.log(`Ready! Logged in as ${readyClient.user.tag}`);
});

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

client.on(Events.InteractionCreate, async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  const command = interaction.client.commands.get(interaction.commandName);

  if (!command) {
    console.error(`No command matching ${interaction.commandName} was found.`);
    return;
  }

  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(error);
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp({
        content: "There was an error while executing this command!",
        flags: MessageFlags.Ephemeral,
      });
    } else {
      await interaction.reply({
        content: "There was an error while executing this command!",
        flags: MessageFlags.Ephemeral,
      });
    }
  }
});

client.login(TOKEN);
