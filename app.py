import streamlit as st

st.set_page_config(page_title="Calculadoras Trabalhistas", layout="centered")

# =========================================================
# CONSTANTES (conferir e atualizar todo janeiro)
# =========================================================
SALARIO_MINIMO = 1621.00
TETO_INSS = 8475.55
FAIXAS_INSS = [  # (limite superior, aliquota)
    (1621.00, 0.075),
    (2902.84, 0.09),
    (4354.27, 0.12),
    (8475.55, 0.14),
]

# IRRF mensal 2026 (Lei 15.270/2025)
DESCONTO_SIMPLIFICADO = 607.20
LIMITE_ISENCAO_IRRF = 5000.00
LIMITE_REDUTOR_IRRF = 7350.00
FAIXAS_IRRF = [  # (limite superior da base, aliquota, parcela a deduzir)
    (2428.80, 0.0, 0.0),
    (2826.65, 0.075, 182.16),
    (3751.05, 0.15, 394.16),
    (4664.68, 0.225, 675.49),
    (float("inf"), 0.275, 908.73),
]

# MEI
LIMITE_MEI_ANUAL = 81000.00  # sobe para 110 mil em 2027
DAS_MEI = {
    "Comércio/Indústria": 82.05,
    "Serviços": 86.05,
    "Comércio e Serviços": 87.05,
}


# =========================================================
# FUNÇÕES DE CÁLCULO
# =========================================================
def brl(valor):
    """Formata em reais: R$ 1.234,56."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def calcular_inss(salario_bruto):
    """INSS progressivo (tabela 2026)."""
    base = min(salario_bruto, TETO_INSS)
    inss, piso = 0.0, 0.0
    for limite, aliquota in FAIXAS_INSS:
        if base > piso:
            inss += (min(base, limite) - piso) * aliquota
        piso = limite
    return inss


def calcular_irrf(salario_bruto, inss):
    """IRRF mensal 2026: isenção até 5.000 e redutor decrescente até 7.350.
    Não considera dependentes nem pensão."""
    if salario_bruto <= LIMITE_ISENCAO_IRRF:
        return 0.0

    base = salario_bruto - max(inss, DESCONTO_SIMPLIFICADO)
    imposto = 0.0
    for limite, aliquota, deducao in FAIXAS_IRRF:
        if base <= limite:
            imposto = max(0.0, base * aliquota - deducao)
            break

    reducao = 0.0
    if salario_bruto <= LIMITE_REDUTOR_IRRF:
        reducao = 978.62 - 0.133145 * salario_bruto
    return max(0.0, imposto - reducao)


# =========================================================
# ABA 1: PLANTONISTA HORISTA 24X48
# =========================================================
def aba_plantonista():
    st.subheader("Calculadora plantonista horista 24x48")

    col1, col2 = st.columns(2)
    with col1:
        salario_hora = st.number_input("1. Salário hora: R$", min_value=0.0, value=12.15, step=0.1)
    with col2:
        qtd_plantao = st.number_input("2. Plantões no mês:", min_value=0, max_value=15, value=10)

    horas_noturnas = st.number_input(
        "Horas noturnas reais por plantão (já com a hora reduzida de 52min30s aplicada abaixo):",
        min_value=0.0, max_value=12.0, value=8.0, step=0.5,
    )
    tipo_dsr = st.selectbox("O cálculo do DSR é fixo ou variável?", ["Fixo por porcentagem", "Variável por calendário"])

    fator_dsr = 0.0
    dias_uteis, dias_repouso = 1, 0
    if tipo_dsr == "Fixo por porcentagem":
        fator_dsr = st.number_input("Porcentagem do DSR:", min_value=0.0, value=16.66) / 100
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            dias_uteis = st.number_input("Dias úteis no mês:", min_value=1, value=23)
        with c2:
            qtd_domingo = st.number_input("Domingos:", min_value=0, value=5)
        with c3:
            qtd_feriado = st.number_input("Feriados:", min_value=0, value=2)
        dias_repouso = qtd_domingo + qtd_feriado

    recebe_vt = st.radio("Recebe vale transporte?", ["Não", "Sim"])

    # Cálculos
    horas_trabalhadas = qtd_plantao * 24
    salario_base = salario_hora * horas_trabalhadas
    insalubridade = SALARIO_MINIMO * 0.2 if qtd_plantao > 0 else 0.0
    horas_noturnas_fictas = horas_noturnas * (60 / 52.5)
    adicional_noturno = (salario_hora * 0.2) * (horas_noturnas_fictas * qtd_plantao)

    if tipo_dsr == "Fixo por porcentagem":
        dsr_reais = salario_base * fator_dsr
        dsr_noturno = adicional_noturno * fator_dsr
    else:
        dsr_reais = (horas_trabalhadas / dias_uteis) * dias_repouso * salario_hora
        dsr_noturno = (adicional_noturno / dias_uteis) * dias_repouso

    salario_bruto = salario_base + insalubridade + adicional_noturno + dsr_reais + dsr_noturno
    desconto_vt = salario_base * 0.06 if recebe_vt == "Sim" else 0.0
    inss = calcular_inss(salario_bruto)
    irrf = calcular_irrf(salario_bruto, inss)
    salario_liquido = salario_bruto - inss - irrf - desconto_vt

    st.markdown("---")
    st.markdown("### 📋 Extrato de pagamento")
    st.write(f"**Salário base:** {brl(salario_base)}")
    st.write(f"**Insalubridade (20% do mínimo):** {brl(insalubridade)}")
    st.write(f"**Adicional noturno (20%):** {brl(adicional_noturno)}")
    st.write(f"**DSR horista:** {brl(dsr_reais)}")
    st.write(f"**DSR noturno:** {brl(dsr_noturno)}")
    st.success(f"**Salário bruto:** {brl(salario_bruto)}")
    st.error(f"**Desconto INSS:** {brl(inss)}")
    if irrf > 0:
        st.error(f"**Desconto IRRF:** {brl(irrf)}")
    if desconto_vt > 0:
        st.error(f"**Desconto vale transporte (6%):** {brl(desconto_vt)}")
    st.info(f"**LÍQUIDO ESTIMADO NA CONTA:** {brl(salario_liquido)}")


# =========================================================
# ABA 2: TRANSIÇÃO CLT PARA MEI
# =========================================================
def aba_mei():
    st.subheader("Calculadora de transição: CLT para MEI")

    col1, col2 = st.columns(2)
    with col1:
        salario_base = st.number_input("Salário base CLT: R$", min_value=0.0, value=2532.00, step=50.0)
        gratificacao_pct = st.number_input("Gratificação de função (%):", min_value=0.0, value=30.0, step=5.0)
        insalubridade = st.number_input("Insalubridade: R$", min_value=0.0, value=324.20)
    with col2:
        vale_alimentacao = st.number_input("Vale alimentação (por fora): R$", min_value=0.0, value=600.00)
        custo_deslocamento = st.number_input("Combustível/pedágio (mês): R$", min_value=0.0, value=0.0)
        proposta = st.number_input("Valor da nota proposto pela empresa: R$", min_value=0.0, value=3500.00, step=100.0)

    atividade = st.selectbox("Atividade do MEI (define o valor do DAS):", list(DAS_MEI), index=1)

    # Cálculos
    valor_gratificacao = salario_base * (gratificacao_pct / 100)
    salario_bruto = salario_base + valor_gratificacao + insalubridade
    inss = calcular_inss(salario_bruto)
    irrf = calcular_irrf(salario_bruto, inss)
    salario_liquido = salario_bruto - inss - irrf

    decimo_terceiro = salario_bruto / 12
    ferias_um_terco = (salario_bruto * 4 / 3) / 12
    fgts = salario_bruto * 0.08
    multa_fgts = fgts * 0.40
    custo_mei = DAS_MEI[atividade]

    ponto_empate = (
        salario_liquido
        + decimo_terceiro
        + ferias_um_terco
        + fgts
        + multa_fgts
        + custo_mei
        + custo_deslocamento
    )
    valor_ideal = ponto_empate * 1.30

    st.markdown("---")
    st.markdown("### 📋 Demonstrativo de custos e provisões")
    st.write(f"**Salário base de referência:** {brl(salario_base)}")
    if valor_gratificacao > 0:
        st.write(f"**Gratificação de função ({gratificacao_pct:.0f}%):** {brl(valor_gratificacao)}")
    st.write(f"**Adicional de insalubridade:** {brl(insalubridade)}")
    st.success(f"**Salário bruto CLT:** {brl(salario_bruto)}")
    st.error(f"**Desconto INSS:** {brl(inss)}")
    st.error(f"**Desconto IRRF:** {brl(irrf)}")
    st.write(f"**Líquido na conta CLT:** {brl(salario_liquido)}")

    st.markdown("#### ⚠️ Direitos que você perde (provisão mensal)")
    st.write(f"- 13º salário: {brl(decimo_terceiro)}")
    st.write(f"- Férias + 1/3: {brl(ferias_um_terco)}")
    st.write(f"- FGTS + multa: {brl(fgts + multa_fgts)}")
    st.write(f"- Imposto MEI (DAS): {brl(custo_mei)}")
    if custo_deslocamento > 0:
        st.write(f"- Deslocamento/estrada: {brl(custo_deslocamento)}")
    st.caption("Estimativa conservadora: inclui a multa do FGTS e não desconta imposto do 13º e das férias.")

    st.markdown("---")
    st.info(f"**PONTO DE EMPATE (mínimo para não perder dinheiro):** {brl(ponto_empate)}")
    st.success(f"**PEDIDA IDEAL (+30% de margem):** {brl(valor_ideal)}")

    # Comparação com a proposta recebida
    st.markdown("### 🤝 Análise da proposta recebida")
    liquido_mei = proposta - custo_mei - custo_deslocamento
    ganho_liquidez = liquido_mei - salario_liquido

    st.write(
        f"**Dinheiro limpo no bolso no mês (Proposta - DAS):** {brl(liquido_mei)} "
        f"({brl(ganho_liquidez)} de diferença em relação ao líquido CLT)"
    )

    diferenca = proposta - ponto_empate
    if diferenca < 0:
        st.error(
            f"Considerando 13º, férias e FGTS, a proposta de {brl(proposta)} fica {brl(-diferenca)} por mês "
            f"({brl(-diferenca * 12)} por ano) **abaixo** do ponto de empate."
        )
    else:
        st.success(
            f"Considerando 13º, férias e FGTS, a proposta de {brl(proposta)} fica {brl(diferenca)} por mês "
            f"({brl(diferenca * 12)} por ano) **acima** do ponto de empate."
        )

    # Limite de faturamento do MEI
    for rotulo, nota in [("proposta", proposta), ("pedida ideal", valor_ideal)]:
        anual = (nota + vale_alimentacao) * 12
        if anual > LIMITE_MEI_ANUAL:
            st.warning(
                f"Atenção ao limite do MEI: {rotulo} + VA = {brl(anual)} por ano, "
                f"acima de {brl(LIMITE_MEI_ANUAL)} (se o VA entrar na nota)."
            )

    if vale_alimentacao > 0:
        st.warning(
            f"🍔 Lembrete: combine os {brl(vale_alimentacao)} de alimentação por escrito "
            "(contrato ou fora da nota), pois valores na nota contam no limite anual do MEI."
        )


# =========================================================
# INTERFACE PRINCIPAL
# =========================================================
st.title("📊 Painel de Análise Trabalhista")
tab1, tab2 = st.tabs(["Plantonista 24x48", "Transição CLT para MEI"])

with tab1:
    aba_plantonista()

with tab2:
    aba_mei()
