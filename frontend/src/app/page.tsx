"use client";

import { type FormEvent, useEffect, useState } from "react";

type Summary = {
  total_orders: number;
  total_revenue: number;
  total_cost: number;
  total_margin: number;
};

type Sale = {
  order_id?: string | number;
  order_date?: string;
  country?: string;
  region?: string;
  product_name?: string;
  category?: string;
  revenue?: number | string;
  total_cost?: number | string;
  margin?: number | string;
  quarter?: string;
};

type Filters = {
  region: string;
  country: string;
  product_name: string;
  category: string;
  quarter: string;
};
type ChatState = "idle" | "queued" | "loading" | "error";

const initialSummary: Summary = {
  total_orders: 0,
  total_revenue: 0,
  total_cost: 0,
  total_margin: 0,
};

const filterDefinitions: { key: keyof Filters; label: string; examples: string[] }[] = [
  { key: "region", label: "Region", examples: ["Europe"] },
  { key: "country", label: "Country", examples: ["Germany"] },
  { key: "product_name", label: "Product", examples: ["Analytics Suite"] },
  { key: "category", label: "Category", examples: ["Software"] },
  { key: "quarter", label: "Quarter", examples: ["Q1", "Q2", "Q3", "Q4"] },
];

function formatNumber(value: number | string | undefined) {
  const number = Number(value ?? 0);
  return Number.isFinite(number)
    ? new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(number)
    : "-";
}

function formatMoney(value: number | string | undefined) {
  const number = Number(value ?? 0);
  return Number.isFinite(number)
    ? new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(number)
    : "-";
}

function getSales(payload: unknown): Sale[] {
  if (Array.isArray(payload)) return payload as Sale[];
  if (payload && typeof payload === "object" && "sales" in payload && Array.isArray(payload.sales)) {
    return payload.sales as Sale[];
  }
  throw new Error("The sales API returned an unexpected response.");
}

function buildFilterQuery(filters: Filters) {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });

  return params.size ? `?${params.toString()}` : "";
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [chatState, setChatState] = useState<ChatState>("idle");
  const [chatError, setChatError] = useState("");
  const [summary, setSummary] = useState<Summary>(initialSummary);
  const [sales, setSales] = useState<Sale[]>([]);
  const [filters, setFilters] = useState<Filters>({
    region: "",
    country: "",
    product_name: "",
    category: "",
    quarter: "",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const initialLoading = loading && lastUpdated === null;
  const filterQuery = buildFilterQuery(filters);

  async function loadSummary(queryString = "", signal?: AbortSignal) {
    const response = await fetch(`/backend/summary${queryString}`, { signal });
    if (!response.ok) throw new Error(`Summary request failed (${response.status}).`);

    const data: Summary = await response.json();
    setSummary(data);
  }

  async function loadSales(queryString = "", signal?: AbortSignal) {
    const response = await fetch(`/backend/sales${queryString}`, { signal });
    if (!response.ok) throw new Error(`Sales request failed (${response.status}).`);

    const data: unknown = await response.json();
    setSales(getSales(data));
  }

  useEffect(() => {
    const controller = new AbortController();
    let timedOut = false;
    const timeoutId = window.setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, 12000);
    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        await Promise.all([
          loadSummary(filterQuery, controller.signal),
          loadSales(filterQuery, controller.signal),
        ]);
        setLastUpdated(new Date());
      } catch (loadError) {
        if (controller.signal.aborted && !timedOut) return;
        setError(timedOut
          ? "The data request timed out. Check the backend and database, then retry."
          : loadError instanceof Error ? loadError.message : "Unable to load dashboard data.");
      } finally {
        if (!controller.signal.aborted || timedOut) setLoading(false);
      }
    }

    void loadDashboard();
    return () => {
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, [filterQuery, reloadKey]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = question.trim();

    if (trimmedQuestion) {
      setSubmittedQuestion(trimmedQuestion);
      setChatError("");
      setChatState("queued");
      setQuestion("");
    }
  }

  function updateFilter(key: keyof Filters, value: string) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  function retryDashboard() {
    setReloadKey((current) => current + 1);
  }

  const quarterRevenue = ["Q1", "Q2", "Q3", "Q4"].map((quarter) => ({
    quarter,
    revenue: sales.reduce((total, sale) => {
      return sale.quarter?.toUpperCase() === quarter ? total + Number(sale.revenue ?? 0) : total;
    }, 0),
  }));
  const maxQuarterRevenue = Math.max(...quarterRevenue.map(({ revenue }) => revenue), 0);

  function optionsFor(key: keyof Filters, examples: string[]) {
    const valueByKey: Record<keyof Filters, keyof Sale> = {
      region: "region",
      country: "country",
      product_name: "product_name",
      category: "category",
      quarter: "quarter",
    };
    const values = sales
      .map((sale) => sale[valueByKey[key]])
      .filter((value): value is string => typeof value === "string" && value.length > 0);
    return [...new Set([...examples, ...values])].sort((left, right) => left.localeCompare(right));
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
        <div className="topbar-status">
          <span className={`status-pill ${error ? "status-error" : ""}`}>
            <span className="status-dot" /> {loading ? "Updating data" : error ? "API unavailable" : "Live data"}
          </span>
          <span className="last-updated">{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}` : "Not synced yet"}</span>
        </div>
      </header>

      <main className="dashboard">
        <section className="intro-section">
          <div>
            <p className="eyebrow">MetricMind / Overview</p>
            <h1>Know what moves your business.</h1>
            <p className="intro-copy">A clear view of orders, revenue, and sales performance.</p>
          </div>
          <div className="date-note">DATA SOURCE<br /><strong>Sales</strong></div>
        </section>

        <section className="filter-section" aria-label="Sales filters">
          <div className="filter-heading">
            <div>
              <p className="panel-kicker">Refine results</p>
              <h2>Filters</h2>
            </div>
            <button className="clear-button" type="button" onClick={() => setFilters({ region: "", country: "", product_name: "", category: "", quarter: "" })} disabled={!Object.values(filters).some(Boolean)}>Clear all</button>
          </div>
          <div className="filter-controls">
            {filterDefinitions.map(({ key, label, examples }) => (
              <label className="filter-control" htmlFor={`filter-${key}`} key={key}>
                <span>{label}</span>
                <select id={`filter-${key}`} value={filters[key]} onChange={(event) => updateFilter(key, event.target.value)}>
                  <option value="">All {key === "country" ? "countries" : key === "category" ? "categories" : `${label.toLowerCase()}s`}</option>
                  {optionsFor(key, examples).map((option) => <option key={option} value={option}>{option}</option>)}
                </select>
              </label>
            ))}
          </div>
        </section>

        <details className="api-inspector">
          <summary>View API calls</summary>
          <div className="api-inspector-content">
            <p>Dashboard requests use the selected filters through the frontend proxy. No credentials or secrets are displayed.</p>
            <div className="api-call-list">
              <div className="api-call">
                <span className="api-method">GET</span>
                <code>/backend/summary{filterQuery}</code>
              </div>
              <div className="api-call">
                <span className="api-method">GET</span>
                <code>/backend/sales{filterQuery}</code>
              </div>
            </div>
          </div>
        </details>

        {error && (
          <div className="error-banner" role="alert">
            <span>Could not load dashboard data: {error} Confirm the backend is running at 127.0.0.1:8000.</span>
            <button className="retry-button" type="button" onClick={retryDashboard} disabled={loading}>
              {loading ? "Retrying..." : "Retry"}
            </button>
          </div>
        )}

        <section className="kpi-grid" aria-label="Sales summary">
          {[
            { label: "Total Orders", value: formatNumber(summary.total_orders), suffix: "orders" },
            { label: "Total Revenue", value: formatMoney(summary.total_revenue), suffix: "USD" },
            { label: "Total Cost", value: formatMoney(summary.total_cost), suffix: "USD" },
            { label: "Total Margin", value: formatMoney(summary.total_margin), suffix: "USD" },
          ].map(({ label, value, suffix }, index) => (
            <article className={`kpi-item ${initialLoading ? "kpi-loading" : ""}`} key={label} aria-busy={loading}>
              <div className="kpi-label"><span className={`kpi-mark kpi-mark-${index + 1}`} />{label}</div>
              {initialLoading ? <span className="skeleton-value" aria-label="Loading value" /> : <strong aria-live="polite" title={error ? `Last loaded value; refresh failed: ${error}` : value}>{lastUpdated !== null || !error ? value : "Unavailable"}</strong>}
              <span className="kpi-suffix">{suffix}</span>
            </article>
          ))}
        </section>

        <section className="sales-section">
          <div className="section-heading">
            <div>
              <p className="panel-kicker">Transactions</p>
              <h2>Recent sales</h2>
            </div>
            <span className="record-count" aria-live="polite">{loading ? lastUpdated ? "Refreshing records..." : "Loading records..." : `${sales.length} records`}</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Order ID</th><th>Order Date</th><th>Country</th><th>Region</th><th>Product</th><th>Category</th><th>Revenue</th><th>Cost</th><th>Margin</th><th>Quarter</th></tr>
              </thead>
              <tbody>
                {sales.map((sale, index) => (
                  <tr key={`${sale.order_id ?? "order"}-${index}`}>
                    <td className="long-cell" title={String(sale.order_id ?? "-")}>{sale.order_id ?? "-"}</td>
                    <td>{sale.order_date ?? "-"}</td>
                    <td className="long-cell" title={sale.country ?? "-"}>{sale.country ?? "-"}</td>
                    <td className="long-cell" title={sale.region ?? "-"}>{sale.region ?? "-"}</td>
                    <td className="long-cell product-cell" title={sale.product_name ?? "-"}>{sale.product_name ?? "-"}</td>
                    <td className="long-cell" title={sale.category ?? "-"}>{sale.category ?? "-"}</td>
                    <td>{formatMoney(sale.revenue)}</td><td>{formatMoney(sale.total_cost)}</td><td>{formatMoney(sale.margin)}</td><td>{sale.quarter ?? "-"}</td>
                  </tr>
                ))}
                {initialLoading && Array.from({ length: 4 }, (_, index) => (
                  <tr className="skeleton-row" key={`loading-row-${index}`} aria-hidden="true">
                    {Array.from({ length: 10 }, (_, cellIndex) => <td key={cellIndex}><span /></td>)}
                  </tr>
                ))}
                {!loading && sales.length === 0 && (
                  <tr>
                    <td className="table-empty" colSpan={10}>
                      <strong>{error ? "Sales data is unavailable" : Object.values(filters).some(Boolean) ? "No sales match these filters" : "No sales records yet"}</strong>
                      <span>{error ? "Check the API connection and retry the dashboard." : Object.values(filters).some(Boolean) ? "Clear one or more filters to broaden the results." : "Records will appear here when the sales API returns data."}</span>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {loading && lastUpdated !== null && <p className="refresh-note" role="status">Updating filtered results. The last loaded data remains visible.</p>}
        </section>

        <div className="insight-grid">
          <section className="panel chart-panel">
            <div className="panel-heading">
              <div><p className="panel-kicker">Sales performance</p><h2>Revenue by quarter</h2></div>
              <span className="record-count">Based on loaded records</span>
            </div>
            <div className="quarter-chart" role="img" aria-label="Revenue by quarter from currently loaded sales records">
              {quarterRevenue.map(({ quarter, revenue }) => (
                <div className="quarter-column" key={quarter}>
                  <strong title={sales.length ? formatMoney(revenue) : "No loaded revenue"}>{sales.length ? formatMoney(revenue) : "-"}</strong>
                  <div className="quarter-track"><span style={{ height: maxQuarterRevenue ? `${Math.max((revenue / maxQuarterRevenue) * 100, revenue ? 2 : 0)}%` : "0%" }} /></div>
                  <span className="quarter-label">{quarter}</span>
                </div>
              ))}
            </div>
            {initialLoading && <p className="chart-status" role="status">Loading revenue data...</p>}
            {!initialLoading && loading && <p className="chart-status" role="status">Refreshing. Bars show the last loaded records until the request completes.</p>}
            {!loading && sales.length === 0 && <p className="chart-status">{error ? "Quarter totals are unavailable until sales data loads." : "No sales records are available for the current filters."}</p>}
          </section>

          <section className="panel chat-panel">
            <div className="panel-heading">
              <div><p className="panel-kicker">Ask MetricMind</p><h2>Business question</h2></div>
              <span className="coming-soon">AI connection pending</span>
            </div>
            <form className="question-form" onSubmit={handleSubmit}>
              <label htmlFor="business-question">What would you like to know?</label>
              <textarea id="business-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="e.g. Which quarter had the highest revenue?" rows={4} />
              <div className="prompt-list" aria-label="Starter questions">
                {["How are sales performing?", "Compare revenue by quarter"].map((prompt) => (
                  <button className="prompt-button" key={prompt} type="button" onClick={() => setQuestion(prompt)}>{prompt}</button>
                ))}
              </div>
              <div className="form-footer">
                <span className="helper-text">Saved locally only. No AI request is sent yet.</span>
                <button className="send-question" type="submit" disabled={!question.trim() || chatState === "loading"}>Send question <span aria-hidden="true">-&gt;</span></button>
              </div>
            </form>
            <section className={`chat-response chat-response-${chatState}`} aria-label="Response area" aria-live="polite">
              <p className="response-label">Response</p>
              {chatState === "loading" ? (
                <div className="chat-loading" role="status"><span className="chat-spinner" aria-hidden="true" /> Preparing your answer...</div>
              ) : chatState === "error" ? (
                <div className="chat-error" role="alert">
                  <strong>We couldn’t get a response.</strong>
                  <p>{chatError || "Check the connection and try again."} Your question is still available above.</p>
                </div>
              ) : submittedQuestion ? (
                <>
                  <p className="question-echo">“{submittedQuestion}”</p>
                  <dl className="structured-answer">
                    <div><dt>Answer</dt><dd>{chatState === "queued" ? "Waiting for the approved AI connection." : "A structured answer will appear here."}</dd></div>
                    <div><dt>Supporting data</dt><dd>Metrics and evidence will appear here when connected.</dd></div>
                    <div><dt>Applied filters</dt><dd>{Object.entries(filters).filter(([, value]) => value).map(([key, value]) => `${key}: ${value}`).join(" · ") || "None"}</dd></div>
                  </dl>
                  <p className="response-message">Saved locally only; no AI request was sent.</p>
                </>
              ) : (
                <p className="helper-text">Your structured answer, supporting data, and applied filters will appear here.</p>
              )}
            </section>
          </section>
        </div>
      </main>
    </div>
  );
}
