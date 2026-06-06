import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuração da página do aplicativo
st.set_page_config(page_title="Calculadora de Processo & RTD Labs", page_icon="📱", layout="centered")

# ==========================================
# SIDEBAR: CONVERSOR RTD DE ALTA PRECISÃO
# ==========================================
st.sidebar.markdown("# 🌡️ Conversor RTD Avançado")
st.sidebar.write("Calibração de alta precisão baseada na norma **IEC 60751 / ITS-90**.")

# 1. Seleção do Elemento Sensor
tipo_rtd = st.sidebar.selectbox("1. Elemento Sensor:", ["Pt100", "Pt1000", "Pt500"])

# Define a resistência nominal a 0°C (R0)
if tipo_rtd == "Pt100":
    r0 = 100.0
elif tipo_rtd == "Pt500":
    r0 = 500.0
else:
    r0 = 1000.0

# 2. Seleção do Coeficiente Alpha (Curva do Sensor)
alpha_sel = st.sidebar.selectbox(
    "2. Curva/Coeficiente Alfa (α):",
    [
        "0.003851 (Padrão Europeu / IEC 60751)",
        "0.003916 (Padrão Americano)",
        "0.003925 (Padrão Japonês - JIS)"
    ]
)

# Ajuste estrito das constantes Callendar-Van Dusen de acordo com a seleção
if "0.003851" in alpha_sel:
    A = 3.9083e-3
    B = -5.775e-7
    C = -4.183e-12
elif "0.003916" in alpha_sel:
    A = 3.9692e-3
    B = -5.8495e-7
    C = -4.2325e-12
else: # 0.003925
    A = 3.9739e-3
    B = -5.870e-7
    C = -4.4e-12

# 3. Entrada da Resistência Ôhmica com alta resolução (3 casas decimais)
resistencia = st.sidebar.number_input(
    f"3. Resistência Medida (Ω):", 
    min_value=0.01,
    max_value=r0 * 4.0,
    value=r0, 
    step=0.001,
    format="%.3f"
)

# Algoritmo de Cálculo de Temperatura Iterativo (Newton-Raphson de Alta Precisão)
def calcular_temperatura_rtd(R, R0, A, B, C):
    if R >= R0:
        # Equação exata de 2º Grau para T >= 0 °C
        # R = R0 * (1 + A*t + B*t^2) -> B*t^2 + A*t + (1 - R/R0) = 0
        discriminante = (A ** 2) - (4 * B * (1.0 - (R / R0)))
        if discriminante >= 0:
            return (-A + np.sqrt(discriminante)) / (2.0 * B)
        return None
    else:
        # Equação de 4º Grau para T < 0 °C (Callendar-Van Dusen Completa)
        # R = R0 * [1 + A*t + B*t^2 + C*(t - 100)*t^3]
        # Resolução numérica robusta por aproximações sucessivas
        t_ajustado = (R - R0) / (R0 * A) # Estimativa linear inicial
        for _ in range(12): # 12 iterações garantem precisão de sub-micrograus
            # Função f(t) = R_calculado - R_real
            f_t = R0 * (1.0 + A * t_ajustado + B * (t_ajustado ** 2) + C * (t_ajustado - 100.0) * (t_ajustado ** 3)) - R
            # Derivada f'(t)
            derivada = R0 * (A + 2.0 * B * t_ajustado + C * (4.0 * (t_ajustado ** 3) - 300.0 * (t_ajustado ** 2)))
            if derivada == 0:
                break
            t_ajustado = t_ajustado - (f_t / derivada)
        return t_ajustado

temp_calculada = calcular_temperatura_rtd(resistencia, r0, A, B, C)

# Exibição do resultado do RTD na Sidebar
st.sidebar.markdown("---")
if temp_calculada is not None and -200 <= temp_calculada <= 850:
    st.sidebar.metric(label="📊 Temperatura Exata", value=f"{temp_calculada:.3f} °C")
else:
    st.sidebar.error("Valor fora dos limites físicos do sensor (-200 a 850°C).")


# ==========================================
# PAINEL PRINCIPAL: CALCULADORA 4-20mA
# ==========================================
st.title("📱 Calculadora de Processo 4-20mA")
st.write("Insira os ranges e mova o slider para calcular os valores em tempo real.")

st.markdown("### 🔧 Configuração do Instrumento")

col_in1, col_in2, col_in3 = st.columns(3)
with col_in1:
    vmin = st.number_input("Range Mínimo (4mA):", value=0.0, step=1.0)
with col_in2:
    vmax = st.number_input("Range Máximo (20mA):", value=100.0, step=1.0)
with col_in3:
    uni = st.text_input("Unidade de Engenharia:", value="bar")

st.markdown("---")
st.subheader("🎛️ Controle de Corrente")
i = st.slider("Ajuste a Corrente (mA):", min_value=4.0, max_value=20.0, value=12.0, step=0.01)

if vmin != vmax:
    valor_eng = vmin + ((vmax - vmin) / 16.0) * (i - 4.0)
    porcentagem = ((i - 4.0) / 16.0) * 100

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric("Valor Convertido", f"{valor_eng:.2f} {uni}")
    with col_res2:
        st.metric("Porcentagem da Escala", f"{porcentagem:.1f} %")

    if porcentagem < 15.0:
        cor_barra = '#1f77b4'  
    elif porcentagem > 90.0:
        cor_barra = '#d62728'  
    else:
        cor_barra = '#2ca02c'  

    fig, ax = plt.subplots(figsize=(2, 4.5))
    ax.bar([''], [100], color='#e0e0e0', edgecolor='none', width=0.4)
    ax.bar([''], [porcentagem], color=cor_barra, edgecolor='none', width=0.4)
    
    ax.set_ylim(0, 100)
    ax.set_ylabel("Porcentagem (%)", fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
        
    st.markdown("### 📊 Nível do Processo")
    col_graph1, col_graph2, col_graph3 = st.columns()
    with col_graph2:
        st.pyplot(fig)
else:
    st.error("Erro: O Range Máximo não pode ser idêntico ao Range Mínimo.")

