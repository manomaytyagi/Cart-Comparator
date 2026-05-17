import { useState, useRef, useCallback, useEffect } from "react";

const BACKEND_URL = "https://cart-comparator.onrender.com";

const PLATFORM_META = {
  zepto: { label: "Zepto", color: "#7c3aed", light: "#f3e8ff", emoji: "⚡" },
  blinkit: {
    label: "Blinkit",
    color: "#d97706",
    light: "#fef3c7",
    emoji: "🟡",
  },
};

const fp = (n) => `₹${Number(n).toFixed(0)}`;

// ─── Upload Zone ─────────────────────────────────────────────────────────────
function UploadZone({ onFile }) {
  const inputRef = useRef();
  const [drag, setDrag] = useState(false);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDrag(false);
      const f = e.dataTransfer.files[0];
      if (f && f.type.startsWith("image/")) onFile(f);
    },
    [onFile],
  );

  return (
    <div
      onClick={() => inputRef.current.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={handleDrop}
      style={{
        border: `2px dashed ${drag ? "#7c3aed" : "#c4b5fd"}`,
        borderRadius: 16,
        padding: "40px 20px",
        textAlign: "center",
        cursor: "pointer",
        background: drag ? "#ede9fe" : "#faf5ff",
        transition: "all 0.2s",
        WebkitTapHighlightColor: "transparent",
        userSelect: "none",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        style={{ display: "none" }}
        onChange={(e) => e.target.files[0] && onFile(e.target.files[0])}
      />
      <div style={{ fontSize: 44, marginBottom: 10 }}>🛒</div>
      <div
        style={{
          fontFamily: "'Syne',sans-serif",
          fontSize: 18,
          fontWeight: 700,
          color: "#4c1d95",
          marginBottom: 4,
        }}
      >
        Tap to upload cart screenshot
      </div>
      <div style={{ fontSize: 13, color: "#8b5cf6" }}>JPG or PNG</div>
    </div>
  );
}

// ─── Loading ──────────────────────────────────────────────────────────────────
function LoadingState() {
  const msgs = [
    "Reading cart with Gemini Vision…",
    "Searching Zepto…",
    "Searching Blinkit…",
    "Matching products…",
    "Comparing prices…",
  ];
  const [i, setI] = useState(0);
  useEffect(() => {
    const iv = setInterval(() => setI((x) => (x + 1) % msgs.length), 2800);
    return () => clearInterval(iv);
  }, [msgs.length]);

  return (
    <div style={{ textAlign: "center", padding: "56px 16px" }}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <div
        style={{
          fontSize: 52,
          display: "inline-block",
          animation: "spin 1.8s linear infinite",
        }}
      >
        ⚙️
      </div>
      <div
        style={{
          fontFamily: "'Syne',sans-serif",
          fontSize: 20,
          fontWeight: 800,
          color: "#4c1d95",
          margin: "16px 0 8px",
        }}
      >
        Comparing prices…
      </div>
      <div
        style={{
          background: "#ede9fe",
          borderRadius: 10,
          padding: "10px 18px",
          display: "inline-block",
          fontSize: 13,
          color: "#6d28d9",
          fontFamily: "monospace",
          marginBottom: 12,
        }}
      >
        {msgs[i]}
      </div>
      <div style={{ fontSize: 12, color: "#a78bfa" }}>
        ⏳ Takes 60–120 seconds. Hang tight.
      </div>
    </div>
  );
}

// ─── Qty Stepper ──────────────────────────────────────────────────────────────
function QtyStepper({ value, onChange }) {
  const Btn = ({ label, action }) => (
    <button
      onClick={(e) => {
        e.stopPropagation();
        action();
      }}
      style={{
        width: 34,
        height: 34,
        borderRadius: 8,
        border: "1.5px solid #c4b5fd",
        background: "#fff",
        color: "#7c3aed",
        fontSize: 20,
        fontWeight: 700,
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
        WebkitTapHighlightColor: "transparent",
        lineHeight: 1,
      }}
    >
      {label}
    </button>
  );
  return (
    <div
      style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}
    >
      <Btn label="−" action={() => onChange(Math.max(1, value - 1))} />
      <span
        style={{
          fontFamily: "'Syne',sans-serif",
          fontWeight: 800,
          fontSize: 16,
          color: "#4c1d95",
          minWidth: 22,
          textAlign: "center",
        }}
      >
        {value}
      </span>
      <Btn label="+" action={() => onChange(value + 1)} />
    </div>
  );
}

// ─── Recompute totals with quantities ────────────────────────────────────────
function computeTotals(data, quantities) {
  const totals = { zepto: 0, blinkit: 0 };
  data.detailed_results?.forEach((item, idx) => {
    const qty = quantities[idx] ?? 1;
    ["zepto", "blinkit"].forEach((p) => {
      const m = item.matches?.[p];
      if (m?.found && m?.in_stock)
        totals[p] += (m.product?.selling_price ?? 0) * qty;
    });
  });
  return totals;
}

// ─── Best Banner ──────────────────────────────────────────────────────────────
function BestBanner({ data, quantities }) {
  const totals = computeTotals(data, quantities);
  const valid = Object.entries(totals).filter(([, v]) => v > 0);
  if (!valid.length) return null;
  const [best, bestTotal] = valid.reduce((a, b) => (b[1] < a[1] ? b : a));
  const meta = PLATFORM_META[best];
  const others = valid.filter(([k]) => k !== best);

  return (
    <div
      style={{
        background: `linear-gradient(135deg,${meta.color}22,${meta.color}08)`,
        border: `2px solid ${meta.color}44`,
        borderRadius: 16,
        padding: "18px 16px",
        display: "flex",
        alignItems: "center",
        gap: 14,
      }}
    >
      <div style={{ fontSize: 42 }}>{meta.emoji}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: 10,
            fontWeight: 700,
            color: meta.color,
            textTransform: "uppercase",
            letterSpacing: 1.5,
            marginBottom: 3,
          }}
        >
          Best deal
        </div>
        <div
          style={{
            fontFamily: "'Syne',sans-serif",
            fontSize: 21,
            fontWeight: 800,
            color: "#1e0a3c",
            lineHeight: 1.2,
          }}
        >
          {meta.label} — {fp(bestTotal)}
        </div>
        {others.map(([k, v]) => (
          <div key={k} style={{ fontSize: 13, color: "#6b7280", marginTop: 3 }}>
            Save {fp(v - bestTotal)} vs {PLATFORM_META[k]?.label} ({fp(v)})
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Platform Totals ──────────────────────────────────────────────────────────
function PlatformTotals({ data, quantities }) {
  const totals = computeTotals(data, quantities);
  const validTotals = Object.entries(totals).filter(([, v]) => v > 0);
  const bestPlatform = validTotals.length
    ? validTotals.reduce((a, b) => (b[1] < a[1] ? b : a))[0]
    : null;

  return (
    <div style={{ display: "flex", gap: 10 }}>
      {Object.entries(PLATFORM_META).map(([platform, meta]) => {
        const total = totals[platform];
        const hasItems = data.available_cart?.[platform]?.length > 0;
        const isBest = platform === bestPlatform && total > 0;
        return (
          <div
            key={platform}
            style={{
              flex: 1,
              background: isBest ? meta.color : "#fff",
              border: `2px solid ${isBest ? meta.color : "#e5e7eb"}`,
              borderRadius: 14,
              padding: "14px 10px",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: 22, marginBottom: 4 }}>{meta.emoji}</div>
            <div
              style={{
                fontFamily: "'Syne',sans-serif",
                fontWeight: 700,
                fontSize: 12,
                color: isBest ? "#fff" : "#374151",
                marginBottom: 4,
              }}
            >
              {meta.label}
            </div>
            {hasItems ? (
              <div
                style={{
                  fontFamily: "'Syne',sans-serif",
                  fontWeight: 800,
                  fontSize: 19,
                  color: isBest ? "#fff" : meta.color,
                }}
              >
                {fp(total)}
              </div>
            ) : (
              <div style={{ fontSize: 12, color: "#9ca3af" }}>—</div>
            )}
            {isBest && (
              <div style={{ fontSize: 10, color: "#ffffffcc", marginTop: 2 }}>
                ★ Cheapest
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ─── Item Card ────────────────────────────────────────────────────────────────
function ItemCard({ item, qty, onQtyChange, screenshotPrices }) {
  const platforms = ["zepto", "blinkit"];
  // Clean display name — strip quantity suffix like "1 pack (75 g)"
  const displayName = item.query
    .replace(/\s+\d+\s*(pack|pc|pcs|piece|pieces|ml|g|kg|l|ltr)[^a-z].*$/i, "")
    .trim();

  return (
    <div
      style={{
        background: "#fff",
        border: "1.5px solid #e5e7eb",
        borderRadius: 14,
        padding: "14px",
      }}
    >
      {/* Header row */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 10,
          marginBottom: 12,
        }}
      >
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              fontFamily: "'Syne',sans-serif",
              fontWeight: 700,
              fontSize: 14,
              color: "#1e0a3c",
              lineHeight: 1.3,
            }}
          >
            {displayName}
          </div>
          {/* Screenshot prices from backend */}
          {screenshotPrices && (
            <div
              style={{
                display: "flex",
                gap: 6,
                marginTop: 5,
                alignItems: "center",
                flexWrap: "wrap",
              }}
            >
              <span
                style={{
                  fontSize: 10,
                  color: "#6b7280",
                  background: "#f3f4f6",
                  borderRadius: 4,
                  padding: "1px 5px",
                }}
              >
                Screenshot
              </span>
              <span style={{ fontSize: 13, fontWeight: 700, color: "#059669" }}>
                {fp(screenshotPrices.discounted)}
              </span>
              {screenshotPrices.original !== screenshotPrices.discounted && (
                <span
                  style={{
                    fontSize: 11,
                    color: "#9ca3af",
                    textDecoration: "line-through",
                  }}
                >
                  {fp(screenshotPrices.original)}
                </span>
              )}
              {screenshotPrices.original > 0 &&
                screenshotPrices.original !== screenshotPrices.discounted && (
                  <span
                    style={{
                      fontSize: 10,
                      background: "#dcfce7",
                      color: "#166534",
                      borderRadius: 20,
                      padding: "1px 6px",
                      fontWeight: 600,
                    }}
                  >
                    {Math.round(
                      (1 -
                        screenshotPrices.discounted /
                          screenshotPrices.original) *
                        100,
                    )}
                    % off
                  </span>
                )}
            </div>
          )}
        </div>
        {/* Qty stepper */}
        <div>
          <div
            style={{
              fontSize: 10,
              color: "#9ca3af",
              textAlign: "center",
              marginBottom: 4,
            }}
          >
            Qty
          </div>
          <QtyStepper value={qty} onChange={onQtyChange} />
        </div>
      </div>

      {/* Platform price columns */}
      <div style={{ display: "flex", gap: 8 }}>
        {platforms.map((platform) => {
          const meta = PLATFORM_META[platform];
          const match = item.matches?.[platform];
          const isBest = item.best_match?.platform === platform;

          let content;
          if (!match || !match.found) {
            content = (
              <div style={{ fontSize: 12, color: "#9ca3af", marginTop: 6 }}>
                Not available
              </div>
            );
          } else if (!match.in_stock) {
            content = (
              <div style={{ fontSize: 12, color: "#f59e0b", marginTop: 6 }}>
                Out of stock
              </div>
            );
          } else {
            const p = match.product;
            const lineTotal = (p.selling_price ?? 0) * qty;
            content = (
              <div style={{ marginTop: 6 }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "baseline",
                    gap: 4,
                    flexWrap: "wrap",
                  }}
                >
                  <span
                    style={{
                      fontFamily: "'Syne',sans-serif",
                      fontWeight: 800,
                      fontSize: 16,
                      color: isBest ? meta.color : "#1e0a3c",
                    }}
                  >
                    {fp(p.selling_price)}
                  </span>
                  {p.mrp && p.mrp !== p.selling_price && (
                    <span
                      style={{
                        fontSize: 10,
                        color: "#9ca3af",
                        textDecoration: "line-through",
                      }}
                    >
                      {fp(p.mrp)}
                    </span>
                  )}
                </div>
                {qty > 1 && (
                  <div style={{ fontSize: 12, color: "#6b7280", marginTop: 2 }}>
                    ×{qty} ={" "}
                    <span style={{ fontWeight: 700, color: meta.color }}>
                      {fp(lineTotal)}
                    </span>
                  </div>
                )}
                <div style={{ fontSize: 10, color: "#9ca3af", marginTop: 2 }}>
                  {p.packsize}
                </div>
                {p.match_score != null && p.match_score < 70 && (
                  <div style={{ fontSize: 10, color: "#d97706", marginTop: 2 }}>
                    ⚠ approx
                  </div>
                )}
              </div>
            );
          }

          return (
            <div
              key={platform}
              style={{
                flex: 1,
                minWidth: 0,
                background:
                  isBest && match?.in_stock ? `${meta.color}0d` : "#f9fafb",
                border: `1.5px solid ${isBest && match?.in_stock ? meta.color + "55" : "#e5e7eb"}`,
                borderRadius: 10,
                padding: "8px 10px",
              }}
            >
              <div
                style={{
                  fontSize: 11,
                  fontWeight: 700,
                  color: meta.color,
                  lineHeight: 1,
                }}
              >
                {meta.emoji} {meta.label}
                {isBest && match?.in_stock ? " ★" : ""}
              </div>
              {content}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Unavailable ──────────────────────────────────────────────────────────────
function UnavailableItems({ items }) {
  if (!items?.length) return null;
  return (
    <div
      style={{
        background: "#fff7ed",
        border: "1.5px solid #fed7aa",
        borderRadius: 14,
        padding: "14px 16px",
      }}
    >
      <div
        style={{
          fontFamily: "'Syne',sans-serif",
          fontWeight: 700,
          color: "#9a3412",
          marginBottom: 8,
          fontSize: 14,
        }}
      >
        ⚠️ Not found anywhere
      </div>
      {items.map((name, i) => (
        <div
          key={i}
          style={{ fontSize: 13, color: "#7c2d12", marginBottom: 3 }}
        >
          •{" "}
          {name
            .replace(/\s+\d+\s*(pack|pc|pcs|ml|g|kg|l)[^a-z].*$/i, "")
            .trim()}
        </div>
      ))}
      <div style={{ fontSize: 11, color: "#b45309", marginTop: 8 }}>
        Not included in platform totals.
      </div>
    </div>
  );
}

// ─── Results ──────────────────────────────────────────────────────────────────
function Results({ data, onReset }) {
  const count = data.detailed_results?.length ?? 0;
  const [quantities, setQuantities] = useState(() => Array(count).fill(1));
  const setQty = (i, v) =>
    setQuantities((q) => {
      const n = [...q];
      n[i] = v;
      return n;
    });

  // Screenshot prices: backend passes original_price + discounted_price per item
  // They're not in detailed_results yet — need backend to include them.
  // To enable: in compare_service.py add original_price + discounted_price to each item in detailed_results.
  // Then read them here as: item.original_price, item.discounted_price
  const getScreenshotPrices = (item) => {
    if (item.original_price != null && item.discounted_price != null) {
      return {
        original: item.original_price,
        discounted: item.discounted_price,
      };
    }
    return null;
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div
          style={{
            fontFamily: "'Syne',sans-serif",
            fontWeight: 800,
            fontSize: 20,
            color: "#1e0a3c",
          }}
        >
          Results
        </div>
        <button
          onClick={onReset}
          style={{
            background: "none",
            border: "1.5px solid #c4b5fd",
            color: "#7c3aed",
            borderRadius: 8,
            padding: "8px 14px",
            fontSize: 13,
            fontWeight: 600,
            cursor: "pointer",
            fontFamily: "'Syne',sans-serif",
            WebkitTapHighlightColor: "transparent",
          }}
        >
          ↩ New scan
        </button>
      </div>

      <BestBanner data={data} quantities={quantities} />
      <PlatformTotals data={data} quantities={quantities} />

      <div
        style={{
          fontFamily: "'Syne',sans-serif",
          fontWeight: 700,
          fontSize: 15,
          color: "#4c1d95",
        }}
      >
        Per-item breakdown
      </div>

      {data.detailed_results?.map((item, i) => (
        <ItemCard
          key={i}
          item={item}
          qty={quantities[i]}
          onQtyChange={(v) => setQty(i, v)}
          screenshotPrices={getScreenshotPrices(item)}
        />
      ))}

      <UnavailableItems items={data.unavailable_products} />

      <div
        style={{
          fontSize: 11,
          color: "#a78bfa",
          textAlign: "center",
          paddingTop: 8,
          borderTop: "1px solid #f3e8ff",
          lineHeight: 1.6,
        }}
      >
        Instamart hidden (not working yet)
        <br />
        Prices are unit prices — totals update with qty above
      </div>

      {/* Disclaimer */}
      <div
        style={{
          fontSize: 12,
          color: "#6b7280",
          textAlign: "center",
          padding: "10px 20px",
          borderTop: "1px solid #e5e7eb",
          marginTop: 20,
        }}
      >
        Prices are exclusive of platform, delivery fees, and taxes. Special
        coupons provided by apps are not included.
      </div>
    </div>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [pincode, setPincode] = useState("110075");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFile = (f) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${BACKEND_URL}/upload?pincode=${pincode}`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) throw new Error(`${res.status}`);
      setResult(await res.json());
    } catch (e) {
      setError(
        "Something went wrong. Check that backend is running and try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(160deg,#faf5ff,#f0fdf4)",
        fontFamily: "'Inter',sans-serif",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap');
        * { box-sizing: border-box; -webkit-font-smoothing: antialiased; }
        body { margin: 0; padding: 0; }
        input:focus { outline: 2px solid #7c3aed; }
        button:active { opacity: 0.85; }
      `}</style>

      {/* Header */}
      <div
        style={{
          background: "linear-gradient(135deg,#4c1d95,#7c3aed)",
          padding: "22px 20px 18px",
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontFamily: "'Syne',sans-serif",
            fontSize: 23,
            fontWeight: 800,
            color: "#fff",
            letterSpacing: -0.5,
          }}
        >
          🛒 Cart Comparator
        </div>
        <div style={{ fontSize: 12, color: "#c4b5fd", marginTop: 3 }}>
          Zepto vs Blinkit — find the best deal
        </div>
      </div>

      {/* Body */}
      <div
        style={{ maxWidth: 480, margin: "0 auto", padding: "18px 14px 80px" }}
      >
        {!result && !loading && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <UploadZone onFile={handleFile} />

            {preview && (
              <div style={{ textAlign: "center" }}>
                <img
                  src={preview}
                  alt="preview"
                  style={{
                    maxHeight: 180,
                    maxWidth: "100%",
                    borderRadius: 12,
                    border: "2px solid #c4b5fd",
                    objectFit: "contain",
                  }}
                />
                <div style={{ fontSize: 12, color: "#8b5cf6", marginTop: 4 }}>
                  {file?.name}
                </div>
              </div>
            )}

            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <label
                style={{
                  fontSize: 13,
                  fontWeight: 600,
                  color: "#4c1d95",
                  whiteSpace: "nowrap",
                }}
              >
                📍 Pincode
              </label>
              <input
                value={pincode}
                onChange={(e) => setPincode(e.target.value)}
                inputMode="numeric"
                style={{
                  flex: 1,
                  border: "1.5px solid #c4b5fd",
                  borderRadius: 10,
                  padding: "12px 14px",
                  fontSize: 15,
                  fontFamily: "monospace",
                  color: "#4c1d95",
                  background: "#faf5ff",
                  outline: "none",
                }}
              />
            </div>

            {error && (
              <div
                style={{
                  background: "#fef2f2",
                  border: "1.5px solid #fca5a5",
                  borderRadius: 12,
                  padding: "12px 14px",
                  fontSize: 13,
                  color: "#991b1b",
                }}
              >
                ❌ {error}
              </div>
            )}

            <button
              onClick={handleSubmit}
              disabled={!file}
              style={{
                background: file
                  ? "linear-gradient(135deg,#7c3aed,#4c1d95)"
                  : "#e5e7eb",
                color: file ? "#fff" : "#9ca3af",
                border: "none",
                borderRadius: 14,
                padding: "17px",
                fontFamily: "'Syne',sans-serif",
                fontWeight: 800,
                fontSize: 17,
                cursor: file ? "pointer" : "not-allowed",
                WebkitTapHighlightColor: "transparent",
              }}
            >
              Compare Prices →
            </button>
          </div>
        )}

        {loading && <LoadingState />}

        {result && !loading && (
          <Results
            data={result}
            onReset={() => {
              setResult(null);
              setFile(null);
              setPreview(null);
              setError(null);
            }}
          />
        )}
      </div>
    </div>
  );
}
