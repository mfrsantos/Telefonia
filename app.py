import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Gestão de Telefonia", layout="wide")

st.title("📱 Gestão Mensal de Telefonia por Centro de Custo")

# 1. Componentes de Upload de Arquivos
col1, col2 = st.columns(2)
with col1:
    fatura_file = st.file_uploader(
        "1. Fatura do Mês (.xlsx / .csv)", type=["xlsx", "csv"]
    )
with col2:
    cadastro_file = st.file_uploader(
        "2. Base Cadastral Atualizada (.xlsx)", type=["xlsx"]
    )

# 2. Processamento e Exibição em Tempo Real
if fatura_file and cadastro_file:
    df_fatura = (
        pd.read_excel(fatura_file)
        if fatura_file.name.endswith(".xlsx")
        else pd.read_csv(fatura_file)
    )
    df_cadastro = pd.read_excel(cadastro_file)

    # Lógica de Cruzamento com Pandas
    df_fatura.columns = ["TELEFONE", "VALOR_FATURA"]
    df_cadastro.columns = ["TELEFONE", "USUARIO", "CENTRO_DE_CUSTO"]

    df_consolidado = pd.merge(
        df_fatura, df_cadastro, on="TELEFONE", how="left"
    )
    df_consolidado["CENTRO_DE_CUSTO"] = df_consolidado[
        "CENTRO_DE_CUSTO"
    ].fillna("NÃO INFORMADO")

    df_resumo = (
        df_consolidado.groupby("CENTRO_DE_CUSTO")
        .agg(
            QTD_LINHAS=("TELEFONE", "count"),
            CUSTO_TOTAL=("VALOR_FATURA", "sum"),
        )
        .reset_index()
    )

    # 3. Cards com Indicadores
    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Custo Total da Fatura",
        f"R$ {df_consolidado['VALOR_FATURA'].sum():,.2f}",
    )
    m2.metric("Linhas Processadas", len(df_consolidado))
    m3.metric("Centros de Custo Ativos", len(df_resumo))

    # 4. Tabela Interativa na Tela
    st.subheader("📊 Resumo Consolidado por Centro de Custo")
    st.dataframe(df_resumo, use_container_width=True)

    # 5. Botão de Download do Excel Final
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_resumo.to_excel(
            writer, sheet_name="RESUMO POR CENTRO DE CUSTO", index=False
        )
        df_consolidado.to_excel(
            writer, sheet_name="BASE CONSOLIDADA", index=False
        )

    st.download_button(
        label="📥 Baixar Planilha Consolidada (Excel)",
        data=output.getvalue(),
        file_name="Relatorio_Telefonia_Consolidado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )