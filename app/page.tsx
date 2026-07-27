import { Workbench } from "./components/Workbench"

export default function Home() {
  return (
    <main>
      <header className="topbar">
        <a className="wordmark" href="#workbench" aria-label="WhoFixesThis home">
          <span className="wordmark-mark" aria-hidden="true">W</span>
          <span>WhoFixesThis</span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#workbench">Workbench</a>
          <a href="#benchmark">Benchmark</a>
          <a href="#methods">Methods</a>
          <a
            href="https://github.com/pxnkit/whofixesthis"
            rel="noreferrer"
            target="_blank"
          >
            Source
          </a>
        </nav>
        <span className="snapshot-pill">Frozen demo data</span>
      </header>

      <section className="intro" aria-labelledby="page-title">
        <div>
          <p className="eyebrow">Temporal civic service routing</p>
          <h1 id="page-title">Find the responsible service, with evidence</h1>
          <p className="intro-copy">
            A research prototype that separates issue recognition from the harder
            question of who was responsible at the time of observation.
          </p>
        </div>
        <aside className="safety-note" aria-label="Safety notice">
          <span className="safety-dot" aria-hidden="true" />
          <div>
            <strong>Local analysis only</strong>
            <p>No report is sent and no personal data leaves this page</p>
          </div>
        </aside>
      </section>

      <Workbench />

      <section className="research-section" id="benchmark">
        <div className="section-heading">
          <p className="eyebrow">FixRouteBench</p>
          <h2>Routing is evaluated as a joint decision</h2>
          <p>
            Fifty deterministic cases exercise provider selection, service codes,
            temporal changes, duplicate detection, open set cases, and abstention.
          </p>
        </div>
        <div className="metric-grid">
          <article>
            <span className="metric-value">50</span>
            <h3>Frozen episodes</h3>
            <p>Replayable with no live government or model API calls</p>
          </article>
          <article>
            <span className="metric-value">2 + 1</span>
            <h3>Jurisdictions</h3>
            <p>Two adjacent civic areas and one state level provider</p>
          </article>
          <article>
            <span className="metric-value">9</span>
            <h3>Hard case families</h3>
            <p>Boundaries, permits, utilities, transit, duplicates, and drift</p>
          </article>
          <article>
            <span className="metric-value">0</span>
            <h3>Silent submissions</h3>
            <p>Prepared reports require a separate explicit approval gate</p>
          </article>
        </div>
      </section>

      <section className="methods-section" id="methods">
        <div className="section-heading">
          <p className="eyebrow">Method</p>
          <h2>A decision trail that can be replayed</h2>
        </div>
        <div className="method-flow" role="list" aria-label="Routing method">
          {[
            ["01", "Observe", "Keep issue cues, location uncertainty, and event time separate"],
            ["02", "Propose", "Construct competing provider and service hypotheses"],
            ["03", "Seek", "Reveal dated ownership, permit, jurisdiction, and duplicate evidence"],
            ["04", "Decide", "Select only above the calibrated threshold, otherwise abstain"],
          ].map(([number, title, copy]) => (
            <article key={number} role="listitem">
              <span>{number}</span>
              <h3>{title}</h3>
              <p>{copy}</p>
            </article>
          ))}
        </div>
      </section>

      <footer>
        <p>Research prototype. Fictional service fixtures. Not government guidance.</p>
        <p>Built for auditable, privacy-aware civic routing research</p>
      </footer>
    </main>
  )
}
