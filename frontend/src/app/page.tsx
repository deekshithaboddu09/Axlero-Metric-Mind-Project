"use client";

import { FormEvent, useState } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = question.trim();

    if (trimmedQuestion) {
      setSubmittedQuestion(trimmedQuestion);
      setQuestion("");
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">M</div>
          <div>
            <p className="brand-name">MetricMind</p>
            <p className="brand-caption">Business intelligence, made clearer</p>
          </div>
        </div>
        <span className="status-pill"><span className="status-dot" /> Prototype workspace</span>
      </header>

      <main className="dashboard">
        <section className="intro-section">
          <div>
            <p className="eyebrow">Your analytics workspace</p>
            <h1>Ask better questions of your business.</h1>
            <p className="intro-copy">Start with a question in plain language. MetricMind will turn your curiosity into a clear path to insight.</p>
          </div>
          <div className="date-note">DAY 01<br /><strong>Foundation</strong></div>
        </section>

        <div className="workspace-grid">
          <section className="panel question-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">Explore your data</p>
                <h2>What would you like to know?</h2>
              </div>
              <span className="panel-number">01</span>
            </div>
            <form className="question-form" onSubmit={handleSubmit}>
              <label htmlFor="business-question">Business question</label>
              <textarea
                id="business-question"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="e.g. Which products drove the most revenue last quarter?"
                rows={5}
              />
              <div className="form-footer">
                <span className="helper-text">Try a question about revenue, customers, or trends.</span>
                <button type="submit">Ask MetricMind <span aria-hidden="true">-&gt;</span></button>
              </div>
            </form>
          </section>

          <section className="panel response-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">Your insight</p>
                <h2>Response</h2>
              </div>
              <span className="panel-number">02</span>
            </div>
            {submittedQuestion ? (
              <div className="response-content">
                <p className="question-echo">“{submittedQuestion}”</p>
                <p className="response-message">Your answer will appear here once your data connection is ready.</p>
                <span className="coming-soon">Analysis coming soon</span>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon" aria-hidden="true">+</div>
                <p>Your response will appear here.</p>
                <span>Ask a question to get started.</span>
              </div>
            )}
          </section>
        </div>

        <section className="panel chart-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Visual summary</p>
              <h2>Chart preview</h2>
            </div>
            <span className="panel-number">03</span>
          </div>
          <div className="chart-placeholder">
            <div className="chart-y-axis"><span>$40k</span><span>$30k</span><span>$20k</span><span>$10k</span><span>$0</span></div>
            <div className="chart-area">
              <div className="chart-gridlines"><span /><span /><span /><span /><span /></div>
              <div className="chart-bars" aria-label="Placeholder bar chart">
                <i style={{ height: "42%" }} /><i style={{ height: "68%" }} /><i style={{ height: "54%" }} /><i style={{ height: "82%" }} /><i style={{ height: "62%" }} /><i style={{ height: "92%" }} />
              </div>
              <div className="chart-x-axis"><span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span></div>
            </div>
            <p className="chart-note">A visualization will be generated from your response.</p>
          </div>
        </section>
      </main>
    </div>
  );
}
