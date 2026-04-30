// About view — what this project is, who built it, what it does and doesn't claim.

export default function About() {
  return (
    <div className="view view-about">
      <article className="about-article">
        <header className="about-header">
          <h1>About</h1>
          <p className="about-lede">
            Migration Atlas treats U.S. immigration as a relational structure
            rather than a list of statistics. Origin countries are nodes.
            Laws that enabled or restricted them are edges. Visa pathways
            are typed connections. Industries of settlement are downstream
            nodes. Four ML models sit on top of that graph.
          </p>
        </header>

        <section className="about-section">
          <h2>What you're looking at</h2>
          <p>
            Six views under one roof. <strong>Atlas</strong> renders the
            knowledge graph itself — click any node to see its
            relationships, or use the natural-language query bar to ask
            something specific. <strong>Forecast</strong> runs migration
            flow projections per origin country with explicit prediction
            intervals. <strong>Discourse, Simulate, Library,</strong> and{" "}
            <strong>Timeline</strong> are the rest of the platform —
            sentiment over time, counterfactual flow exploration, the
            literary corpus, and a synchronized history view.
          </p>
        </section>

        <section className="about-section">
          <h2>What it does claim</h2>
          <ul>
            <li>
              The graph captures association and known historical causation
              as documented in the cited literature.
            </li>
            <li>
              The forecaster produces calibrated point forecasts with
              prediction intervals on annual flow data.
            </li>
            <li>
              The retrieval-augmented research layer surfaces cited
              passages from the actual literature.
            </li>
          </ul>
        </section>

        <section className="about-section">
          <h2>What it does not claim</h2>
          <ul>
            <li>
              It does not estimate causal effects. Where you see
              cause-and-effect language, it traces back to a cited paper,
              not to a model output.
            </li>
            <li>
              It does not advocate a position. Where empirical questions
              are contested in the academic literature (the wage-effects
              debate is the canonical example), the system surfaces the
              contest rather than choosing.
            </li>
            <li>
              It does not predict beyond five years. Beyond that horizon,
              the prediction intervals widen to the point that any number
              is consistent with the data.
            </li>
          </ul>
        </section>

        <section className="about-section">
          <h2>Sources</h2>
          <p>
            U.S. Census ACS, USCIS Yearbook of Immigration Statistics,
            Migration Policy Institute, Pew Research, BLS, OECD DIOC,
            Voteview / DW-NOMINATE, the Comparative Manifesto Project,
            Library of Congress Chronicling America, and a curated
            research corpus (Borjas, Card, Peri, NAS 2017, Cato, Pew, MPI).
          </p>
          <p>
            Full source dictionary, harmonization decisions, and licensing
            notes live in the{" "}
            <a
              href="https://github.com/ujjawal40/migration-atlas/blob/main/data/README.md"
              target="_blank"
              rel="noreferrer"
            >
              data README
            </a>
            .
          </p>
        </section>

        <section className="about-section">
          <h2>How to read it</h2>
          <p>
            This is an academic case study, not a policy brief. The case
            study writeup — including a literature review, methodology,
            five country deep-dives, four worked example queries, and a
            limitations section — lives in the{" "}
            <a
              href="https://github.com/ujjawal40/migration-atlas/tree/main/docs/case-study"
              target="_blank"
              rel="noreferrer"
            >
              docs/case-study
            </a>{" "}
            tree.
          </p>
        </section>

        <footer className="about-footer">
          <p>
            Built as a portfolio project. Source on{" "}
            <a
              href="https://github.com/ujjawal40/migration-atlas"
              target="_blank"
              rel="noreferrer"
            >
              GitHub
            </a>
            . MIT licensed. Not affiliated with any government agency or
            research institution.
          </p>
        </footer>
      </article>
    </div>
  );
}
