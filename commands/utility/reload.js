const { SlashCommandBuilder } = require("discord.js");
const fs = require("node:fs");
const path = require("node:path");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("reload")
    .setDescription("Reloads a command.")
    .addStringOption((option) =>
      option
        .setName("command")
        .setDescription("The command to reload.")
        .setRequired(true),
    ),
  /**
   * Clears module cache and re-imports a command without restarting the bot.
   *
   * @param {import("discord.js").ChatInputCommandInteraction} interaction - Command interaction.
   * @returns {Promise<void>}
   */
  async execute(interaction) {
    const command_name = interaction.options
      .getString("command", true)
      .toLowerCase();
    const command = interaction.client.commands.get(command_name);

    if (!command) {
      return interaction.reply(
        `There is no command with the name \`${command_name}\`!`,
      );
    }

    const commands_path = path.join(__dirname, "..");
    const command_folders = fs.readdirSync(commands_path);
    let command_file_path = null;

    for (const folder of command_folders) {
      const file_path = path.join(
        commands_path,
        folder,
        `${command.data.name}.js`,
      );
      if (fs.existsSync(file_path)) {
        command_file_path = file_path;
        break;
      }
    }

    if (!command_file_path) {
      return interaction.reply(
        `Could not find the file for command \`${command.data.name}\`!`,
      );
    }

    try {
      // Purge module from Node's require cache so subsequent require() loads fresh code
      delete require.cache[require.resolve(command_file_path)];
      const new_command = require(command_file_path);
      interaction.client.commands.set(new_command.data.name, new_command);
      await interaction.reply(
        `Command \`${new_command.data.name}\` was reloaded!`,
      );
    } catch (error) {
      console.error(error);
      await interaction.reply(
        `There was an error while reloading a command \`${command.data.name}\`:\n\`${error.message}\``,
      );
    }
  },
};
