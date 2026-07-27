"use client"

import { useMemo, useState } from "react"
import { MapPanel } from "./MapPanel"
import {
  resolveIssue,
  sampleCases,
  type Resolution,
  type SampleCase,
} from "../../lib/routing"

const issueLabels = {
  road_surface: "Road surface",
  street_light: "Street light",
  sidewalk_obstruction: "Obstruction",
}

export function Workbench() {
  const [activeSample, setActiveSample] = useState<SampleCase>(sampleCases[0])
  const [description, setDescription] = useState(activeSample.description)
  const [locationId, setLocationId] = useState(activeSample.locationId)
  const [observationDate, setObservationDate] = useState(activeSample.observationDate)
  const [uncertaintyMeters, setUncertaintyMeters] = useState(
    activeSample.uncertaintyMeters,
  )
  const [assetId, setAssetId] = useState(activeSample.assetId)
  const [fileName, setFileName] = useState("")
  const [resolution, setResolution] = useState<Resolution | null>(null)
  const [approved, setApproved] = useState(false)
  const [exported, setExported] = useState(false)

  const coordinate = useMemo(
    () =>
      sampleCases.find((item) => item.locationId === locationId)?.coordinate ??
      activeSample.coordinate,
    [activeSample.coordinate, locationId],
  )

  const chooseSample = (sample: SampleCase) => {
    setActiveSample(sample)
    setDescription(sample.description)
    setLocationId(sample.locationId)
    setObservationDate(sample.observationDate)
    setUncertaintyMeters(sample.uncertaintyMeters)
    setAssetId(sample.assetId)
    setResolution(null)
    setApproved(false)
    setExported(false)
  }

  const runResolution = () => {
    setResolution(
      resolveIssue({
        description,
        locationId,
        observationDate,
        uncertaintyMeters,
        assetId,
      }),
    )
    setApproved(false)
    setExported(false)
  }

  const exportPreparedReport = () => {
    if (!approved || !resolution) return
    const payload = {
      status: "prepared_only",
      createdAt: new Date().toISOString(),
      observation: {
        description,
        locationId,
        coordinate,
        observationDate,
        uncertaintyMeters,
        assetId: assetId || null,
        media: fileName || null,
      },
      decision: resolution,
      submission: {
        attempted: false,
        reason: "Explicit government submission is outside this prototype",
      },
    }
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json",
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `whofixesthis-${activeSample.id}.json`
    link.click()
    URL.revokeObjectURL(url)
    setExported(true)
  }

  return (
    <section className="workbench-shell" id="workbench" aria-label="Routing workbench">
      <div className="workbench-bar">
        <div className="workbench-title">
          <span>Responsibility workbench</span>
          <span className="run-id">snapshot 2025.10</span>
        </div>
        <div className="sample-tabs" aria-label="Load a sample case">
          {sampleCases.map((sample) => (
            <button
              className={sample.id === activeSample.id ? "active" : ""}
              key={sample.id}
              onClick={() => chooseSample(sample)}
              type="button"
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      <div className="workbench-grid">
        <form
          className="issue-form"
          onSubmit={(event) => {
            event.preventDefault()
            runResolution()
          }}
        >
          <p className="panel-kicker">01 · Observation</p>

          <label className="field">
            <span>Issue photo</span>
            <span className="photo-drop">
              <input
                accept="image/*"
                aria-label="Choose an issue photo"
                onChange={(event) => setFileName(event.target.files?.[0]?.name ?? "")}
                type="file"
              />
              <strong>{fileName || "Choose a local image"}</strong>
              <small>Optional. File stays in this browser session</small>
            </span>
          </label>

          <label className="field">
            <span>Short description</span>
            <textarea
              maxLength={280}
              onChange={(event) => setDescription(event.target.value)}
              required
              value={description}
            />
          </label>

          <label className="field">
            <span>Map context</span>
            <select
              onChange={(event) => setLocationId(event.target.value)}
              value={locationId}
            >
              <option value="harbor-boundary">Harbor City and Route 17 boundary</option>
              <option value="northbank-transit">Northbank transit entrance</option>
              <option value="harbor-works">Harbor City active works area</option>
              <option value="northbank-utility">Northbank shared utility pole</option>
            </select>
          </label>

          <div className="location-row">
            <label className="field">
              <span>Observation date</span>
              <input
                onChange={(event) => setObservationDate(event.target.value)}
                required
                type="date"
                value={observationDate}
              />
            </label>
            <span className="accuracy-box">± {uncertaintyMeters} m</span>
          </div>

          <label className="field">
            <span className="range-line">
              <span>Location uncertainty</span>
              <small>Privacy adjustable</small>
            </span>
            <input
              aria-label="Location uncertainty in meters"
              max="80"
              min="5"
              onChange={(event) => setUncertaintyMeters(Number(event.target.value))}
              type="range"
              value={uncertaintyMeters}
            />
          </label>

          <label className="field">
            <span>Asset or permit identifier</span>
            <input
              onChange={(event) => setAssetId(event.target.value)}
              placeholder="Optional"
              type="text"
              value={assetId}
            />
          </label>

          <button className="primary-button" type="submit">
            Resolve responsibility
          </button>
          <p className="form-footnote">Runs locally against frozen fictional fixtures</p>
        </form>

        <div className="map-column">
          <MapPanel
            coordinate={coordinate}
            selectedProvider={resolution?.provider ?? ""}
            uncertaintyMeters={uncertaintyMeters}
          />
          <div className="hypothesis-strip">
            <h3>Competing hypotheses</h3>
            {(resolution?.hypotheses ?? [
              {
                provider: "Awaiting analysis",
                service: "Provider and service candidates",
                serviceCode: "—",
                score: 0,
              },
            ]).map((hypothesis, index) => (
              <div className="hypothesis" key={`${hypothesis.provider}-${index}`}>
                <span className="rank">{index + 1}</span>
                <span>
                  <strong>{hypothesis.provider}</strong>
                  <small>{hypothesis.service} · {hypothesis.serviceCode}</small>
                </span>
                <span className="score">
                  {resolution ? `${Math.round(hypothesis.score * 100)}%` : "pending"}
                </span>
              </div>
            ))}
          </div>
        </div>

        <aside className="decision-column" aria-live="polite">
          {!resolution ? (
            <div className="empty-decision">
              <div className="empty-glyph" aria-hidden="true">?</div>
              <h2>No decision yet</h2>
              <p>
                Review the observation and run the resolver to generate an auditable
                provider and service decision.
              </p>
            </div>
          ) : (
            <>
              <div className="decision-state">
                <div className="state-line">
                  <span
                    className={`state-badge ${
                      resolution.status === "unresolved" ? "unresolved" : ""
                    }`}
                  >
                    {resolution.status}
                  </span>
                  <span className="confidence">
                    calibrated {Math.round(resolution.confidence * 100)}%
                  </span>
                </div>
                <h2>{resolution.provider}</h2>
                <p className="service-code">
                  {resolution.service} · {resolution.serviceCode}
                </p>
              </div>

              <p className="mini-heading">Issue distribution</p>
              <div className="issue-bars">
                {Object.entries(resolution.issueDistribution).map(([key, value]) => (
                  <div className="issue-bar" key={key}>
                    <span>{issueLabels[key as keyof typeof issueLabels]}</span>
                    <span className="bar-track">
                      <span
                        className="bar-fill"
                        style={{ width: `${Math.round(value * 100)}%` }}
                      />
                    </span>
                    <span>{Math.round(value * 100)}%</span>
                  </div>
                ))}
              </div>

              <p className="mini-heading">Signed evidence</p>
              <div className="evidence-list">
                {resolution.evidence.map((evidence) => (
                  <div className="evidence-row" key={evidence.id}>
                    <span
                      className={`evidence-sign ${
                        evidence.direction === "contradicts" ? "against" : ""
                      }`}
                    >
                      {evidence.direction === "supports" ? "+" : "−"}
                    </span>
                    <span>
                      <strong>{evidence.title}</strong>
                      <small>{evidence.detail} · {evidence.observedAt}</small>
                    </span>
                  </div>
                ))}
              </div>

              <p className="mini-heading">Counterfactual</p>
              <div className="next-action">{resolution.counterfactual}</div>

              <p className="mini-heading">Duplicate search</p>
              {resolution.duplicate ? (
                <div className="duplicate-card">
                  <span>
                    <strong>{resolution.duplicate.caseId}</strong>
                    <small>
                      {resolution.duplicate.relation} · {resolution.duplicate.status}
                    </small>
                  </span>
                  <span className="duplicate-match">
                    {Math.round(resolution.duplicate.score * 100)}% match
                  </span>
                </div>
              ) : (
                <div className="duplicate-card">
                  <span>No sufficiently similar frozen case found</span>
                </div>
              )}

              <p className="mini-heading">Next action</p>
              <div className="next-action">{resolution.nextAction}</div>

              <p className="mini-heading">Prepared report</p>
              <div className="approval-box">
                <label>
                  <input
                    checked={approved}
                    onChange={(event) => setApproved(event.target.checked)}
                    type="checkbox"
                  />
                  <span>
                    I reviewed the fields and understand this exports a local file.
                    It does not contact a provider.
                  </span>
                </label>
                <button
                  className="secondary-button"
                  disabled={!approved}
                  onClick={exportPreparedReport}
                  type="button"
                >
                  {exported ? "Prepared report exported" : "Export prepared report"}
                </button>
              </div>
            </>
          )}
        </aside>
      </div>
    </section>
  )
}
