"""
styles.py
---------
Centralizes all custom CSS for the AI Research Assistant frontend.

Streamlit ships with its own default chrome (header, padding, widget
styles) that reads as "a Streamlit app" rather than a polished SaaS
product. This module overrides that chrome with a dark, ChatGPT /
Claude / Perplexity-style theme using CSS variables, while every
component in components.py is written to hook into these same classes.

Usage:
    from styles import inject_custom_css
"""
import streamlit as st

# ---------------------------------------------------------------------------
# Design tokens (single source of truth - matches the required brief exactly)
# ---------------------------------------------------------------------------
COLOR_PRIMARY = "#4F46E5"      # Indigo - primary actions, active states
COLOR_BACKGROUND = "#0F172A"   # App background
COLOR_CARD = "#111827"         # Card / surface background
COLOR_BORDER = "#334155"       # Borders, dividers
COLOR_TEXT = "#F8FAFC"         # Primary text (near-white for readability)
COLOR_TEXT_MUTED = "#94A3B8"   # Secondary / muted text
COLOR_ACCENT = "#22C55E"       # Success / accent (uploads, online status)
COLOR_DANGER = "#EF4444"       # Delete / error actions


def inject_custom_css() -> None:
    """Injects the full custom stylesheet into the Streamlit app."""
    st.markdown(
        f"""
        <style>
        /* =====================================================
           ROOT VARIABLES
        ===================================================== */
        :root {{
            --color-primary: {COLOR_PRIMARY};
            --color-bg: {COLOR_BACKGROUND};
            --color-card: {COLOR_CARD};
            --color-border: {COLOR_BORDER};
            --color-text: {COLOR_TEXT};
            --color-text-muted: {COLOR_TEXT_MUTED};
            --color-accent: {COLOR_ACCENT};
            --color-danger: {COLOR_DANGER};
        }}

        /* =====================================================
           GLOBAL RESET / TYPOGRAPHY
        ===================================================== */
        html, body, [class*="css"] {{
            font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-font-smoothing: antialiased;
        }}

        .stApp {{
            background: radial-gradient(circle at 15% 0%, #16213c 0%, var(--color-bg) 45%) fixed;
            color: var(--color-text);
        }}

        /* Hide Streamlit's default chrome so our custom header/footer own the page */
        #MainMenu {{visibility: hidden;}}
        header[data-testid="stHeader"] {{
            background: transparent;
            height: 0;
        }}
        footer {{visibility: hidden;}}
        div[data-testid="stToolbar"] {{visibility: hidden;}}

        .block-container {{
            padding-top: 1.25rem;
            padding-bottom: 1.5rem;
            max-width: 1450px;
            width: 100%;
        }}

       
        h1, h2, h3, h4 {{
            color: var(--color-text);
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-top: 0;
            margin-bottom: 0.6rem;
        }}

        p, span, label, li {{
            color: var(--color-text);
            font-size: 0.95rem;
        }}

        p {{
            line-height: 1.65;
        }}

        a {{ color: var(--color-primary); text-decoration: none; }}
        a:hover {{ color: #6366F1; text-decoration: underline; }}

        /* =====================================================
           SIDEBAR (sticky, own surface, own scroll)
        ===================================================== */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0B1220 0%, #0A0F1C 100%);
            border-right: 1px solid var(--color-border);
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }}
        section[data-testid="stSidebar"] > div {{
            padding-top: 1rem;
        }}
        section[data-testid="stSidebar"] .block-container {{
            padding-top: 0.5rem;
            padding-left: 1.1rem;
            padding-right: 1.1rem;
        }}
        section[data-testid="stSidebar"] hr {{
            margin: 1rem 0;
            opacity: 0.6;
        }}
        section[data-testid="stSidebar"] ::-webkit-scrollbar {{
            width: auto;
        }}

        /* =====================================================
           CUSTOM HEADER
        ===================================================== */
        .app-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.9rem 1.5rem;
            margin-bottom: 1.4rem;
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid var(--color-border);
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        }}
        .app-header .brand {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }}
        .app-header .brand-icon {{
            width: 40px;
            height: 40px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--color-primary), #7C3AED);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.45);
        }}
        .app-header .brand-text h1 {{
            font-size: 1.15rem;
            margin: 0;
            line-height: 1.1;
        }}
        .app-header .brand-text span {{
            font-size: 0.78rem;
            color: var(--color-text-muted);
        }}
        .status-pill {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            border: 1px solid var(--color-border);
            background: rgba(255, 255, 255, 0.03);
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
        .status-online {{ background: var(--color-accent); box-shadow: 0 0 8px var(--color-accent); }}
        .status-offline {{ background: var(--color-danger); box-shadow: 0 0 8px var(--color-danger); }}

        /* =====================================================
           CARDS (documents, sources, hero, etc.)
        ===================================================== */
        .app-card {{
            background: var(--color-card);
            border: 1px solid var(--color-border);
            border-radius: 14px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.75rem;
            transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .app-card:hover {{
            border-color: var(--color-primary);
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(79, 70, 229, 0.16);
        }}
        .doc-card-title {{
            font-weight: 600;
            font-size: 0.92rem;
            color: var(--color-text);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin: 0 0 0.3rem 0;
        }}
        .doc-card-meta {{
            font-size: 0.76rem;
            color: var(--color-text-muted);
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }}

        /* Sidebar document cards get a slightly tighter, "premium" surface */
        section[data-testid="stSidebar"] .app-card {{
            background: linear-gradient(180deg, rgba(255,255,255,0.025) 0%, rgba(255,255,255,0) 100%), var(--color-card);
            padding: 0.85rem 0.95rem;
            border-radius: 12px;
        }}
        section[data-testid="stSidebar"] .app-card:hover {{
            transform: translateY(-1px);
        }}

        /* =====================================================
           HERO / LANDING / EMPTY STATE
        ===================================================== */
        .hero-wrap {{
            text-align: center;
            padding: 3rem 1.5rem 2.5rem 1.5rem;
        }}
        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.9rem;
            border-radius: 999px;
            background: rgba(79, 70, 229, 0.12);
            border: 1px solid rgba(79, 70, 229, 0.4);
            color: #A5B4FC;
            font-size: 0.78rem;
            font-weight: 600;
            margin-bottom: 1.25rem;
        }}
        .hero-wrap h1 {{
            font-size: 2.4rem;
            margin-bottom: 0.6rem;
            background: linear-gradient(90deg, #FFFFFF 30%, #A5B4FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .hero-wrap p.subtitle {{
            font-size: 1.02rem;
            color: var(--color-text-muted);
            max-width: 560px;
            margin: 0 auto 2rem auto;
            line-height: 1.6;
        }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.9rem;
            margin-top: 1.5rem;
        }}
        @media (max-width: 768px) {{
            .feature-grid {{ grid-template-columns: 1fr; }}
        }}
        .feature-card {{
            background: var(--color-card);
            border: 1px solid var(--color-border);
            border-radius: 14px;
            padding: 1.2rem 1rem;
            text-align: left;
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }}
        .feature-card:hover {{
            transform: translateY(-3px);
            border-color: var(--color-primary);
            box-shadow: 0 12px 26px rgba(79, 70, 229, 0.14);
        }}
        .feature-card .icon {{ font-size: 1.4rem; margin-bottom: 0.5rem; }}
        .feature-card h4 {{ font-size: 0.95rem; margin: 0 0 0.3rem 0; }}
        .feature-card p {{ font-size: 0.8rem; color: var(--color-text-muted); margin: 0; line-height: 1.5; }}

        .empty-chat {{
            text-align: center;
            padding: 2.5rem 1rem;
            color: var(--color-text-muted);
        }}
        .empty-chat .icon {{ font-size: 2.2rem; margin-bottom: 0.5rem; }}

        /* =====================================================
           SOURCE CITATION CARDS (inside expanders)
        ===================================================== */
        .source-card {{
            background: rgba(255, 255, 255, 0.03);
            border-left: 3px solid var(--color-primary);
            border-radius: 8px;
            padding: 0.65rem 0.85rem;
            margin-bottom: 0.5rem;
            transition: background 0.15s ease;
        }}
        .source-card:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        .source-card .source-meta {{
            font-size: 0.75rem;
            font-weight: 700;
            color: #A5B4FC;
            margin-bottom: 0.25rem;
        }}
        .source-card .source-snippet {{
            font-size: 0.82rem;
            color: var(--color-text-muted);
            line-height: 1.55;
        }}

        /* =====================================================
           BUTTONS / SUGGESTED QUESTION CHIPS
        ===================================================== */
        div[data-testid="stButton"] > button {{
            border-radius: 10px;
            border: 1px solid var(--color-border);
            background: var(--color-card);
            color: var(--color-text);
            font-weight: 500;
            padding: 0.5rem 1rem;
            transition: border-color 0.18s ease, background 0.18s ease,
                        box-shadow 0.18s ease, transform 0.12s ease;
        }}
        div[data-testid="stButton"] > button:hover {{
            border-color: var(--color-primary);
            background: rgba(79, 70, 229, 0.15);
            color: #FFFFFF;
            box-shadow: 0 6px 16px rgba(79, 70, 229, 0.22);
        }}
        div[data-testid="stButton"] > button:active {{
            transform: scale(0.98);
            background: rgba(79, 70, 229, 0.25);
        }}
        div[data-testid="stButton"] > button:focus:not(:active) {{
            border-color: var(--color-primary);
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.25);
        }}
        /* Primary-styled buttons (upload, send) */
        div[data-testid="stButton"] > button[kind="primary"] {{
            background: var(--color-primary);
            border-color: var(--color-primary);
            color: #FFFFFF;
        }}
        div[data-testid="stButton"] > button[kind="primary"]:hover {{
            background: #4338CA;
            border-color: #4338CA;
            box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4);
        }}
        div[data-testid="stButton"] > button[kind="primary"]:active {{
            background: #3730A3;
            transform: scale(0.98);
        }}

        /* =====================================================
            CHAT MESSAGES
        ===================================================== */

        div[data-testid="stChatMessage"] {{
            background: var(--color-card);
            border: 1px solid var(--color-border);
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box;
            box-shadow: 0 4px 14px rgba(0,0,0,.25);
        }}

        /* Streamlit applies its own "reading width" cap (~730-740px) to
           text-bearing widgets with higher-specificity internal CSS. Every
           wrapper level between stChatMessage and the actual paragraph text
           has to be forced back to full width with !important, or the cap
           silently wins even when the outer bubble looks full-width. */
        div[data-testid="stChatMessageContent"],
        div[data-testid="stChatMessageContent"] > div,
        div[data-testid="stChatMessage"] [data-testid="stVerticalBlock"],
        div[data-testid="stChatMessage"] [data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stChatMessage"] .element-container,
        div[data-testid="stChatMessage"] [data-testid="stMarkdown"],
        div[data-testid="stMarkdownContainer"] {{
            width: 100% !important;
            max-width: 100% !important;
            flex: 1 1 auto !important;
        }}

        div[data-testid="stMarkdownContainer"] p {{
            margin:0 0 .8rem 0;
            line-height:1.75;
        }}

        div[data-testid="stMarkdownContainer"] ul,
        div[data-testid="stMarkdownContainer"] ol {{
            margin:.4rem 0 1rem 1.2rem;
        }}

        div[data-testid="stMarkdownContainer"] li {{
            margin-bottom:.4rem;
            line-height:1.7;
        }}

        div[data-testid="stMarkdownContainer"] code {{
            background:rgba(255,255,255,.06);
            padding:.15rem .4rem;
            border-radius:6px;
        }}

        div[data-testid="stMarkdownContainer"] pre {{
            border-radius:10px;
            border:1px solid var(--color-border);
        }}

        /* =====================================================
           CHAT INPUT (robust selectors for recent Streamlit versions)
        ===================================================== */
        div[data-testid="stChatInput"] {{
            border-radius: 14px;
            border: 1px solid var(--color-border);
            background: var(--color-card);
            min-height: 52px;
            display: flex;
            align-items: center;
            transition: border-color 0.18s ease, box-shadow 0.18s ease;
        }}
        div[data-testid="stChatInput"]:focus-within {{
            border-color: var(--color-primary);
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.25);
        }}
        /* Newer Streamlit nests the textarea inside stChatInputTextArea;
           older builds render it directly. Target both defensively. */
        div[data-testid="stChatInput"] textarea,
        div[data-testid="stChatInputTextArea"] textarea,
        div[data-testid="stChatInput"] textarea:focus,
        div[data-testid="stChatInput"] textarea:focus-visible {{
            color: var(--color-text) !important;
            -webkit-text-fill-color: var(--color-text) !important;
            caret-color: var(--color-text) !important;
            background: transparent !important;
            min-height: 50px !important;
            max-height: 54px !important;
            line-height: 1.4 !important;
            padding-top: 15px !important;
            padding-bottom: 15px !important;
            display: flex;
            align-items: center;
        }}
        div[data-testid="stChatInput"] textarea::placeholder,
        div[data-testid="stChatInputTextArea"] textarea::placeholder {{
            color: var(--color-text-muted) !important;
            opacity: 1 !important;
        }}
        /* Send button inside the chat input */
        div[data-testid="stChatInput"] button {{
            color: var(--color-text-muted);
            transition: color 0.15s ease, transform 0.12s ease;
        }}
        div[data-testid="stChatInput"] button:hover {{
            color: var(--color-primary);
        }}
        div[data-testid="stChatInput"] button:active {{
            transform: scale(0.94);
        }}

        /* =====================================================
           FLOATING CHAT BAR / BOTTOM CONTAINER
           Removes the default white strip Streamlit renders beneath
           the chat input by blending the bottom container into the
           app background instead of padding it away.
        ===================================================== */
        div[data-testid="stBottom"] {{
            background: linear-gradient(180deg, rgba(15, 23, 42, 0) 0%, var(--color-bg) 55%) !important;
        }}
        /* Streamlit wraps the chat bar in one or more anonymous divs
           (no data-testid) that inherit the light theme background.
           Targeting only the untagged wrappers clears that background
           without touching stChatInput / stBottomBlockContainer, which
           keep their own dark styling defined elsewhere. */
        div[data-testid="stBottom"] div:not([data-testid]) {{
            background: transparent !important;
            box-shadow: none !important;
        }}
        div[data-testid="stBottomBlockContainer"] {{
            background: transparent !important;
            padding-top: 0.5rem;
            padding-bottom: 1rem;
            max-width: 1450px;
        }}
        .stChatFloatingInputContainer {{
            background: transparent !important;
        }}

        /* Suppress the browser's native focus outline on the chat input
           so only our custom focus-within ring (defined above) shows. */
        div[data-testid="stChatInput"] textarea,
        div[data-testid="stChatInputTextArea"] textarea,
        div[data-testid="stChatInput"] {{
            outline: none !important;
        }}

        /* =====================================================
           FILE UPLOADER
        ===================================================== */
        div[data-testid="stFileUploaderDropzone"] {{
            background: var(--color-card);
            border: 1.5px dashed var(--color-border);
            border-radius: 14px;
            padding: 0.6rem;
            transition: border-color 0.18s ease, background 0.18s ease;
        }}
        div[data-testid="stFileUploaderDropzone"]:hover {{
            border-color: var(--color-primary);
            background: rgba(79, 70, 229, 0.06);
        }}
        div[data-testid="stFileUploaderFile"] {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--color-border);
            border-radius: 10px;
        }}

        /* =====================================================
           EXPANDERS (robust across Streamlit versions)
        ===================================================== */
        div[data-testid="stExpander"] {{
            background: var(--color-card);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            margin-bottom: 0.7rem;
            overflow: hidden;
        }}
        div[data-testid="stExpander"] summary {{
            padding: 0.75rem 1rem;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        div[data-testid="stExpander"] summary:hover {{
            color: var(--color-primary);
        }}
        div[data-testid="stExpander"] > div > div {{
            padding: 0.25rem 1rem 0.9rem 1rem;
        }}
        details {{
            background: var(--color-card);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            margin-bottom: 0.6rem;
        }}
        details summary {{
            padding: 0.75rem 1rem;
        }}

        /* =====================================================
           METRICS
        ===================================================== */
        div[data-testid="stMetric"] {{
            background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0) 100%), var(--color-card);
            border: 1px solid var(--color-border);
            border-radius: 12px;
            padding: 0.85rem 1rem;
            transition: border-color 0.18s ease, transform 0.18s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            border-color: var(--color-primary);
            transform: translateY(-1px);
        }}
        div[data-testid="stMetricLabel"] {{
            font-size: 0.75rem;
            color: var(--color-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.4rem;
            font-weight: 700;
        }}

        /* =====================================================
           DIVIDERS / SCROLLBAR
        ===================================================== */
        hr {{ border-color: var(--color-border); margin: 1rem 0; }}

        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{
            background: var(--color-border);
            border-radius: 8px;
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--color-primary); }}

        /* =====================================================
           FOOTER
        ===================================================== */
        .app-footer {{
            margin-top: 2rem;
            padding: 1.25rem 1rem;
            text-align: center;
            border-top: 1px solid var(--color-border);
        }}
        .tech-badge-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
            margin-top: 0.75rem;
        }}
        .tech-badge {{
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
            border: 1px solid var(--color-border);
            background: var(--color-card);
            color: var(--color-text-muted);
            transition: border-color 0.15s ease, color 0.15s ease;
        }}
        .tech-badge:hover {{
            border-color: var(--color-primary);
            color: var(--color-text);
        }}
        .app-footer .caption {{
            font-size: 0.78rem;
            color: var(--color-text-muted);
        }}

        /* =====================================================
           SIDEBAR SECTION LABELS
        ===================================================== */
        .sidebar-label {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--color-text-muted);
            margin: 1.1rem 0 0.6rem 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
