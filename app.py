import streamlit as st

# =========================================================
# FUNÇÕES GERAIS DE CÁLCULO (DRY - Don't Repeat Yourself)
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
    # Regra condicional de isenção até R$ 5.000 (conforme definido no seu projeto)
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
        
    return max(0, irrf) # Garante que o IRRF não seja negativo


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
    
    salario_hora = st.number_input("1. Salário Hora: R$ ", min_value=0.0, value=12.15, step=0.1)
    qtd_plantao = st.number_input("2. Quantos plantões você fará no mês: ", min_value=0, value=10)

    tipo_dsr = st.selectbox("O cálculo do DSR é Fixo ou Variável?", ["Fixo por porcentagem", "Variável por calendário"])

    if tipo_dsr == "Fixo por porcentagem":
        porcentagem_dsr = st.number_input("Digite a porcentagem do DSR da empresa: ", min_value=0.0, value=16.66)
        fator_dsr = porcentagem_dsr / 100
    else:
        dias_uteis = st.number_input("3. Quantos dias úteis tem no mês: ", min_value=1, value=23)
        qtd_domingo = st.number_input("4. Quantos domingos tem no mês: ", min_value=0, value=5)
        qtd_feriado = st.number_input("5. Quantos feriados tem no mês: ", min_value=0, value=2)
        dias_repouso = qtd_domingo + qtd_feriado

    recebe_vt = st.radio("6. Recebe Vale Transporte?", ["Não", "Sim"])

    # Cálculos Brutos
    horas_trabalhadas = qtd_plantao * 24
    salario_base = salario_hora * horas_trabalhadas
    insalubridade = 1621 * 0.2
    horas_noturnas_reais = 8 * 1.142857
    adicional_noturno = (salario_hora * 0.2) * (horas_noturnas_reais * qtd_plantao)

    # Cálculo do DSR
    if tipo_dsr == "Fixo por porcentagem":
        dsr_reais = salario_base * fator_dsr
        dsr_noturno = adicional_noturno * fator_dsr
    else:
        dsr = (horas_trabalhadas / dias_uteis) * dias_repouso
        dsr_reais = dsr * salario_hora
        dsr_noturno = (adicional_noturno / dias_uteis) * dias_repouso

    salario_bruto = salario_base + insalubridade + adicional_noturno + dsr_reais + dsr_noturno

    # Descontos
    desconto_vt = salario_base * 0.06 if recebe_vt == "Sim" else 0.0
    inss = calcular_inss(salario_bruto)
    irrf = calcular_irrf(salario_bruto, inss)

    salario_liquido = salario_bruto - inss - irrf - desconto_vt
