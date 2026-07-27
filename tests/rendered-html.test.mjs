import assert from "node:assert/strict"
import test from "node:test"

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url)
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`)
  const { default: worker } = await import(workerUrl.href)

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  )
}

test("server renders the complete research application", async () => {
  const response = await render()
  assert.equal(response.status, 200)
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i)

  const html = await response.text()
  assert.match(html, /<title>WhoFixesThis \| Temporal civic service routing<\/title>/i)
  assert.match(html, /Find the responsible service, with evidence/)
  assert.match(html, /Responsibility workbench/)
  assert.match(html, /FixRouteBench/)
  assert.match(html, /Local analysis only/)
  assert.match(html, /Fictional service fixtures/)
  assert.doesNotMatch(html, /codex-preview/)
  assert.doesNotMatch(html, /react-loading-skeleton/)
  assert.doesNotMatch(html, /Your site is taking shape/)
})

test("submission is not exposed in rendered product controls", async () => {
  const response = await render()
  const html = await response.text()
  assert.match(html, /No report is sent/)
  assert.doesNotMatch(html, />Submit report</i)
  assert.doesNotMatch(html, />Send report</i)
})
