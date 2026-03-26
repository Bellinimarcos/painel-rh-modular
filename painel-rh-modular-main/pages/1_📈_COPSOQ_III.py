# pages/1_📈_COPSOQ_III.py
# Página de análise COPSOQ III
# Versão conservadora e robusta para importação de dados do Google Forms

import re
import io
import pandas as pd
import streamlit as st

from logic.copsoq_processor import COPSOQProcessor

# Se o projeto tiver armazenamento persistente, tenta usar.
# Se não tiver, a página continua funcionando sem salvar.
try:
    from services.storage import get_persistent_storage
    HAS_STORAGE = True
except Exception:
    HAS_STORAGE = False


st.set_page_config(page_title="COPSOQ III", page_icon="📈", layout="wide")


# =========================
# Funções auxiliares
# =========================

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza cabeçalhos vindos do Google Forms:
    'Q1 - texto da pergunta' -> 'Resp_Q1'

    Mantém compatibilidade com:
    - Resp_Q1
    - Q1
    - P1
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {}

    for col in df.columns:
        c = str(col).strip()

        # Formato Google Forms: Q1 - texto...
        m = re.match(r"^Q(\d+)\s*[-–]\s*", c)
        if m:
            rename_map[col] = f"Resp_Q{m.group(1)}"
            continue

        # Formato simples Q1
        if c.startswith("Q") and c[1:].isdigit():
            rename_map[col] = f"Resp_Q{c[1:]}"
            continue

        # Formato simples P1
        if c.startswith("P") and c[1:].isdigit():
            rename_map[col] = f"Resp_Q{c[1:]}"
            continue

    if rename_map:
        df = df.rename(columns=rename_map)

    return df


def detect_file_format(df: pd.DataFrame):
    """
    Detecta se o arquivo contém:
    - respostas individuais (Resp_Q, P, Q, ou Q1 - texto do Forms)
    - scores calculados por dimensão
    """
    resp_cols = []

    for col in df.columns:
        c = str(col).strip()

        # Resp_Q1
        if c.startswith("Resp_Q") and c[6:].isdigit():
            resp_cols.append(col)
            continue

        # P1 ou Q1
        if (c.startswith("P") or c.startswith("Q")) and c[1:].isdigit():
            resp_cols.append(col)
            continue

        # Q1 - texto da pergunta (Google Forms)
        if re.match(r"^Q(\d+)\s*[-–]\s*", c):
            resp_cols.append(col)
            continue

    exclude_keywords = ["resp_q", "timestamp", "unnamed", "index", "id"]
    numeric_cols = []

    for col in df.columns:
        col_lower = str(col).lower()
        if (
            pd.api.types.is_numeric_dtype(df[col])
            and not any(keyword in col_lower for keyword in exclude_keywords)
        ):
            numeric_cols.append(col)

    if len(numeric_cols) >= 5:
        return "calculated_scores", numeric_cols
    elif len(resp_cols) >= 20:
        return "raw_responses", resp_cols
    else:
        return "unknown", []


def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    """
    Lê CSV ou XLSX com tolerância a separador/encoding.
    """
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        raw = uploaded_file.getvalue()

        # tentativas conservadoras
        attempts = [
            {"sep": ",", "encoding": "utf-8"},
            {"sep": ";", "encoding": "utf-8"},
            {"sep": ",", "encoding": "utf-8-sig"},
            {"sep": ";", "encoding": "utf-8-sig"},
            {"sep": ";", "encoding": "latin1"},
            {"sep": ",", "encoding": "latin1"},
        ]

        last_error = None
        for cfg in attempts:
            try:
                return pd.read_csv(
                    io.BytesIO(raw),
                    sep=cfg["sep"],
                    encoding=cfg["encoding"]
                )
            except Exception as e:
                last_error = e

        raise ValueError(f"Não foi possível ler o CSV. Erro final: {last_error}")

    elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
        return pd.read_excel(uploaded_file)

    else:
        raise ValueError("Formato de arquivo não suportado. Use CSV ou XLSX.")


def render_dimension_table(results: dict):
    if not results:
        st.warning("Nenhuma dimensão pôde ser calculada.")
        return

    df_results = pd.DataFrame(
        [{"Dimensão": k, "Score (0-100)": round(v, 2)} for k, v in results.items()]
    ).sort_values("Dimensão")

    st.dataframe(df_results, use_container_width=True)


def save_analysis_if_possible(result):
    if not HAS_STORAGE:
        return False, "Armazenamento persistente não disponível neste ambiente."

    try:
        storage = get_persistent_storage()
        storage.save_analysis(result)
        return True, "Análise guardada com sucesso."
    except Exception as e:
        return False, f"Não foi possível guardar a análise: {e}"


# =========================
# Interface
# =========================

st.title("📈 COPSOQ III — Importação e Análise")
st.caption("Projeto Itajubá 2026")

with st.expander("ℹ️ Formatos aceites", expanded=False):
    st.markdown(
        """
        Esta página aceita:
        - CSV/XLSX do Google Forms com colunas no formato `Q1 - ...`
        - planilhas com colunas `Resp_Q1`, `Resp_Q2`, ...
        - planilhas com colunas `Q1`, `Q2`, ...
        - planilhas com colunas `P1`, `P2`, ...
        """
    )

uploaded_file = st.file_uploader(
    "Envie a planilha do COPSOQ III",
    type=["csv", "xlsx", "xls"]
)

nome_analise = st.text_input(
    "Nome da análise",
    value="COPSOQ III - Importação"
)

debug_mode = st.toggle("🐞 Debug", value=False)

if uploaded_file is not None:
    try:
        df_original = load_uploaded_file(uploaded_file)
        st.success("Arquivo lido com sucesso.")

        if debug_mode:
            st.subheader("Debug — arquivo original")
            st.write("Colunas originais:")
            st.write(list(df_original.columns))
            st.write("Pré-visualização:")
            st.dataframe(df_original.head(), use_container_width=True)

        detected_format, detected_cols = detect_file_format(df_original)

        st.info(f"Formato detectado: **{detected_format}**")

        if debug_mode:
            st.write(f"Colunas válidas detectadas: {len(detected_cols)}")
            st.write(detected_cols[:20])

        # Normaliza antes de processar
        df = normalize_columns(df_original)

        if debug_mode:
            st.subheader("Debug — após normalização")
            st.write("Colunas normalizadas:")
            st.write(list(df.columns))

            resp_q_cols = [c for c in df.columns if str(c).startswith("Resp_Q")]
            st.write(f"Total de colunas Resp_Q detectadas: {len(resp_q_cols)}")
            st.write(resp_q_cols[:20])

        processor = COPSOQProcessor(version="III")

        # Se for calculado por dimensão, apenas mostrar aviso.
        # O processador atual está preparado para respostas brutas.
        if detected_format == "calculated_scores":
            st.warning(
                "O arquivo parece conter scores já calculados por dimensão. "
                "Esta página está configurada para processar respostas brutas do questionário."
            )

        elif detected_format == "unknown":
            st.error(
                "Formato de arquivo não reconhecido. "
                "Verifique se a planilha contém colunas de perguntas no padrão `Q1 - ...`, "
                "`Resp_Q1`, `Q1` ou `P1`."
            )

        else:
            validation = processor.validate(df)

            if debug_mode:
                st.subheader("Debug — validação")
                st.write("Validação:", validation)

            if not validation.is_valid:
                st.error("Falha na validação do arquivo.")
                if validation.errors:
                    for err in validation.errors:
                        st.write(f"- {err}")
                if getattr(validation, "warnings", None):
                    for warn in validation.warnings:
                        st.write(f"- {warn}")
            else:
                result = processor.process(df, nome_analise)

                st.success("Análise processada com sucesso.")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Respostas", result.metadata.get("n_responses", 0))
                with col2:
                    st.metric("Cobertura/Qualidade", f"{result.metadata.get('coverage', 0):.1f}")
                with col3:
                    risk_label = getattr(result.risk_level, "label", "N/D")
                    risk_emoji = getattr(result.risk_level, "emoji", "📊")
                    st.metric("Risco Global", f"{risk_emoji} {risk_label}")

                st.subheader("Dimensões Processadas")
                render_dimension_table(result.data)

                with st.expander("Ver metadados da análise", expanded=False):
                    st.json(result.metadata)

                if st.button("💾 Guardar análise"):
                    ok, msg = save_analysis_if_possible(result)
                    if ok:
                        st.success(msg)
                    else:
                        st.warning(msg)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        if debug_mode:
            st.exception(e)
else:
    st.info("Envie um arquivo CSV ou XLSX para iniciar a análise.")
