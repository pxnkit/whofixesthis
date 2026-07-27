import assert from "node:assert/strict"
import test from "node:test"

import {
  inferIssueDistribution,
  resolveIssue,
  sampleCases,
} from "../lib/routing.ts"

test("issue distribution is normalized", () => {
  const distribution = inferIssueDistribution("pothole in the road")
  const total = Object.values(distribution).reduce((sum, value) => sum + value, 0)
  assert.ok(Math.abs(total - 1) <= 0.02)
  assert.ok(distribution.road_surface > distribution.street_light)
})

test("event time activates permit delegation", () => {
  const decision = resolveIssue(sampleCases[2])
  assert.equal(decision.status, "resolved")
  assert.equal(decision.serviceCode, "HC-PERMIT-08")
})

test("expired permit produces an unresolved decision", () => {
  const decision = resolveIssue({
    ...sampleCases[2],
    observationDate: "2025-09-15",
  })
  assert.equal(decision.status, "unresolved")
})

test("unknown utility case abstains without an asset identifier", () => {
  const decision = resolveIssue(sampleCases[3])
  assert.equal(decision.status, "unresolved")
  assert.equal(decision.serviceCode, "UNRESOLVED")
})

test("broader location uncertainty cannot improve confidence", () => {
  const precise = resolveIssue(sampleCases[0])
  const broad = resolveIssue({
    ...sampleCases[0],
    uncertaintyMeters: 70,
  })
  assert.ok(broad.confidence <= precise.confidence)
})
