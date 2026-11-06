import streamlit as st

# Configuração da página do site
st.set_page_config(page_title="Calculadoras Trabalhistas", layout="centered")

st.title("📊 Painel de Análise Trabalhista")
aba = st.sidebar.radio("Selecione a ferramenta:", ["Plantonista 24x48", "Transição CLT para MEI"])

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

    # Cálculos
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

    if st.button("Calcular Proventos"):
        st.success(f"**Salário Bruto Total:** R$ {salario_bruto:.2f}")
        st.write(f"Salário Base: R$ {salario_base:.2f}")
        st.write(f"DSR s/ Horas Normais: R$ {dsr_reais:.2f}")
        st.write(f"DSR Noturno: R$ {dsr_noturno:.2f}")

elif aba == "Transição CLT para MEI":
    st.header("--- CALCULADORA DE TRANSIÇÃO: CLT PARA MEI ---")
    salario_base = st.number_input("1. Salário Base de Referência: R$ ", min_value=0.0, value=3401.81)

    insalubridade = 1621.00 * 0.20
    vale_alimentacao = 600.00
    salario_bruto = salario_base + insalubridade

    # INSS
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

    salario_liquido = salario_bruto - inss
    decimo_terceiro = salario_bruto / 12
    ferias_um_terco = (salario_bruto * 1.333333) / 12
    fgts = salario_bruto * 0.08
    multa_fgts = fgts * 0.40
    custo_mei = 85.00

    ponto_empate = salario_liquido + vale_alimentacao + decimo_terceiro + ferias_um_terco + fgts + multa_fgts + custo_mei
    valor_ideal = ponto_empate * 1.30

    if st.button("Analisar Cenário PJ"):
        st.info(f"**PONTO DE EMPATE FINANCEIRO (Mínimo):** R$ {ponto_empate:.2f}")
        st.success(f"**PEDIDA COM AUMENTO IDEAL (30% Margem):** R$ {valor_ideal:.2f}")

        st.write("--- Detalhamento das Provisões Mensais ---")
        st.write(f"13º Salário Diluído: R$ {decimo_terceiro:.2f}/mês")
        st.write(f"Férias + 1/3 Proporcional: R$ {ferias_um_terco:.2f}/mês")
        st.write(f"FGTS + Reserva de Multa: R$ {(fgts + multa_fgts):.2f}/mês")