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
type ChatState = "idle" | "loading" | "answered" | "error";

type QuestionAnswer = {
  question: string;
  answer: string;
};

type SavedQuestion = {
  id?: string | number;
  question: string;
  created_at: string;
};

const QUESTION_PAGE_SIZE = 10;

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

function getQuestionAnswer(payload: unknown): QuestionAnswer {
  if (
    payload &&
    typeof payload === "object" &&
    "question" in payload &&
    typeof payload.question === "string" &&
    "answer" in payload &&
    typeof payload.answer === "string"
  ) {
    return { question: payload.question, answer: payload.answer };
  }
  throw new Error("The question API returned an unexpected response.");
}

function getQuestionHistory(payload: unknown): { questions: SavedQuestion[]; total: number | null } {
  let records: unknown[];
  let total: number | null = null;

  if (Array.isArray(payload)) {
    records = payload;
  } else if (payload && typeof payload === "object" && "questions" in payload && Array.isArray(payload.questions)) {
    records = payload.questions;
    if ("total" in payload && typeof payload.total === "number") total = payload.total;
  } else {
    throw new Error("The question history API returned an unexpected response.");
  }

  const questions = records.map((record): SavedQuestion => {
    if (
      !record ||
      typeof record !== "object" ||
      !("question" in record) ||
      typeof record.question !== "string" ||
      !("created_at" in record) ||
      typeof record.created_at !== "string"
    ) {
      throw new Error("A saved question was missing its question or creation time.");
    }

    return {
      id: "id" in record && (typeof record.id === "string" || typeof record.id === "number") ? record.id : undefined,
      question: record.question,
      created_at: record.created_at,
    };
  });

  return { questions, total };
}

function formatQuestionTimestamp(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat("en-US", { dateStyle: "medium", timeStyle: "short" }).format(date);
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
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatState, setChatState] = useState<ChatState>("idle");
  const [chatError, setChatError] = useState("");
  const [savedQuestions, setSavedQuestions] = useState<SavedQuestion[]>([]);
  const [questionSearch, setQuestionSearch] = useState("");
  const [appliedQuestionSearch, setAppliedQuestionSearch] = useState("");
  const [questionOffset, setQuestionOffset] = useState(0);
  const [questionTotal, setQuestionTotal] = useState<number | null>(null);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyError, setHistoryError] = useState("");
  const [historyReloadKey, setHistoryReloadKey] = useState(0);
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

  useEffect(() => {
    const controller = new AbortController();

    async function loadQuestionHistory() {
      setHistoryLoading(true);
      setHistoryError("");
      const params = new URLSearchParams({
        limit: String(QUESTION_PAGE_SIZE),
        offset: String(questionOffset),
      });
      if (appliedQuestionSearch) params.set("search", appliedQuestionSearch);

      try {
        const response = await fetch(`/backend/questions?${params.toString()}`, { signal: controller.signal });
        if (!response.ok) throw new Error(`Question history request failed (${response.status}).`);

        const result = getQuestionHistory(await response.json());
        setSavedQuestions(result.questions.sort((left, right) => Date.parse(right.created_at) - Date.parse(left.created_at)));
        setQuestionTotal(result.total);
      } catch (loadError) {
        if (controller.signal.aborted) return;
        setHistoryError(loadError instanceof TypeError
          ? "Could not reach the MetricMind API. Check that the backend is running and try again."
          : loadError instanceof Error ? loadError.message : "Unable to load question history.");
        setSavedQuestions([]);
        setQuestionTotal(null);
      } finally {
        if (!controller.signal.aborted) setHistoryLoading(false);
      }
    }

    void loadQuestionHistory();
    return () => controller.abort();
  }, [appliedQuestionSearch, questionOffset, historyReloadKey]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || chatState === "loading") return;

    setSubmittedQuestion(trimmedQuestion);
    setChatAnswer("");
    setChatError("");
    setChatState("loading");

    try {
      const response = await fetch("/backend/questions/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmedQuestion }),
      });
      const payload: unknown = await response.json().catch(() => null);

      if (!response.ok) {
        let message = `Question request failed (${response.status}).`;
        if (payload && typeof payload === "object") {
          if ("detail" in payload && typeof payload.detail === "string") message = payload.detail;
          else if ("message" in payload && typeof payload.message === "string") message = payload.message;
        }
        throw new Error(message);
      }

      const result = getQuestionAnswer(payload);
      setSubmittedQuestion(result.question);
      setChatAnswer(result.answer);
      setQuestion("");
      setChatState("answered");
      setQuestionOffset(0);
      setHistoryReloadKey((current) => current + 1);
    } catch (requestError) {
      setChatError(requestError instanceof TypeError
        ? "Could not reach the MetricMind API. Check that the backend is running and try again."
        : requestError instanceof Error ? requestError.message : "Unable to get an answer. Please try again.");
      setChatState("error");
    }
  }

  function updateFilter(key: keyof Filters, value: string) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  function retryDashboard() {
    setReloadKey((current) => current + 1);
  }

  function handleQuestionSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setQuestionOffset(0);
    setAppliedQuestionSearch(questionSearch.trim());
  }

  function clearQuestionSearch() {
    setQuestionSearch("");
    setAppliedQuestionSearch("");
    setQuestionOffset(0);
  }

  const hasMoreQuestions = questionTotal !== null
    ? questionOffset + QUESTION_PAGE_SIZE < questionTotal
    : savedQuestions.length === QUESTION_PAGE_SIZE;

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
              <span className="coming-soon">Backend API</span>
            </div>
            <form className="question-form" onSubmit={handleSubmit}>
              <label htmlFor="business-question">What would you like to know?</label>
              <textarea id="business-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="e.g. Which quarter had the highest revenue?" rows={4} disabled={chatState === "loading"} />
              <div className="prompt-list" aria-label="Starter questions">
                {["How are sales performing?", "Compare revenue by quarter"].map((prompt) => (
                  <button className="prompt-button" key={prompt} type="button" onClick={() => setQuestion(prompt)} disabled={chatState === "loading"}>{prompt}</button>
                ))}
              </div>
              <div className="form-footer">
                <span className="helper-text">Answers are provided by the MetricMind backend.</span>
                <button className="send-question" type="submit" disabled={!question.trim() || chatState === "loading"}>Send question <span aria-hidden="true">-&gt;</span></button>
              </div>
            </form>
            <section className={`chat-response chat-response-${chatState}`} aria-label="Response area" aria-live="polite">
              <p className="response-label">Response</p>
              {chatState === "loading" ? (
                <>
                  <p className="question-echo"><strong>Question</strong> {submittedQuestion}</p>
                  <div className="chat-loading" role="status"><span className="chat-spinner" aria-hidden="true" /> Getting your answer...</div>
                </>
              ) : chatState === "error" ? (
                <div className="chat-error" role="alert">
                  <strong>We couldn’t get a response.</strong>
                  <p>{chatError || "Check the connection and try again."} Your question is still available above.</p>
                </div>
              ) : chatState === "answered" ? (
                <>
                  <p className="question-echo"><strong>Question</strong> {submittedQuestion}</p>
                  <dl className="structured-answer">
                    <div><dt>Answer</dt><dd>{chatAnswer}</dd></div>
                  </dl>
                </>
              ) : (
                <p className="helper-text">Your question and its answer will appear here.</p>
              )}
            </section>
          </section>
        </div>

        <section className="history-section" aria-labelledby="question-history-heading">
          <div className="history-toolbar">
            <div>
              <p className="panel-kicker">Saved questions</p>
              <h2 id="question-history-heading">Question history</h2>
            </div>
            <form className="history-search" onSubmit={handleQuestionSearch} role="search">
              <input
                type="search"
                aria-label="Search saved questions"
                placeholder="Search questions"
                value={questionSearch}
                onChange={(event) => setQuestionSearch(event.target.value)}
              />
              <button type="submit">Search</button>
              <button className="history-clear" type="button" onClick={clearQuestionSearch} disabled={!questionSearch && !appliedQuestionSearch}>Clear</button>
            </form>
          </div>

          {historyLoading ? (
            <p className="history-status" role="status">Loading recent questions...</p>
          ) : historyError ? (
            <div className="error-banner" role="alert">
              <span>{historyError}</span>
              <button className="retry-button" type="button" onClick={() => setHistoryReloadKey((current) => current + 1)}>Retry</button>
            </div>
          ) : savedQuestions.length === 0 ? (
            <div className="history-empty">
              {appliedQuestionSearch ? "No saved questions match your search." : "No saved questions yet."}
            </div>
          ) : (
            <>
              <div className="history-list" aria-live="polite">
                {savedQuestions.map((savedQuestion, index) => (
                  <article className="history-item" key={savedQuestion.id ?? `${savedQuestion.created_at}-${index}`}>
                    <p className="history-question">{savedQuestion.question}</p>
                    <time className="history-time" dateTime={savedQuestion.created_at}>{formatQuestionTimestamp(savedQuestion.created_at)}</time>
                  </article>
                ))}
              </div>
              <div className="history-pagination">
                <span className="record-count">
                  {questionTotal === null
                    ? `Showing ${questionOffset + 1}–${questionOffset + savedQuestions.length}`
                    : `Showing ${questionOffset + 1}–${Math.min(questionOffset + savedQuestions.length, questionTotal)} of ${questionTotal}`}
                </span>
                <div>
                  <button type="button" onClick={() => setQuestionOffset((current) => Math.max(0, current - QUESTION_PAGE_SIZE))} disabled={questionOffset === 0 || historyLoading}>Previous</button>
                  <button type="button" onClick={() => setQuestionOffset((current) => current + QUESTION_PAGE_SIZE)} disabled={!hasMoreQuestions || historyLoading}>Next</button>
                </div>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}
