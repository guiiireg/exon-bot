const test = require("node:test");
const assert = require("node:assert");
const { Collection, MessageFlags } = require("discord.js");
const reload = require("../commands/utility/reload.js");
const userinfo = require("../commands/utility/userinfo.js");

test("reload command rejects execution when invoking user is not the bot owner", async () => {
  let reply_options = null;
  const mock_client = {
    application: {
      owner: {
        id: "owner-123",
      },
    },
    commands: new Collection(),
  };

  const mock_interaction = {
    client: mock_client,
    user: {
      id: "unauthorized-user-456",
    },
    options: {
      getString: () => "userinfo",
    },
    reply: async (options) => {
      reply_options = options;
    },
  };

  await reload.execute(mock_interaction);

  assert.deepStrictEqual(reply_options, {
    content: "This command can only be used by the bot owner!",
    flags: MessageFlags.Ephemeral,
  });
});

test("reload command allows execution when invoking user is the bot owner", async () => {
  let reply_message = null;
  const mock_client = {
    application: {
      owner: {
        id: "owner-123",
      },
    },
    commands: new Collection(),
  };
  mock_client.commands.set(userinfo.data.name, userinfo);

  const mock_interaction = {
    client: mock_client,
    user: {
      id: "owner-123",
    },
    options: {
      getString: () => "userinfo",
    },
    reply: async (msg) => {
      reply_message = msg;
    },
  };

  await reload.execute(mock_interaction);

  assert.strictEqual(reply_message, "Command `userinfo` was reloaded!");
  assert.ok(mock_client.commands.has("userinfo"));
});
