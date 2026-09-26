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
  cost?: number | string;
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

export default function Home() {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
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

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });

    const query = params.size ? `?${params.toString()}` : "";

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const [summaryResponse, salesResponse] = await Promise.all([
          fetch(`/backend/summary${query}`, { signal: controller.signal }),
          fetch(`/backend/sales${query}`, { signal: controller.signal }),
        ]);

        if (!summaryResponse.ok) throw new Error(`Summary request failed (${summaryResponse.status}).`);
        if (!salesResponse.ok) throw new Error(`Sales request failed (${salesResponse.status}).`);

        const [summaryData, salesData]: [Summary, unknown] = await Promise.all([
          summaryResponse.json(),
          salesResponse.json(),
        ]);

        setSummary(summaryData);
        setSales(getSales(salesData));
      } catch (loadError) {
        if (controller.signal.aborted) return;
        setError(loadError instanceof Error ? loadError.message : "Unable to load dashboard data.");
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    void loadDashboard();
    return () => controller.abort();
  }, [filters]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = question.trim();

    if (trimmedQuestion) {
      setSubmittedQuestion(trimmedQuestion);
      setQuestion("");
    }
  }

  function updateFilter(key: keyof Filters, value: string) {
    setFilters((current) => ({ ...current, [key]: value }));
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
        <span className={`status-pill ${error ? "status-error" : ""}`}>
          <span className="status-dot" /> {loading ? "Updating data" : error ? "API unavailable" : "Live data"}
        </span>
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

        {error && <p className="error-banner" role="alert">Could not load dashboard data: {error} Confirm the backend is running at 127.0.0.1:8000.</p>}

        <section className="kpi-grid" aria-label="Sales summary">
          {[
            { label: "Total Orders", value: formatNumber(summary.total_orders), suffix: "orders" },
            { label: "Total Revenue", value: formatMoney(summary.total_revenue), suffix: "USD" },
            { label: "Total Cost", value: formatMoney(summary.total_cost), suffix: "USD" },
            { label: "Total Margin", value: formatMoney(summary.total_margin), suffix: "USD" },
          ].map(({ label, value, suffix }, index) => (
            <article className="kpi-item" key={label}>
              <div className="kpi-label"><span className={`kpi-mark kpi-mark-${index + 1}`} />{label}</div>
              <strong aria-live="polite">{loading ? "Loading..." : error ? "-" : value}</strong>
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
            <span className="record-count">{loading ? "Loading records" : `${sales.length} records`}</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Order ID</th><th>Order Date</th><th>Country</th><th>Region</th><th>Product</th><th>Category</th><th>Revenue</th><th>Cost</th><th>Margin</th><th>Quarter</th></tr>
              </thead>
              <tbody>
                {sales.map((sale, index) => (
                  <tr key={`${sale.order_id ?? "order"}-${index}`}>
                    <td>{sale.order_id ?? "-"}</td><td>{sale.order_date ?? "-"}</td><td>{sale.country ?? "-"}</td><td>{sale.region ?? "-"}</td><td>{sale.product_name ?? "-"}</td><td>{sale.category ?? "-"}</td><td>{formatMoney(sale.revenue)}</td><td>{formatMoney(sale.cost)}</td><td>{formatMoney(sale.margin)}</td><td>{sale.quarter ?? "-"}</td>
                  </tr>
                ))}
                {!loading && sales.length === 0 && <tr><td className="table-empty" colSpan={10}>{error ? "Sales records are unavailable." : "No sales records match these filters."}</td></tr>}
              </tbody>
            </table>
          </div>
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
                  <strong>{sales.length ? formatMoney(revenue) : "-"}</strong>
                  <div className="quarter-track"><span style={{ height: maxQuarterRevenue ? `${Math.max((revenue / maxQuarterRevenue) * 100, revenue ? 2 : 0)}%` : "0%" }} /></div>
                  <span className="quarter-label">{quarter}</span>
                </div>
              ))}
            </div>
            {loading && <p className="chart-status">Refreshing chart data...</p>}
            {!loading && sales.length === 0 && <p className="chart-status">Quarter values will appear when sales records are available.</p>}
          </section>

          <section className="panel chat-panel">
            <div className="panel-heading">
              <div><p className="panel-kicker">Ask MetricMind</p><h2>Business question</h2></div>
              <span className="coming-soon">AI later</span>
            </div>
            <form className="question-form" onSubmit={handleSubmit}>
              <label htmlFor="business-question">What would you like to know?</label>
              <textarea id="business-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="e.g. Which quarter had the highest revenue?" rows={3} />
              <div className="form-footer">
                <span className="helper-text">AI integration will be connected later.</span>
                <button type="submit">Save question <span aria-hidden="true">-&gt;</span></button>
              </div>
            </form>
            <div className="chat-response" aria-live="polite">
              {submittedQuestion ? <><p className="question-echo">“{submittedQuestion}”</p><p className="response-message">AI integration will be connected later.</p></> : <p className="helper-text">Your question will be ready for future analysis.</p>}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
