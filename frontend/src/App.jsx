import { useState } from "react";
import ReactMarkdown from "react-markdown";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [status, setStatus] = useState("");
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fileCount, setFileCount] = useState(0);

  const startReview = async () => {
    if (!repoUrl.startsWith("https://github.com/")) {
      setError("Please enter a valid GitHub URL starting with https://github.com/");
      return;
    }

    setLoading(true);
    setReport("");
    setError("");
    setStatus("Starting...");
    setFileCount(0);

    try {
      const response = await fetch(`${API_BASE}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;

          try {
            const data = JSON.parse(raw);

            if (data.status === "error") {
              setError(data.message);
              setLoading(false);
              return;
            }

            if (data.status === "complete") {
              setReport(data.report);
              setFileCount(data.file_count);
              setStatus("Complete");
              setLoading(false);
              return;
            }

            if (data.message) setStatus(data.message);

          } catch (e) {
            console.log("Parse error:", e, "on line:", raw);
          }
        }
      }
    } catch (err) {
      setError("Could not connect to backend. Is it running?");
      setLoading(false);
    }
  };

  return (
    <div style={styles.shell}>
      <div style={styles.sidebar}>
        <div style={styles.logo}>🔍 Code Review Agent</div>
        <p style={styles.tagline}>
          Paste a GitHub repo URL and get an AI-powered code quality and security review.
        </p>

        <input
          style={styles.input}
          type="text"
          placeholder="https://github.com/user/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && startReview()}
          disabled={loading}
        />

        <button
          style={{
            ...styles.button,
            opacity: loading || !repoUrl ? 0.5 : 1,
            cursor: loading || !repoUrl ? "not-allowed" : "pointer",
          }}
          onClick={startReview}
          disabled={loading || !repoUrl}
        >
          {loading ? "Analyzing..." : "Start Review"}
        </button>

        {loading && (
          <div style={styles.statusBox}>
            <div style={styles.spinner} />
            <p style={styles.statusText}>{status}</p>
          </div>
        )}

        {error && <p style={styles.error}>{error}</p>}

        {fileCount > 0 && !loading && (
          <div style={styles.statsBox}>
            <p style={styles.statLabel}>Files analyzed</p>
            <p style={styles.statValue}>{fileCount}</p>
          </div>
        )}

        <div style={styles.footer}>
          <p>Powered by</p>
          <p>Groq · LangGraph · FastAPI · React</p>
        </div>
      </div>

      <div style={styles.main}>
        {!report && !loading && (
          <div style={styles.empty}>
            <div style={styles.emptyIcon}>💻</div>
            <p>Enter a GitHub repo URL on the left to get started.</p>
            <p style={styles.emptyHint}>
              Works best on Python, JavaScript, TypeScript, Java, and Go repos.
            </p>
          </div>
        )}

        {loading && !report && (
          <div style={styles.empty}>
            <div style={styles.emptyIcon}>⚙️</div>
            <p style={styles.statusText}>{status}</p>
          </div>
        )}

        {report && (
          <div style={styles.report} className="report-content">
            <ReactMarkdown>{report}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  shell: {
    display: "flex",
    height: "100vh",
    background: "#0f0f0f",
    color: "#e0e0e0",
    fontFamily: "'Segoe UI', sans-serif",
  },
  sidebar: {
    width: "300px",
    minWidth: "300px",
    background: "#1a1a2e",
    display: "flex",
    flexDirection: "column",
    padding: "28px 20px",
    borderRight: "1px solid #2a2a4a",
  },
  logo: {
    fontSize: "20px",
    fontWeight: "700",
    color: "#a78bfa",
    marginBottom: "8px",
  },
  tagline: {
    fontSize: "12px",
    color: "#888",
    marginBottom: "24px",
    lineHeight: "1.6",
  },
  input: {
    background: "#12122a",
    border: "1px solid #3a3a6a",
    borderRadius: "8px",
    color: "#e0e0e0",
    padding: "10px 12px",
    fontSize: "13px",
    marginBottom: "12px",
    outline: "none",
    width: "100%",
    boxSizing: "border-box",
  },
  button: {
    padding: "11px",
    background: "#6d28d9",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "14px",
    fontWeight: "600",
    width: "100%",
    marginBottom: "16px",
  },
  statusBox: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    background: "#12122a",
    borderRadius: "8px",
    padding: "10px 12px",
    marginBottom: "12px",
  },
  spinner: {
    width: "14px",
    height: "14px",
    border: "2px solid #3a3a6a",
    borderTop: "2px solid #a78bfa",
    borderRadius: "50%",
    animation: "spin 0.8s linear infinite",
    flexShrink: 0,
  },
  statusText: {
    fontSize: "12px",
    color: "#a78bfa",
    margin: 0,
  },
  error: {
    fontSize: "12px",
    color: "#f87171",
    marginTop: "8px",
  },
  statsBox: {
    background: "#12122a",
    borderRadius: "8px",
    padding: "12px",
    marginTop: "8px",
    textAlign: "center",
  },
  statLabel: {
    fontSize: "11px",
    color: "#888",
    margin: "0 0 4px",
  },
  statValue: {
    fontSize: "28px",
    fontWeight: "700",
    color: "#a78bfa",
    margin: 0,
  },
  footer: {
    marginTop: "auto",
    fontSize: "11px",
    color: "#555",
    lineHeight: "1.8",
  },
  main: {
    flex: 1,
    overflowY: "auto",
    padding: "32px 40px",
  },
  empty: {
    margin: "auto",
    textAlign: "center",
    color: "#555",
    paddingTop: "120px",
  },
  emptyIcon: {
    fontSize: "48px",
    marginBottom: "16px",
  },
  emptyHint: {
    fontSize: "12px",
    color: "#444",
    marginTop: "8px",
  },
  report: {
    lineHeight: "1.8",
    fontSize: "14px",
    maxWidth: "860px",
  },
};