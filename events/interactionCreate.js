const { Events, MessageFlags } = require("discord.js");

module.exports = {
  name: Events.InteractionCreate,
  /**
   * Routes incoming interactions to their command handlers and handles uncaught errors.
   *
   * @param {import("discord.js").BaseInteraction} interaction - Interaction received from Discord gateway.
   * @returns {Promise<void>}
   */
  async execute(interaction) {
    if (!interaction.isChatInputCommand()) return;

    const command = interaction.client.commands.get(interaction.commandName);

    if (!command) {
      console.error(
        `No command matching ${interaction.commandName} was found.`,
      );
      return;
    }

    try {
      await command.execute(interaction);
    } catch (error) {
      console.error(error);
      // Discord rejects reply() if already acknowledged or deferred. Use followUp() in that state.
      const reply_method =
        interaction.replied || interaction.deferred ? "followUp" : "reply";
      await interaction[reply_method]({
        content: "There was an error while executing this command!",
        flags: MessageFlags.Ephemeral,
      });
    }
  },
};
