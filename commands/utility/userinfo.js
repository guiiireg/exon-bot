const { SlashCommandBuilder } = require("discord.js");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("userinfo")
    .setDescription("Provides informations about the user."),

  async execute(interaction) {
    await interaction.reply(
      `Username: {interaction.user.username}\n`,
      `ID: ${interaction.user.id}`,
    );
  },
};
