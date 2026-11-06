print("--- CALCULADORA DE TRANSIÇÃO: CLT PARA MEI ---")
salario_base = float(input("1. Salário Base: R$ ").replace(",", "."))

# Insalubridade + VA
insalubridade = 1621.00 * 0.20
vale_alimentacao = 600.00

# Base bruta para cálculo de INSS e FGTS
salario_bruto = salario_base + insalubridade

# Cálculo do INSS Progressivo (com trava de teto)
inss = 0
base_inss = salario_bruto if salario_bruto <= 8475.55 else 8475.55

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

# Cálculo do Imposto de Renda Retido na Fonte (IRRF)
if salario_bruto <= 5000.00:
    irrf = 0.0
else:
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

if irrf < 0:
    irrf = 0

# Salário Líquido que cai na conta do trabalhador CLT
salario_liquido = salario_bruto - inss - irrf

# Cálculos REAIS das provisões trabalhistas (Baseadas no BRUTO)
decimo_terceiro = salario_bruto / 12
ferias_um_terco = (salario_bruto * 1.3333) / 12  # Salário + 1/3 constitucional divididos por 12
fgts = salario_bruto * 0.08
multa_fgts = fgts * 0.40 # Provisão de demissão
custo_mei = 85.00 # Guia DAS-MEI

# Ponto de empate
ponto_empate = salario_liquido + decimo_terceiro + ferias_um_terco + fgts + multa_fgts + custo_mei
valor_ideal = ponto_empate * 1.30

print("\n" + "="*45)
print("RESULTADO DA CONVERSÃO REGULARIZADO".center(45))
print("="*45)
print(f"Salário Bruto CLT:         R$ {salario_bruto:.2f}")
print(f"Desconto INSS:             R$ {inss:.2f}")
print(f"Desconto IRRF:             R$ {irrf:.2f}")
print(f"Salário Líquido na Conta:  R$ {salario_liquido:.2f}")
print(f"Vale Alimentação (CLT):    R$ {vale_alimentacao:.2f}")
print("-" * 45)
print(f"Provisão 13º Salário:      R$ {decimo_terceiro:.2f} /mês")
print(f"Provisão Férias + 1/3:     R$ {ferias_um_terco:.2f} /mês")
print(f"Provisão FGTS (com multa): R$ {(fgts + multa_fgts):.2f} /mês")
print(f"Custo DAS-MEI obrigatório: R$ {custo_mei:.2f} /mês")
print("-" * 45)
print(f"PONTO DE EMPATE (Mínimo):  R$ {ponto_empate:.2f}")
print(f"PEDIDA COM AUMENTO IDEAL:  R$ {valor_ideal:.2f}")
print("="*45)