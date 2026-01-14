import math
import pandas as pd
import streamlit as st

EXCEL_FILE = "Calibrage_Collections.xlsx"
COL_COLLECTION = "Collection"
COL_SPP = "NB signes par page"

st.set_page_config(page_title="Calibrage éditorial", layout="centered")

# Style (résultat violet + micro-ajustements)
st.markdown("""
<style>
:root{
  --accent_soft: rgba(124,58,237,.18);
  --accent_soft2: rgba(124,58,237,.08);
  --accent_text: #a78bfa;
  --muted: rgba(255,255,255,.65);
}

.block-container { max-width: 900px; padding-top: 1.2rem; padding-bottom: 2rem; }

.result-card {
  background: linear-gradient(180deg, var(--accent_soft), var(--accent_soft2));
  border-radius: 18px;
  padding: 20px 24px;
  margin-top: 12px;
}

.result-label {
  color: var(--muted);
  margin-bottom: 6px;
  font-size: 0.95rem;
}

.result-value {
  font-size: 56px;
  font-weight: 900;
  color: var(--accent_text);
  line-height: 1.05;
}

.result-sub {
  color: rgba(255,255,255,.60);
  margin-top: 8px;
  font-size: 0.98rem;
}

[data-baseweb="select"] > div {
  border: 1.5px solid rgba(124,58,237,.45) !important;
  box-shadow: 0 0 0 1px rgba(124,58,237,.15) inset;
  border-radius: 14px !important;
}

input { border-radius: 14px !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_collections(excel_path: str) -> pd.DataFrame:
    df = pd.read_excel(excel_path)

    missing = [c for c in (COL_COLLECTION, COL_SPP) if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans l’Excel : {missing}")

    df = df.dropna(subset=[COL_COLLECTION, COL_SPP]).copy()
    df[COL_COLLECTION] = df[COL_COLLECTION].astype(str).str.strip()
    df[COL_SPP] = pd.to_numeric(df[COL_SPP], errors="coerce")
    df = df.dropna(subset=[COL_SPP])
    df = df[df[COL_SPP] > 0]

    # Tri alphabétique (peut être retiré si vous préférez l'ordre Excel)
    df = df.sort_values(COL_COLLECTION)

    df = df.drop_duplicates(subset=[COL_COLLECTION], keep="first")
    return df[[COL_COLLECTION, COL_SPP]].reset_index(drop=True)

try:
    df_collections = load_collections(EXCEL_FILE)
except Exception as e:
    st.error(f"Impossible de charger '{EXCEL_FILE}'. Détail : {e}")
    st.stop()

collections = df_collections[COL_COLLECTION].tolist()

st.title("Calibrage")
st.write("On saisit le nombre de signes, on choisit la collection et on obtient la pagination (avec un arrondi au multiple de 8).")

left, right = st.columns([2, 1])
with left:
    signes = st.number_input("Nombre de signes du manuscrit", min_value=0, step=1000, value=0)
with right:
    collection = st.selectbox("Collection", collections, index=0)

spp = float(df_collections.loc[df_collections[COL_COLLECTION] == collection, COL_SPP].iloc[0])

# Séparateur violet
st.markdown("""
<hr style="
  border: none;
  height: 2px;
  margin: 28px 0 24px 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(124,58,237,.6),
    transparent
  );
">
""", unsafe_allow_html=True)

st.subheader("Pagination prévisionnelle")

def pages_arrondi_8(signes_: int, spp_: float) -> int:
    return math.ceil((signes_ / spp_) / 8) * 8

if signes <= 0:
    st.write("—")
else:
    pages = pages_arrondi_8(int(signes), spp)
    st.markdown(f"""
    <div class="result-card">
      <div class="result-label">Résultat</div>
      <div class="result-value">{pages} pages</div>
      <div class="result-sub">Collection : <strong>{collection}</strong></div>
    </div>
    """, unsafe_allow_html=True)

with st.expander("Détails"):
    st.markdown(f"- **Collection** : {collection}")
    st.markdown(f"- **Signes/page** : {int(spp)}")
    if signes > 0:
        st.markdown(f"- **Pages théoriques** : {signes / spp:.2f}")
    st.markdown("- **Règle** : arrondi au multiple supérieur de 8")
