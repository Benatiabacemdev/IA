css = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Remove Streamlit chrome ── */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

[data-testid="stHeader"] { height: 0 !important; }

/* ── Layout — remove excess padding ── */
.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 0.5rem !important;
    max-width: 860px !important;
}

/* ── App header ── */
.rag-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 0.75rem;
}

.rag-logo {
    width: 34px; height: 34px; flex-shrink: 0;
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    box-shadow: 0 2px 8px rgba(99,102,241,0.25);
}

.rag-title {
    font-family: 'Inter', sans-serif;
    font-weight: 600; font-size: 1rem;
    color: #111827; letter-spacing: -0.01em; line-height: 1.2;
}

.rag-model {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; color: #9ca3af;
    letter-spacing: 0.03em; margin-top: 2px;
}

.rag-model span {
    color: #4f46e5;
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    border-radius: 3px;
    padding: 0 5px; margin-left: 4px;
}

/* ── Chat container ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    height: calc(100vh - 210px) !important;
    min-height: 280px !important;
    border-radius: 12px !important;
    border: 1px solid #e5e7eb !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    overflow: hidden !important;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    height: 100% !important;
    overflow-y: auto !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    padding: 0.6rem 0.9rem !important;
    border-bottom: 1px solid #f3f4f6 !important;
}

[data-testid="stChatMessage"]:last-child {
    border-bottom: none !important;
}

[data-testid="stChatMessage"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    line-height: 1.65 !important;
}

/* ── Empty state ── */
.empty-state {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 100%; min-height: 220px;
    text-align: center; gap: 6px;
    padding: 2rem;
}

.empty-logo {
    font-size: 2.5rem;
    opacity: 0.25;
    margin-bottom: 8px;
}

.empty-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem; font-weight: 500;
    color: #9ca3af; margin: 0;
}

.empty-hint {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; color: #d1d5db;
    margin: 0;
}

/* ── Timing row ── */
.timing-row {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; color: #d1d5db;
    display: flex; gap: 14px;
    padding: 0.25rem 0.1rem;
    align-items: center;
}

.timing-seg { display: flex; gap: 4px; align-items: center; }
.timing-dot { color: #6366f1; font-size: 5px; }
.timing-label { color: #9ca3af; }
.timing-val { color: #6b7280; }

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    border-radius: 10px !important;
    border: 1px solid #e5e7eb !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #d1d5db; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    border-right: 1px solid #e5e7eb !important;
}

/* ── Source badges ── */
.source-badges {
    display: flex;
    gap: 5px;
    flex-wrap: wrap;
    margin-top: 6px;
}

.source-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    padding: 2px 7px;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    letter-spacing: 0.02em;
    max-width: 420px;
}

.source-path {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 390px;
    display: inline-block;
}

.source-local {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
}

.source-sharepoint {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #15803d;
}

/* ── Expander (debug) ── */
[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    margin-top: 0.4rem !important;
}

[data-testid="stExpander"] summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
}

[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
}
</style>
'''

bot_template = ''
user_template = ''
