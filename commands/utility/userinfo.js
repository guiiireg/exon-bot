const { SlashCommandBuilder } = require("discord.js");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("userinfo")
    .setDescription("Provides informations about the user."),

  /**
   * Responds with user details and guild-specific join date.
   *
   * @param {import("discord.js").ChatInputCommandInteraction} interaction - Command interaction.
   * @returns {Promise<void>}
   */
  async execute(interaction) {
    await interaction.reply(
      `Username: ${interaction.user.username}\nID: ${interaction.user.id}\nCreated: ${interaction.user.createdAt}\nJoined: ${interaction.member.joinedAt}`,
    );
  },
};
