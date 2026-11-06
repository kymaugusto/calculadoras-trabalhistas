print("--- CALCULADORA PLANTONISTA HORISTA 24x48 ---")
salario_hora = float(input("1. Salário Hora: R$ ").replace(",", "."))
qtd_plantao = int(input("2. Quantos plantões você fará no mês: "))

# Pergunta qual tipo de cálculo a empresa usa (converte para maiúsculo com .upper())
tipo_dsr = input("O cálculo do DSR é Fixo por porcentagem ou Variável por calendário? (F/V): ").upper()

# Se for Fixo (F), pede a porcentagem. Se for Variável (V), pede os dados do calendário.
if tipo_dsr == 'F':
    porcentagem_dsr = float(input("Digite a porcentagem do DSR da empresa (ex: 16.66): ").replace(",", "."))
    fator_dsr = porcentagem_dsr / 100
else:
    dias_uteis = int(input("3. Quantos dias úteis tem no mês: "))
    qtd_domingo = int(input("4. Quantos domingos tem no mês: "))
    qtd_feriado = int(input("5. Quantos feriados tem no mês: "))
    dias_repouso = qtd_domingo + qtd_feriado

# Cálculos Base de Horas e Salário
horas_trabalhadas = qtd_plantao * 24
salario_base = salario_hora * horas_trabalhadas

# Cálculo de Insalubridade
insalubridade = 1621 * 0.2

# Cálculo de Adicional Noturno (Com a hora reduzida da CLT: 8h físicas viram ~8.57h)
horas_noturnas_reais = 8 * 1.142857
adicional_noturno = (salario_hora * 0.2) * (horas_noturnas_reais * qtd_plantao)

# Bloco de Decisão do DSR: Calcula as variáveis finais em Reais (R$)
if tipo_dsr == 'F':
    # Método Fixo por Porcentagem
    dsr_reais = salario_base * fator_dsr
    dsr_noturno = adicional_noturno * fator_dsr
else:
    # Método Variável por Calendário
    dsr = (horas_trabalhadas / dias_uteis) * dias_repouso
    dsr_reais = dsr * salario_hora
    dsr_noturno = (adicional_noturno / dias_uteis) * dias_repouso

# Cálculo do Salário Bruto
salario_bruto = salario_base + insalubridade + adicional_noturno + dsr_reais + dsr_noturno

# Cálculo do INSS Progressivo Corrigido (Tabela 2026)
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

# Salário Líquido (sem contar o Imposto de Renda ainda)
salario_liquido = salario_bruto - inss

# Print do Extrato Final Formatado
print("\n" + "="*45)
print("RESULTADO".center(45))
print("="*45)
print(f"Salário Base: R$ {salario_base:.2f}")
print(f"Insalubridade 20%: R$ {insalubridade:.2f}")
print(f"Adicional Noturno 20%: R$ {adicional_noturno:.2f}")
print(f"DSR Horista: R$ {dsr_reais:.2f}")
print(f"DSR Noturno: R$ {dsr_noturno:.2f}")
print(f"Salário Bruto: R$ {salario_bruto:.2f}")
print(f"Desconto INSS: R$ {inss:.2f}")
print(f"Líquido Estimado: R$ {salario_liquido:.2f}")