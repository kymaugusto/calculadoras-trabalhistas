import streamlit as st

# =========================================================
# FUNÇÕES GERAIS DE CÁLCULO (DRY)
# =========================================================

def calcular_inss(salario_bruto):
    """Calcula o INSS Progressivo (Tabela 2026)."""
    teto_inss = 8475.55
    base_inss = min(salario_bruto, teto_inss)
    inss = 0
    
    if base_inss > 4354.27:
        inss += (base_inss - 4354.27) * 0.14
        base_inss = 4354.27
    if base_inss > 2902.84:
        inss += (base_inss - 2902.84) * 0.12
        base_inss = 2902.84
    if base_inss > 1621.00:
        inss += (base_inss - 1621.00) * 0.09
        base_inss = 1621.00
    
    inss += base_inss * 0.075
    return inss

def calcular_irrf(salario_bruto, inss):
    """Calcula o Imposto de Renda Retido na Fonte (IRRF)."""
    if salario_bruto <= 5000.00:
        return 0.0
    
    base_irrf = salario_bruto - inss
    irrf = 0
    
    if base_irrf > 4874.62:
        irrf = (base_irrf * 0.275) - 931.11
    elif base_irrf > 3920.35:
        irrf = (base_irrf * 0.225) - 687.38
    elif base_irrf > 2940.29:
        irrf = (base_irrf * 0.15) - 393.35
    elif base_irrf > 2259.20:
        irrf = (base_irrf * 0.075) - 169.44
        
    return max(0, irrf)

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(page_title="Calculadoras Trabalhistas", layout="centered")

st.title("📊 Painel de Análise Trabalhista")
aba = st.sidebar.radio("Selecione a ferramenta:", ["Plantonista 24x48", "Transição CLT para MEI"])

# =========================================================
# ABA 1: PLANTONISTA HORISTA 24X48
# =========================================================
if aba == "Plantonista 24x48":
    st.header("--- CALCULADORA PLANTONISTA HORISTA 24x48 ---")
    
    col1, col2 = st.columns(2)
    with col1:
        salario_hora = st.number_input("1. Salário Hora: R$ ", min_value=0.0, value=12.15, step=0.1)
    with col2:
        qtd_plantao = st.number_input("2. Plantões no mês: ", min_value=0, value=10)

    tipo_dsr = st.selectbox("O cálculo do DSR é Fixo ou Variável?", ["Fixo por porcentagem", "Variável por calendário"])

    if tipo_dsr == "Fixo por porcentagem":
        porcentagem_dsr = st.number_input("Porcentagem do DSR: ", min_value=0.0, value=16.66)
        fator_dsr = porcentagem_dsr / 100
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            dias_uteis = st.number_input("Dias úteis no mês: ", min_value=1, value=23)
        with c2:
            qtd_domingo = st.number_input("Domingos: ", min_value=0, value=5)
        with c3:
            qtd_feriado = st.number_input("Feriados: ", min_value=0, value=2)
        dias_repouso = qtd_domingo + qtd_feriado

    recebe_vt = st.radio("Recebe Vale Transporte?", ["Não", "Sim"])

    # Cálculos Brutos
    horas_trabalhadas = qtd_plantao * 24
    salario_base = salario_hora * horas_trabalhadas
    insalubridade = 1621 * 0.2
    horas_noturnas_reais = 8 * 1.142857
    adicional_noturno = (salario_hora * 0.2) * (horas_noturnas_reais * qtd_plantao)

    if tipo_dsr == "Fixo por porcentagem":
        dsr_reais = salario_base * fator_dsr
        dsr_noturno = adicional_noturno * fator_dsr
    else:
        dsr = (horas_trabalhadas / dias_uteis) * dias_repouso
        dsr_reais = dsr * salario_hora
        dsr_noturno = (adicional_noturno / dias_uteis) * dias_repouso

    salario_bruto = salario_base + insalubridade + adicional_noturno + dsr_reais + dsr_noturno
    desconto_vt = salario_base * 0.06 if recebe_vt == "Sim" else 0.0
    inss = calcular_inss(salario_bruto)
    irrf = calcular_irrf(salario_bruto, inss)

    salario_liquido = salario_bruto - inss - irrf - desconto_vt

    # Exibição Imediata (Sem botão)
    st.markdown("---")
    st.markdown("### 📋 Extrato de Pagamento")
    st.write(f"**Salário Base:** R$ {salario_base:.2f}")
    st.write(f"**Insalubridade (20% Min.):** R$ {insalubridade:.2f}")
    st.write(f"**Adicional Noturno (20%):** R$ {adicional_noturno:.2f}")
    st.write(f"**DSR Horista:** R$ {dsr_reais:.2f}")
    st.write(f"**DSR Noturno:** R$ {dsr_noturno:.2f}")
    
    st.success(f"**Salário Bruto:** R$ {salario_bruto:.2f}")
    st.error(f"**Desconto INSS:** R$ {inss:.2f}")
    if irrf > 0:
        st.error(f"**Desconto IRRF:** R$ {irrf:.2f}")
    if desconto_vt > 0:
        st.error(f"**Desconto Vale Transporte (6%):** R$ {desconto_vt:.2f}")
        
    st.info(f"**LÍQUIDO ESTIMADO NA CONTA:** R$ {salario_liquido:.2f}")


# =========================================================
# ABA 2: TRANSIÇÃO CLT PARA MEI
# =========================================================
elif aba == "Transição CLT para MEI":
    st.header("--- CALCULADORA DE TRANSIÇÃO: CLT PARA MEI ---")
    
    col1, col2 = st.columns(2)
    with col1:
        salario_base = st.number_input("Salário Base CLT: R$ ", min_value=0.0, value=3291.60)
        insalubridade = st.number_input("Insalubridade: R$ ", min_value=0.0, value=324.20)
    with col2:
        vale_alimentacao = st.number_input("Vale Alimentação (Por fora): R$ ", min_value=0.0, value=600.00)
        custo_deslocamento = st.number_input("Combustível/Pedágio (Mês): R$ ", min_value=0.0, value=0.0)

    # Cálculos
    salario_bruto = salario_base + insalubridade
    inss = calcular_inss(salario_bruto)
    irrf = calcular_irrf(salario_bruto, inss)
    salario_liquido = salario_bruto - inss - irrf

    # Provisões Trabalhistas
    decimo_terceiro = salario_bruto / 12
    ferias_um_terco = (salario_bruto * 1.333333) / 12
    fgts = salario_bruto * 0.08
    multa_fgts = fgts * 0.40
    custo_mei = 85.00

    # NOVO CÁLCULO: Vale alimentação removido da soma do ponto de empate
    ponto_empate = salario_liquido + decimo_terceiro + ferias_um_terco + fgts + multa_fgts + custo_mei + custo_deslocamento
    valor_ideal = ponto_empate * 1.30 # Margem de 30%

    # Exibição Imediata (Sem botão)
    st.markdown("---")
    st.markdown("### 📋 Demonstrativo de Custos e Provisões")
    
    st.write(f"**Salário Base de Referência:** R$ {salario_base:.2f}")
    st.write(f"**Adicional de Insalubridade:** R$ {insalubridade:.2f}")
    st.success(f"**Salário Bruto CLT:** R$ {salario_bruto:.2f}")
    
    st.error(f"**Desconto INSS:** R$ {inss:.2f}")
    st.error(f"**Desconto IRRF:** R$ {irrf:.2f}")
    st.write(f"**Líquido na Conta CLT:** R$ {salario_liquido:.2f}")
    
    st.markdown("#### ⚠️ Custos e Direitos que você perde (Provisão Mensal)")
    st.write(f"- 13º Salário: R$ {decimo_terceiro:.2f}")
    st.write(f"- Férias + 1/3: R$ {ferias_um_terco:.2f}")
    st.write(f"- FGTS + Multa: R$ {(fgts + multa_fgts):.2f}")
    st.write(f"- Imposto MEI (DAS): R$ {custo_mei:.2f}")
    if custo_deslocamento > 0:
        st.write(f"- Deslocamento/Estrada: R$ {custo_deslocamento:.2f}")
    
    st.markdown("---")
    st.info(f"**PONTO DE EMPATE (Mínimo para não perder dinheiro):** R$ {ponto_empate:.2f}")
    st.success(f"**PEDIDA IDEAL (Com +30% de margem):** R$ {valor_ideal:.2f}")
    
    # Destacando que o VA deve ser cobrado por fora
    if vale_alimentacao > 0:
        st.warning(f"🍔 **LEMBRETE:** Acrescentar R$ {vale_alimentacao:.2f} referentes à alimentação por fora no valor da nota ou no contrato.")
