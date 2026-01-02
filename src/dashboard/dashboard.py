import streamlit as st
import pandas as pd
from kafka import KafkaConsumer
import json
import plotly.express as px
import time
import uuid

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E LAYOUT
# ==========================================
st.set_page_config(page_title="Monitor Crypto", layout="wide")
st.title("📊 Dashboard Streaming (Visão Separada)")

# Configuração das 3 colunas principais (Uma para cada moeda)
col1, col2, col3 = st.columns(3)

# Dicionário de Referência: Onde cada moeda vai ser desenhada
# Definimos cores personalizadas para facilitar a leitura visual
layout_map = {
    'bitcoin': {
        'col': col1, 
        'metric_spot': col1.empty(), 
        'chart_spot': col1.empty(),
        'color': '#F7931A' # Laranja Bitcoin
    },
    'ethereum': {
        'col': col2, 
        'metric_spot': col2.empty(), 
        'chart_spot': col2.empty(),
        'color': '#627EEA' # Azul Ethereum
    },
    'solana': {
        'col': col3, 
        'metric_spot': col3.empty(), 
        'chart_spot': col3.empty(),
        'color': '#14F195' # Verde Solana
    }
}

raw_data_placeholder = st.expander("Ver Dados Brutos (Debug)", expanded=False)

# Inicializa o histórico
if 'df_history' not in st.session_state:
    st.session_state.df_history = pd.DataFrame()

# ==========================================
# 2. CONEXÃO KAFKA
# ==========================================
@st.cache_resource
def get_consumer():
    return KafkaConsumer(
        'monitor-cripto',
        bootstrap_servers=['127.0.0.1:9094'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=f"dash-split-v3-{uuid.uuid4()}", # Novo ID para garantir leitura total
        consumer_timeout_ms=1000
    )

# ==========================================
# 3. LOOP DE LEITURA E RENDERIZAÇÃO
# ==========================================
try:
    consumer = get_consumer()
    st.toast("Conectado! Gerando gráficos individuais...")

    while True:
        msg_pack = consumer.poll(timeout_ms=1000)

        if msg_pack:
            # --- Processamento de Dados ---
            for tp, messages in msg_pack.items():
                for message in messages:
                    data = message.value
                    
                    # COMENTÁRIO: Reativado o Debug Visual Centralizado
                    # Mostra o conteúdo bruto da última mensagem recebida no expander
                    raw_data_placeholder.json(data)

                    # Normalização
                    if isinstance(data, list):
                        batch_df = pd.DataFrame(data)
                    else:
                        batch_df = pd.DataFrame([data])

                    if 'last_updated' in batch_df.columns:
                        batch_df['last_updated'] = pd.to_datetime(batch_df['last_updated'])

                    # Adiciona ao histórico
                    st.session_state.df_history = pd.concat(
                        [st.session_state.df_history, batch_df], ignore_index=True
                    ).tail(1000)

            # --- Atualização Visual (Separada por Moeda) ---
            if not st.session_state.df_history.empty:
                df = st.session_state.df_history
                
                # Loop para atualizar cada coluna independentemente
                for coin_id, layout in layout_map.items():
                    # Filtra os dados apenas desta moeda
                    df_coin = df[df['id'] == coin_id]
                    
                    if not df_coin.empty:
                        # 1. Atualiza Card (Métrica)
                        last_price = df_coin['current_price'].iloc[-1]
                        delta = 0
                        if len(df_coin) > 1:
                            delta = last_price - df_coin['current_price'].iloc[-2]
                            
                        layout['metric_spot'].metric(
                            label=coin_id.upper(), 
                            value=f"R$ {last_price:,.2f}",
                            delta=f"{delta:,.2f}"
                        )

                        # 2. Atualiza Gráfico (Específico da moeda)
                        fig = px.line(
                            df_coin, 
                            x="last_updated", 
                            y="current_price", 
                            title=f"Tendência: {coin_id.capitalize()}",
                            markers=True
                        )
                        # Aplica a cor definida no layout_map e ajusta tamanho
                        fig.update_traces(line_color=layout['color'])
                        fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
                        
                        layout['chart_spot'].plotly_chart(fig, use_container_width=True)

        time.sleep(0.1)

except KeyboardInterrupt:
    st.warning("Dashboard interrompido.")