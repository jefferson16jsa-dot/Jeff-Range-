import streamlit as st
import matplotlib.pyplot as plt

# Configuração da página do aplicativo
st.set_page_config(page_title="Escalonamento 4-20mA", page_icon="📱")

st.title("📱 Calculadora de Processo 4-20mA")
st.write("Insira os ranges e mova o slider para calcular os valores em tempo real.")

# Inputs estruturados no Frontend
vmin = st.number_input("Range Mínimo (4mA):", value=0.0, step=1.0)
vmax = st.number_input("Range Máximo (20mA):", value=100.0, step=1.0)
uni = st.text_input("Unidade de Engenharia:", value="bar")

st.markdown("---")
st.subheader("🎛️ Controle de Corrente")
i = st.slider("Ajuste a Corrente (mA):", min_value=4.0, max_value=20.0, value=12.0, step=0.01)

# Lógica de cálculo e validação
if vmin != vmax:
    valor_eng = vmin + ((vmax - vmin) / 16.0) * (i - 4.0)
    porcentagem = ((i - 4.0) / 16.0) * 100

    # Exibição de cartões com os resultados
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Valor Convertido", f"{valor_eng:.2f} {uni}")
    with col2:
        st.metric("Porcentagem da Escala", f"{porcentagem:.1f} %")

    # Gráfico de barra vertical indicativo
    if porcentagem < 15.0:
        cor_barra = '#1f77b4'  # Azul
    elif porcentagem > 90.0:
        cor_barra = '#d62728'  # Vermelho
    else:
        cor_barra = '#2ca02c'  # Verde

    fig, ax = plt.subplots(figsize=(3, 5))
    ax.bar(['Processo'], [100], color='#e0e0e0', edgecolor='black', width=0.4)
    ax.bar(['Processo'], [porcentagem], color=cor_barra, edgecolor='black', width=0.4)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Porcentagem (%)")
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    st.pyplot(fig)
else:
    st.error("Erro: O Range Máximo não pode ser idêntico ao Range Mínimo.")
