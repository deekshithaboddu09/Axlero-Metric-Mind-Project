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

type FilterOptions = {
  regions: string[];
  countries: string[];
  products: string[];
  categories: string[];
  quarters: string[];
  min_date: string | null;
  max_date: string | null;
};

type QuestionAnswer = {
  question: string;
  answer: string;
};

const initialSummary: Summary = {
  total_orders: 0,
  total_revenue: 0,
  total_cost: 0,
  total_margin: 0,
};

const initialFilterOptions: FilterOptions = {
  regions: [],
  countries: [],
  products: [],
  categories: [],
  quarters: [],
  min_date: null,
  max_date: null,
};

const filterDefinitions: {
  key: keyof Filters;
  label: string;
}[] = [
  { key: "region", label: "Region" },
  { key: "country", label: "Country" },
  { key: "product_name", label: "Product" },
  { key: "category", label: "Category" },
  { key: "quarter", label: "Quarter" },
];

const suggestedQuestions = [
  "Which quarter had the highest revenue?",
  "Which country generated the most revenue?",
  "Which product has the highest margin?",
  "What is the total revenue for Europe?",
  "Which category generated the highest revenue?",
];

function formatNumber(value: number | string | undefined) {
  const number = Number(value ?? 0);

  return Number.isFinite(number)
    ? new Intl.NumberFormat("en-US", {
        maximumFractionDigits: 2,
      }).format(number)
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
  if (Array.isArray(payload)) {
    return payload as Sale[];
  }

  if (
    payload &&
    typeof payload === "object" &&
    "sales" in payload &&
    Array.isArray(payload.sales)
  ) {
    return payload.sales as Sale[];
  }

  throw new Error("The sales API returned an unexpected response.");
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [submittedQuestion, setSubmittedQuestion] = useState("");
  const [questionAnswer, setQuestionAnswer] = useState("");
  const [summary, setSummary] = useState<Summary>(initialSummary);
  const [sales, setSales] = useState<Sale[]>([]);

function exportSalesToCSV() {
  if (sales.length === 0) {
    return;
  }

  const headers = [
    "Order ID",
    "Order Date",
    "Country",
    "Region",
    "Product",
    "Category",
    "Revenue",
    "Cost",
    "Margin",
    "Quarter",
  ];

  const rows = sales.map((sale) => [
    sale.order_id ?? "",
    sale.order_date ?? "",
    sale.country ?? "",
    sale.region ?? "",
    sale.product_name ?? "",
    sale.category ?? "",
    sale.revenue ?? "",
    sale.total_cost ?? "",
    sale.margin ?? "",
    sale.quarter ?? "",
  ]);

  const escapeCSV = (value: string | number) =>
    `"${String(value).replace(/"/g, '""')}"`;

  const csvContent = [
    headers,
    ...rows,
  ]
    .map((row) => row.map(escapeCSV).join(","))
    .join("\r\n");

  const blob = new Blob(
    ["\uFEFF", csvContent],
    { type: "text/csv;charset=utf-8;" }
  );

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "metricmind_sales.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const [filters, setFilters] = useState<Filters>({
    region: "",
    country: "",
    product_name: "",
    category: "",
    quarter: "",
  });

  const [filterOptions, setFilterOptions] =
    useState<FilterOptions>(initialFilterOptions);
  const [filterOptionsLoading, setFilterOptionsLoading] = useState(true);
  const [filterOptionsError, setFilterOptionsError] = useState("");

  const clearFilters = () => {
    setFilters({
      region: "",
      country: "",
      product_name: "",
      category: "",
      quarter: "",
    });
    setStartDate("");
    setEndDate("");
  };

  const hasActiveFilters =
    Object.values(filters).some(Boolean) ||
    Boolean(startDate) ||
    Boolean(endDate);

  const activeFiltersCount =
    Object.values(filters).filter(Boolean).length +
    (startDate ? 1 : 0) +
    (endDate ? 1 : 0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [questionSaving, setQuestionSaving] = useState(false);
  const [questionMessage, setQuestionMessage] = useState("");
  const [questionError, setQuestionError] = useState("");

  async function loadSummary(
    queryString = "",
    signal?: AbortSignal
  ) {
    const response = await fetch(
      `/backend/summary${queryString}`,
      { signal }
    );

    if (!response.ok) {
      throw new Error(
        `Summary request failed (${response.status}).`
      );
    }

    const data: Summary = await response.json();

    setSummary(data);
  }

  async function loadSales(
    queryString = "",
    signal?: AbortSignal
  ) {
    const response = await fetch(
      `/backend/sales${queryString}`,
      { signal }
    );

    if (!response.ok) {
      throw new Error(
        `Sales request failed (${response.status}).`
      );
    }

    const data: unknown = await response.json();

    setSales(getSales(data));
  }

  useEffect(() => {
    const controller = new AbortController();

    async function loadFilterOptions() {
      setFilterOptionsLoading(true);
      setFilterOptionsError("");

      try {
        const response = await fetch("/backend/filters/options", {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(
            `Filter options request failed (${response.status}).`
          );
        }

        const data: FilterOptions = await response.json();
        setFilterOptions(data);
      } catch (err) {
        if (controller.signal.aborted) {
          return;
        }

        setFilterOptionsError(
          err instanceof Error
            ? err.message
            : "Unable to load filter options."
        );
      } finally {
        if (!controller.signal.aborted) {
          setFilterOptionsLoading(false);
        }
      }
    }

    void loadFilterOptions();

    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      }
    });
    if (startDate) {
      params.set("start_date", startDate);
    }

    if (endDate) {
      params.set("end_date", endDate);
    }

    const query = params.size
      ? `?${params.toString()}`
      : "";

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        await Promise.all([
          loadSummary(query, controller.signal),
          loadSales(
            `${query ? `${query}&` : "?"}limit=1000`,
            controller.signal
          ),
        ]);
      } catch (loadError) {
        if (controller.signal.aborted) {
          return;
        }

        setError(
          loadError instanceof Error
            ? loadError.message
            : "Unable to load dashboard data."
        );
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => controller.abort();
  }, [filters, startDate, endDate]);

  const [pageSize, setPageSize] = useState<number>(25);
  const [currentPage, setCurrentPage] = useState<number>(1);

  useEffect(() => {
    setCurrentPage(1);
  }, [filters, startDate, endDate]);

  const totalPages = Math.max(1, Math.ceil(sales.length / pageSize));
  const safeCurrentPage = Math.min(currentPage, totalPages);
  const startIndex = (safeCurrentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, sales.length);
  const paginatedSales = sales.slice(startIndex, endIndex);

  async function executeQuestion(targetQuestion: string) {
    const trimmedQuestion = targetQuestion.trim();

    if (!trimmedQuestion || questionSaving) {
      return;
    }

    setQuestionSaving(true);
    setQuestionMessage("");
    setQuestionError("");
    setQuestionAnswer("");
    setSubmittedQuestion("");

    try {
      // -------------------------------------------------
      // STEP 1: SAVE QUESTION
      // -------------------------------------------------

      const saveResponse = await fetch(
        "/backend/questions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: trimmedQuestion,
          }),
        }
      );

      if (!saveResponse.ok) {
        let errorMessage =
          `Question save failed (${saveResponse.status}).`;

        try {
          const errorData =
            await saveResponse.json();

          if (
            typeof errorData?.detail === "string"
          ) {
            errorMessage = errorData.detail;
          }
        } catch {
          // Keep default error message.
        }

        throw new Error(errorMessage);
      }

      const savedQuestion: {
        id: number;
        question: string;
      } = await saveResponse.json();

      setSubmittedQuestion(
        savedQuestion.question
      );

      setQuestionMessage(
        "Question saved successfully."
      );

      // -------------------------------------------------
      // STEP 2: GET ANSWER FROM METRICMIND BACKEND
      // -------------------------------------------------

      const answerResponse = await fetch(
        "/backend/questions/answer",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: trimmedQuestion,
          }),
        }
      );

      if (!answerResponse.ok) {
        let errorMessage =
          `Answer request failed (${answerResponse.status}).`;

        try {
          const errorData =
            await answerResponse.json();

          if (
            typeof errorData?.detail === "string"
          ) {
            errorMessage = errorData.detail;
          }
        } catch {
          // Keep default error message.
        }

        throw new Error(errorMessage);
      }

      const answerData: QuestionAnswer =
        await answerResponse.json();

      setQuestionAnswer(answerData.answer);

      // Clear input only after both save + answer succeed.
      setQuestion("");

    } catch (submitError) {
      setQuestionError(
        submitError instanceof Error
          ? submitError.message
          : "Unable to process the question."
      );
    } finally {
      setQuestionSaving(false);
    }
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();
    await executeQuestion(question);
  }

  function updateFilter(
    key: keyof Filters,
    value: string
  ) {
    setFilters((current) => ({
      ...current,
      [key]: value,
    }));
  }

  const quarterRevenue = [
    "Q1",
    "Q2",
    "Q3",
    "Q4",
  ].map((quarter) => ({
    quarter,
    revenue: sales.reduce(
      (total, sale) => {
        return sale.quarter?.toUpperCase() === quarter
          ? total + Number(sale.revenue ?? 0)
          : total;
      },
      0
    ),
  }));

  const maxQuarterRevenue = Math.max(
    ...quarterRevenue.map(
      ({ revenue }) => revenue
    ),
    0
  );

  function optionsFor(key: keyof Filters) {
    const optionListByKey: Record<keyof Filters, string[]> = {
      region: filterOptions.regions,
      country: filterOptions.countries,
      product_name: filterOptions.products,
      category: filterOptions.categories,
      quarter: filterOptions.quarters,
    };

    const backendOptions = optionListByKey[key] ?? [];
    if (backendOptions.length > 0) {
      return backendOptions;
    }

    const valueByKey: Record<
      keyof Filters,
      keyof Sale
    > = {
      region: "region",
      country: "country",
      product_name: "product_name",
      category: "category",
      quarter: "quarter",
    };

    const values = sales
      .map((sale) => sale[valueByKey[key]])
      .filter(
        (value): value is string =>
          typeof value === "string" &&
          value.length > 0
      );

    return [...new Set(values)].sort((left, right) =>
      left.localeCompare(right)
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div
            className="brand-mark"
            aria-hidden="true"
          >
            M
          </div>

          <div>
            <p className="brand-name">
              MetricMind
            </p>

            <p className="brand-caption">
              Business intelligence, made clearer
            </p>
          </div>
        </div>

        <span
          className={`status-pill ${
            loading
              ? "status-loading"
              : error
                ? "status-error"
                : ""
          }`}
        >
          <span className="status-dot" />

          {loading
            ? "Updating data"
            : error
              ? "API unavailable"
              : "Live data"}
        </span>
      </header>

      <main className="dashboard">
        <section className="intro-section">
          <div>
            <p className="eyebrow">
              MetricMind / Overview
            </p>

            <h1>
              Know what moves your business.
            </h1>

            <p className="intro-copy">
              A clear view of orders, revenue,
              and sales performance.
            </p>
          </div>

          <div className="date-note">
            DATA SOURCE
            <br />
            <strong>Sales</strong>
          </div>
        </section>

        <section
          className="filter-section"
          aria-label="Sales filters"
        >
          <div className="filter-heading">
            <div>
              <p className="panel-kicker">Refine results</p>
              <h2>Filters</h2>
            </div>

            {hasActiveFilters && (
              <span className="record-count">
                {activeFiltersCount}{" "}
                {activeFiltersCount === 1
                  ? "filter"
                  : "filters"}{" "}
                applied
              </span>
            )}

            <button
              className="clear-button"
              onClick={clearFilters}
              type="button"
              disabled={!hasActiveFilters}
            >
              Clear all
            </button>
          </div>

          <div className="filter-controls">
            {filterDefinitions.map(
              ({ key, label }) => (
                <label
                  className="filter-control"
                  htmlFor={`filter-${key}`}
                  key={key}
                >
                  <span>{label}</span>

                  <select
                    id={`filter-${key}`}
                    value={filters[key]}
                    disabled={filterOptionsLoading && optionsFor(key).length === 0}
                    onChange={(event) =>
                      updateFilter(key, event.target.value)
                    }
                  >
                    <option value="">
                      All{" "}
                      {key === "country"
                        ? "countries"
                        : key === "category"
                          ? "categories"
                          : `${label.toLowerCase()}s`}
                    </option>

                    {optionsFor(key).map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
              )
            )}

            <label
              className="filter-control date-filter-control"
              htmlFor="filter-start-date"
            >
              <span>Start Date</span>
              <input
                id="filter-start-date"
                type="date"
                value={startDate}
                min={filterOptions.min_date || undefined}
                max={endDate || filterOptions.max_date || undefined}
                onChange={(event) => setStartDate(event.target.value)}
              />
            </label>

            <label
              className="filter-control date-filter-control"
              htmlFor="filter-end-date"
            >
              <span>End Date</span>
              <input
                id="filter-end-date"
                type="date"
                value={endDate}
                min={startDate || filterOptions.min_date || undefined}
                max={filterOptions.max_date || undefined}
                onChange={(event) => setEndDate(event.target.value)}
              />
            </label>
          </div>
        </section>

        {error && (
          <p
            className="error-banner"
            role="alert"
          >
            Could not load dashboard data:
            {" "}
            {error} Confirm the backend is
            running at 127.0.0.1:8000.
          </p>
        )}

        <section
          className="kpi-grid"
          aria-label="Sales summary"
        >
          {[
            {
              label: "Total Orders",
              value: formatNumber(
                summary.total_orders
              ),
              suffix: "orders",
            },
            {
              label: "Total Revenue",
              value: formatMoney(
                summary.total_revenue
              ),
              suffix: "USD",
            },
            {
              label: "Total Cost",
              value: formatMoney(
                summary.total_cost
              ),
              suffix: "USD",
            },
            {
              label: "Total Margin",
              value: formatMoney(
                summary.total_margin
              ),
              suffix: "USD",
            },
          ].map(
            ({
              label,
              value,
              suffix,
            }, index) => (
              <article
                className="kpi-item"
                key={label}
              >
                <div className="kpi-label">
                  <span
                    className={`kpi-mark kpi-mark-${
                      index + 1
                    }`}
                  />
                  {label}
                </div>

                <strong aria-live="polite">
                  {loading
                    ? "Loading..."
                    : error
                      ? "-"
                      : value}
                </strong>

                <span className="kpi-suffix">
                  {suffix}
                </span>
              </article>
            )
          )}
        </section>

        <section className="sales-section">
          <div className="section-heading">
            <div>
              <p className="panel-kicker">
                Transactions
              </p>

              <h2>Recent sales</h2>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
              <button
                type="button"
                className="clear-button"
                onClick={exportSalesToCSV}
                disabled={loading || sales.length === 0}
                title="Download all sales records matching current filters"
              >
                Export CSV ({sales.length})
              </button>

              <span className="record-count">
                {loading
                  ? "Loading records"
                  : `${sales.length} ${sales.length === 1 ? "record" : "records"} found`}
              </span>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Order Date</th>
                  <th>Country</th>
                  <th>Region</th>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Revenue</th>
                  <th>Cost</th>
                  <th>Margin</th>
                  <th>Quarter</th>
                </tr>
              </thead>

              <tbody>
                {paginatedSales.map(
                  (sale, index) => (
                    <tr
                      key={`${
                        sale.order_id ??
                        "order"
                      }-${startIndex + index}`}
                    >
                      <td>
                        {sale.order_id ?? "-"}
                      </td>

                      <td>
                        {sale.order_date ?? "-"}
                      </td>

                      <td>
                        {sale.country ?? "-"}
                      </td>

                      <td>
                        {sale.region ?? "-"}
                      </td>

                      <td>
                        {sale.product_name ??
                          "-"}
                      </td>

                      <td>
                        {sale.category ?? "-"}
                      </td>

                      <td>
                        {formatMoney(
                          sale.revenue
                        )}
                      </td>

                      <td>
                        {formatMoney(
                          sale.total_cost
                        )}
                      </td>

                      <td>
                        {formatMoney(
                          sale.margin
                        )}
                      </td>

                      <td>
                        {sale.quarter ?? "-"}
                      </td>
                    </tr>
                  )
                )}

                {!loading &&
                  sales.length === 0 && (
                    <tr>
                      <td
                        className="table-empty"
                        colSpan={10}
                      >
                        {error
                          ? "Sales records are unavailable."
                          : "No sales records match these filters."}
                      </td>
                    </tr>
                  )}
              </tbody>
            </table>

            {!loading && sales.length > 0 && (
              <div className="pagination-bar">
                <div className="pagination-left">
                  <span>
                    Showing {startIndex + 1}–{endIndex} of {sales.length} records
                  </span>

                  <label className="pagination-page-size">
                    <span>Rows per page:</span>
                    <select
                      value={pageSize}
                      onChange={(e) => {
                        setPageSize(Number(e.target.value));
                        setCurrentPage(1);
                      }}
                    >
                      <option value={15}>15</option>
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                    </select>
                  </label>
                </div>

                <div className="pagination-controls">
                  <button
                    type="button"
                    className="pagination-btn"
                    onClick={() =>
                      setCurrentPage((prev) => Math.max(1, prev - 1))
                    }
                    disabled={safeCurrentPage <= 1}
                  >
                    Previous
                  </button>

                  <span className="pagination-page-info">
                    Page {safeCurrentPage} of {totalPages}
                  </span>

                  <button
                    type="button"
                    className="pagination-btn"
                    onClick={() =>
                      setCurrentPage((prev) =>
                        Math.min(totalPages, prev + 1)
                      )
                    }
                    disabled={safeCurrentPage >= totalPages}
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>

        <div className="insight-grid">
          <section className="panel chart-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  Sales performance
                </p>

                <h2>
                  Revenue by quarter
                </h2>
              </div>

              <span className="record-count">
                Based on loaded records
              </span>
            </div>

            <div
              className="quarter-chart"
              role="img"
              aria-label="Revenue by quarter from currently loaded sales records"
            >
              {quarterRevenue.map(
                ({
                  quarter,
                  revenue,
                }) => (
                  <div
                    className="quarter-column"
                    key={quarter}
                  >
                    <strong>
                      {sales.length
                        ? formatMoney(
                            revenue
                          )
                        : "-"}
                    </strong>

                    <div className="quarter-track">
                      <span
                        style={{
                          height:
                            maxQuarterRevenue
                              ? `${
                                  Math.max(
                                    (revenue /
                                      maxQuarterRevenue) *
                                      100,
                                    revenue
                                      ? 2
                                      : 0
                                  )
                                }%`
                              : "0%",
                        }}
                      />
                    </div>

                    <span className="quarter-label">
                      {quarter}
                    </span>
                  </div>
                )
              )}
            </div>

            {loading && (
              <p className="chart-status">
                Refreshing chart data...
              </p>
            )}

            {!loading &&
              sales.length === 0 && (
                <p className="chart-status">
                  Quarter values will appear when sales records are available.
                </p>
              )}
          </section>

          <section className="panel chat-panel">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">
                  Ask MetricMind
                </p>

                <h2>
                  Business question
                </h2>
              </div>

              <span className="coming-soon">
                AI
              </span>
            </div>

            <div className="suggested-questions">
              <span className="suggested-label">Suggested questions</span>
              <div className="suggestion-chips">
                {suggestedQuestions.map((promptText) => (
                  <button
                    key={promptText}
                    type="button"
                    className="suggestion-chip"
                    onClick={() => {
                      setQuestion(promptText);
                      void executeQuestion(promptText);
                    }}
                    disabled={questionSaving}
                  >
                    {promptText}
                  </button>
                ))}
              </div>
            </div>

            <form
              className="question-form"
              onSubmit={handleSubmit}
            >
              <label htmlFor="business-question">
                What would you like to know?
              </label>

              <textarea
                id="business-question"
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }
                placeholder="e.g. Which quarter had the highest revenue?"
                rows={3}
                disabled={questionSaving}
              />

              <div className="form-footer">
                <span className="helper-text">
                  {questionSaving
                    ? "Analyzing question..."
                    : questionError
                      ? questionError
                      : questionMessage ||
                        "Ask a business question to get an answer."}
                </span>

                <button
                  type="submit"
                  disabled={
                    questionSaving ||
                    !question.trim()
                  }
                >
                  {questionSaving
                    ? "Analyzing..."
                    : "Ask MetricMind"}

                  {" "}

                  <span aria-hidden="true">
                    -&gt;
                  </span>
                </button>
              </div>
            </form>

            <div
              className="chat-response"
              aria-live="polite"
            >
              {submittedQuestion ? (
                <>
                  <p className="question-echo">
                    “{submittedQuestion}”
                  </p>

                  <p className="response-message">
                    {questionAnswer ||
                      "Preparing answer..."}
                  </p>
                </>
              ) : (
                <p className="helper-text">
                  Your answer will appear here.
                </p>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}