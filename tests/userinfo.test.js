const test = require("node:test");
const assert = require("node:assert");
const userinfo = require("../commands/utility/userinfo.js");

test("userinfo replies with user details and member join date when member exists", async () => {
  let reply_content = null;
  const mock_interaction = {
    user: {
      username: "testuser",
      id: "123456789",
    },
    member: {
      joinedAt: new Date("2026-01-01T00:00:00.000Z"),
    },
    reply: async (content) => {
      reply_content = content;
    },
  };

  await userinfo.execute(mock_interaction);

  assert.ok(reply_content.includes("Username: testuser"));
  assert.ok(reply_content.includes("ID: 123456789"));
  assert.ok(reply_content.includes("Joined:"));
  assert.ok(!reply_content.includes("Joined: N/A"));
});

test("userinfo handles missing member gracefully when run outside a guild", async () => {
  let reply_content = null;
  const mock_interaction = {
    user: {
      username: "testuser",
      id: "123456789",
    },
    member: null,
    reply: async (content) => {
      reply_content = content;
    },
  };

  await userinfo.execute(mock_interaction);

  assert.ok(reply_content.includes("Username: testuser"));
  assert.ok(reply_content.includes("ID: 123456789"));
  assert.ok(reply_content.includes("Joined: N/A"));
});
