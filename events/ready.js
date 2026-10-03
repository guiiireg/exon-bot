const { Events } = require("discord.js");

module.exports = {
  name: Events.ClientReady,
  once: true,
  /**
   * Invoked once when the client gateway connection is established and ready.
   *
   * @param {import("discord.js").Client<true>} client - Ready Discord client instance.
   */
  execute(client) {
    console.log(`Ready! Logged in as ${client.user.tag}`);
  },
};
