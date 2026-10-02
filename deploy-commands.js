const { REST, Routes } = require("discord.js");
const fs = require("node:fs");
const path = require("node:path");
require("dotenv").config();

const TOKEN = process.env.DISCORD_TOKEN;
const CLIENT = process.env.CLIENT_ID;
const GUILD = process.env.GUILD_ID;

const commands = [];
const folders_path = path.join(__dirname, "commands");
console.log(folders_path);
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
      commands.push(command.data.toJSON());
    } else {
      console.log(
        `[WARNING] The command at ${file_path} is missing a required "data" or "execute" property.`,
      );
    }
  }
}

const rest = new REST().setToken(TOKEN);

(async () => {
  try {
    console.log(
      `Started refreshing ${commands.length} application (/) commands.`,
    );
    const data = await rest.put(
      Routes.applicationGuildCommands(CLIENT, GUILD),
      { body: commands },
    );
    console.log(
      `Successfully reloaded ${data.length} application (/) commands.`,
    );
  } catch (error) {
    console.error(error);
  }
})();
