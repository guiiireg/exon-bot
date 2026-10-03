const test = require("node:test");
const assert = require("node:assert");
const { Collection, MessageFlags } = require("discord.js");
const interactionCreate = require("../events/interactionCreate.js");

test("handle_interaction_error replies with ephemeral message when not replied or deferred", async () => {
  let reply_payload = null;
  const mock_interaction = {
    replied: false,
    deferred: false,
    reply: async (payload) => {
      reply_payload = payload;
    },
    followUp: async () => {},
  };

  await interactionCreate.handle_interaction_error(
    mock_interaction,
    new Error("Test error"),
  );

  assert.deepStrictEqual(reply_payload, {
    content: "There was an error while executing this command!",
    flags: MessageFlags.Ephemeral,
  });
});

test("handle_interaction_error uses followUp when interaction is already replied or deferred", async () => {
  let follow_up_payload = null;
  const mock_interaction = {
    replied: true,
    deferred: false,
    reply: async () => {},
    followUp: async (payload) => {
      follow_up_payload = payload;
    },
  };

  await interactionCreate.handle_interaction_error(
    mock_interaction,
    new Error("Test error"),
  );

  assert.deepStrictEqual(follow_up_payload, {
    content: "There was an error while executing this command!",
    flags: MessageFlags.Ephemeral,
  });
});

test("interactionCreate event executes command and delegates error when command throws", async () => {
  let reply_payload = null;
  const mock_client = {
    commands: new Collection(),
  };
  mock_client.commands.set("failing_cmd", {
    execute: async () => {
      throw new Error("Command failed");
    },
  });

  const mock_interaction = {
    isChatInputCommand: () => true,
    commandName: "failing_cmd",
    client: mock_client,
    replied: false,
    deferred: false,
    reply: async (payload) => {
      reply_payload = payload;
    },
    followUp: async () => {},
  };

  await interactionCreate.execute(mock_interaction);

  assert.deepStrictEqual(reply_payload, {
    content: "There was an error while executing this command!",
    flags: MessageFlags.Ephemeral,
  });
});
