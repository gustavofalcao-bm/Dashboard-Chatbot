import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import warnings
import base64
import io

warnings.filterwarnings('ignore')

logo_icon = load_logo(["BM-Icone.png", "BM Ícone.png", "BM-Icone.jpg"])
logo_full = load_logo(["BASE-MOBILE-Fundo-Transparente.png", "BASE MOBILE - Fundo Transparente.png"])

st.set_page_config(
    page_title="Base Mobile | Gestão de Licenças",
    page_icon="BM-Icone.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== IMAGENS ====================

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

def load_logo(variants):
    for v in variants:
        result = get_base64_image(v)
        if result:
            return result
    return None


# ==================== CORES ====================
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#8BC34A',
    'accent': '#4CAF50',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db',
    'light': '#ecf0f1',
    'claro': '#FF0000',
    'vivo': '#660099',
    'tim': '#0033A0',
    'oi': '#FFCC00',
    'algar': '#00A651'
}

# ==================== CSS ====================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    
    .stApp {{ background: linear-gradient(135deg, #f5f7fa 0%, #e8ecef 100%); }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['secondary']} 0%, {COLORS['accent']} 50%, #2ecc71 100%) !important;
        box-shadow: 5px 0 20px rgba(0,0,0,0.1);
    }}
    
    [data-testid="stSidebar"] * {{ color: white !important; }}
    
    .metric-card {{
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border-left: 5px solid {COLORS['secondary']};
        transition: all 0.3s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(139, 195, 74, 0.3);
    }}
    
    .metric-value {{
        font-size: 3rem;
        font-weight: 800;
        color: {COLORS['primary']};
        line-height: 1;
        margin: 1rem 0;
    }}
    
    .metric-label {{
        font-size: 0.85rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 15px;
        background: white;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 65px;
        padding: 0 3rem;
        border-radius: 12px;
        color: {COLORS['primary']};
        font-weight: 700;
        font-size: 1.1rem;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent']}) !important;
        color: white !important;
        border: 3px solid {COLORS['primary']} !important;
    }}
    
    .stButton>button {{
        border-radius: 12px;
        font-weight: 700;
        border: 3px solid {COLORS['secondary']};
        background: white;
        color: {COLORS['primary']};
        transition: all 0.3s;
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent']});
        color: white;
        transform: translateY(-3px);
    }}
    
    .chat-container {{
        max-height: 600px;
        overflow-y: auto !important;
        padding: 1.5rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }}
    
    .chat-container::-webkit-scrollbar {{ width: 14px; }}
    .chat-container::-webkit-scrollbar-track {{ background: {COLORS['light']}; border-radius: 10px; }}
    .chat-container::-webkit-scrollbar-thumb {{ 
        background: linear-gradient(180deg, {COLORS['secondary']}, {COLORS['accent']}); 
        border-radius: 10px;
    }}
    
    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    
    .loading-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 2rem;
        background: white;
        border-radius: 25px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.15);
        margin: 3rem auto;
        max-width: 600px;
    }}
    
    .loading-spinner {{
        width: 90px;
        height: 90px;
        border: 8px solid {COLORS['light']};
        border-top-color: {COLORS['secondary']};
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 2rem;
    }}
    
    .loading-text {{
        color: {COLORS['primary']};
        font-size: 1.5rem;
        font-weight: 800;
    }}
</style>
""", unsafe_allow_html=True)

# ==================== LOADING ====================

def show_loading(message="Carregando"):
    return st.markdown(f"""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">{message}...</div>
    </div>
    """, unsafe_allow_html=True)

# ==================== CARREGAMENTO ULTRA OTIMIZADO ====================

@st.cache_data(ttl=7200, show_spinner=False)  # 2 horas
def load_excel_optimized():
    """
    OTIMIZAÇÃO PARA 450K+ REGISTROS:
    1. Lê APENAS colunas necessárias
    2. Parse de datas otimizado
    3. Sem loops desnecessários
    """
    try:
        excel_path = Path("MAPEAMENTO DE CHIPS.xlsx")
        if not excel_path.exists():
            return pd.DataFrame()
        
        # Colunas essenciais (ajuste conforme sua planilha)
        cols_needed = [
            'PROJETO', 'OPERADORA', 
            'DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO'
        ]
        
        # Ler todas as sheets de uma vez
        all_sheets = pd.read_excel(
            excel_path, 
            sheet_name=None, 
            engine='openpyxl',
            usecols=lambda x: x.strip().upper() in cols_needed if isinstance(x, str) else False
        )
        
        dfs = []
        for sheet_name, df in all_sheets.items():
            # Normalizar nomes
            df.columns = df.columns.str.strip().str.upper()
            
            # Adicionar projeto se não existir
            if 'PROJETO' not in df.columns:
                df['PROJETO'] = sheet_name
            
            dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        # Concatenar TUDO de uma vez (mais rápido)
        df_completo = pd.concat(dfs, ignore_index=True)
        
        # Converter datas de forma otimizada
        date_cols = ['DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO']
        for col in date_cols:
            if col in df_completo.columns:
                df_completo[col] = pd.to_datetime(df_completo[col], errors='coerce', format='mixed')
        
        return df_completo
    
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=7200, show_spinner=False)
def calcular_metricas_rapido(total_rows, df_hash):
    """Calcula métricas SEM reprocessar o DataFrame"""
    df = st.session_state.df_loaded
    
    hoje = pd.Timestamp.now().normalize()
    
    # Filtrar apenas com datas válidas
    df_com_venc = df[df['DATA DE VENCIMENTO'].notna()]
    
    # Contar de uma vez
    validas = (df_com_venc['DATA DE VENCIMENTO'] > hoje).sum()
    expiradas = (df_com_venc['DATA DE VENCIMENTO'] <= hoje).sum()
    
    return {
        'total': total_rows,
        'vinculadas': total_rows,
        'perc_vinculadas': 100.0,
        'saldo': 0,
        'validas': int(validas),
        'expiradas': int(expiradas)
    }

@st.cache_data(ttl=7200, show_spinner=False)
def agregrar_dados_graficos(df_hash):
    """Pré-agrega dados para gráficos (MUITO mais rápido)"""
    df = st.session_state.df_loaded
    
    # Distribuição por operadora
    df_op = df['OPERADORA'].value_counts().reset_index()
    df_op.columns = ['Operadora', 'Qtd']
    
    # Top 10 projetos
    df_proj = df['PROJETO'].value_counts().head(10).reset_index()
    df_proj.columns = ['Projeto', 'Qtd']
    
    # Vencimentos (só registros com data)
    hoje = pd.Timestamp.now().normalize()
    df_venc = df[df['DATA DE VENCIMENTO'].notna()].copy()
    df_venc = df_venc[df_venc['DATA DE VENCIMENTO'] > hoje]
    
    if not df_venc.empty:
        df_venc['dias'] = (df_venc['DATA DE VENCIMENTO'] - hoje).dt.days
        bins = [0, 30, 90, 180, 365, float('inf')]
        labels = ['0-30 dias', '31-90 dias', '91-180 dias', '181-365 dias', 'Mais de 1 ano']
        df_venc['categoria'] = pd.cut(df_venc['dias'], bins=bins, labels=labels, right=False)
        venc_cat = df_venc['categoria'].value_counts().reindex(labels, fill_value=0)
    else:
        venc_cat = pd.Series([0]*5, index=labels)
    
    # Timeline mensal
    if not df_venc.empty:
        prox_ano = hoje + pd.DateOffset(months=12)
        df_prox = df_venc[df_venc['DATA DE VENCIMENTO'] <= prox_ano]
        df_prox['mes'] = df_prox['DATA DE VENCIMENTO'].dt.to_period('M')
        venc_mensal = df_prox.groupby('mes').size().reset_index(name='Quantidade')
        venc_mensal['mes'] = venc_mensal['mes'].dt.to_timestamp()
    else:
        venc_mensal = pd.DataFrame(columns=['mes', 'Quantidade'])
    
    return {
        'operadoras': df_op,
        'projetos': df_proj,
        'venc_categorias': venc_cat,
        'venc_mensal': venc_mensal
    }

def format_number(num):
    try:
        return f"{int(num):,}".replace(',', '.')
    except:
        return str(num)

def export_to_excel(df, filename):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Licenças')
    return output.getvalue()

# ==================== CHATBOT OTIMIZADO ====================

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'df_loaded' not in st.session_state:
    st.session_state.df_loaded = None
if 'llm_initialized' not in st.session_state:
    st.session_state.llm_initialized = None

@st.cache_resource(show_spinner=False)
def init_llm_optimized():
    """LLM com Groq otimizado para respostas rápidas"""
    try:
        from langchain_groq import ChatGroq
        
        api_key = st.secrets["GROQ_API_KEY"]
        
        return ChatGroq(
            model="llama-3.1-8b-instant",  # Modelo MAIS RÁPIDO (8B ao invés de 70B)
            temperature=0,
            max_tokens=250,  # Reduzido para velocidade
            timeout=60,
            groq_api_key=api_key
        )
        
    except Exception as e:
        st.error(f"❌ Erro Groq: {e}")
        return None

def process_chat_fast(question, df):
    """Chat otimizado - SÓ envia métricas agregadas, NÃO 450k linhas"""
    if df is None or df.empty:
        return {"answer": "❌ Dados não disponíveis.", "time": 0}
    
    # Hash para cache
    df_hash = hash(len(df))
    metricas = calcular_metricas_rapido(len(df), df_hash)
    
    # Resumo MUITO compacto
    dist_op = df['OPERADORA'].value_counts().head(3).to_dict()
    dist_proj = df['PROJETO'].value_counts().head(3).to_dict()
    
    hoje = datetime.now()
    df_venc = df[df['DATA DE VENCIMENTO'].notna()]
    df_venc_fut = df_venc[df_venc['DATA DE VENCIMENTO'] > hoje]
    prox_30d = len(df_venc_fut[df_venc_fut['DATA DE VENCIMENTO'] <= hoje + timedelta(days=30)])
    
    # Contexto MÍNIMO (não manda 450k linhas!)
    contexto = f"""
BASE MOBILE - Gestão de Licenças

MÉTRICAS:
Total: {metricas['total']:,} licenças
Válidas: {metricas['validas']:,}
Expiradas: {metricas['expiradas']:,}
Expirando em 30d: {prox_30d:,}

TOP 3 OPERADORAS: {dist_op}
TOP 3 PROJETOS: {dist_proj}

PERGUNTA: {question}

Responda em português, seja direto e executivo. Máximo 200 palavras.
"""
    
    try:
        import time
        start = time.time()
        
        if st.session_state.llm_initialized is None:
            st.session_state.llm_initialized = init_llm_optimized()
        
        llm = st.session_state.llm_initialized
        
        if llm is None:
            return {"answer": "⚠️ **IA indisponível**", "time": 0}
        
        resposta = llm.invoke(contexto)
        elapsed = time.time() - start
        
        return {"answer": resposta.content if hasattr(resposta, 'content') else str(resposta), "time": elapsed}
    
    except Exception as e:
        return {"answer": f"⚠️ **Erro**: {str(e)[:100]}", "time": 0}

# ==================== SIDEBAR ====================
with st.sidebar:
    if logo_icon:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.2rem; background: white; border-radius: 15px; margin-bottom: 1.5rem;">
            <img src="data:image/png;base64,{logo_icon}" style="max-width: 90px;">
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Gestão de Licenças")
    st.caption("Base Mobile 2026")
    st.markdown("---")
    
    st.markdown("### 🎛️ Ações")
    
    if st.button("🔄 Recarregar", key="reload", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📤 Exportar")
    
    if st.session_state.df_loaded is not None and not st.session_state.df_loaded.empty:
        df = st.session_state.df_loaded
        hoje = pd.Timestamp.now().normalize()
        
        # Expirando 30 dias (sample para não travar)
        df_exp = df[df['DATA DE VENCIMENTO'].notna()]
        df_exp = df_exp[(df_exp['DATA DE VENCIMENTO'] > hoje) & (df_exp['DATA DE VENCIMENTO'] <= hoje + timedelta(days=30))]
        
        if not df_exp.empty:
            excel_exp = export_to_excel(df_exp.head(10000), "expirando.xlsx")  # Limita a 10k
            st.download_button(
                label=f"⚠️ Expirando 30d ({len(df_exp):,})".replace(',', '.'),
                data=excel_exp,
                file_name=f"expirando_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# ==================== HEADER ====================
st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(44, 62, 80, 0.95), rgba(52, 73, 94, 0.95)); 
            padding: 2.5rem 3rem; 
            border-radius: 20px; 
            margin-bottom: 2rem; 
            box-shadow: 0 15px 50px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 2rem;">
    <div style="background: white; padding: 1rem 1.5rem; border-radius: 15px;">
        {f'<img src="data:image/png;base64,{logo_full}" style="max-height: 50px;">' if logo_full else '<div>BASE MOBILE</div>'}
    </div>
    <div>
        <h1 style="color: white; font-size: 2.2rem; font-weight: 800; margin: 0;">
            Gestão de Licenças Corporativas
        </h1>
        <p style="color: {COLORS['secondary']}; font-size: 1.1rem; margin: 0.5rem 0 0 0; font-weight: 600;">
            Sistema Enterprise | Base Mobile 2026
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== CARREGAMENTO ====================
if st.session_state.df_loaded is None:
    loading_placeholder = st.empty()
    
    with loading_placeholder.container():
        show_loading("Processando base de dados")
    
    st.session_state.df_loaded = load_excel_optimized()
    
    # Inicializar LLM em background
    if st.session_state.llm_initialized is None:
        st.session_state.llm_initialized = init_llm_optimized()
    
    loading_placeholder.empty()

df = st.session_state.df_loaded

if df.empty:
    st.error("❌ Erro ao carregar dados")
    st.stop()

st.success(f"✅ **{len(df):,} licenças** de **{df['PROJETO'].nunique()} projetos**".replace(',', '.'))
st.markdown("---")

# ==================== TABS ====================
tab1, tab2 = st.tabs(["📊 Dashboard", "💬 Assistente IA"])

# ==================== TAB 1 ====================
with tab1:
    st.markdown("### 🎯 Indicadores")
    
    df_hash = hash(len(df))
    metricas = calcular_metricas_rapido(len(df), df_hash)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    metrics_data = [
        (col1, "📋 Total", metricas['total'], COLORS['secondary']),
        (col2, "🔗 Vinculadas", metricas['vinculadas'], COLORS['secondary']),
        (col3, "📊 %", f"{metricas['perc_vinculadas']:.0f}%", COLORS['secondary']),
        (col4, "💼 Saldo", metricas['saldo'], COLORS['info']),
        (col5, "✅ Válidas", metricas['validas'], COLORS['accent']),
        (col6, "❌ Expiradas", metricas['expiradas'], COLORS['danger'])
    ]
    
    for col, label, value, color in metrics_data:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color: {color};">{format_number(value) if isinstance(value, (int, float)) else value}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📊 Análises")
    
    # Pegar dados pré-agregados
    dados_graficos = agregrar_dados_graficos(df_hash)
    
    col1, col2 = st.columns(2)
    
    with col1:
        df_op = dados_graficos['operadoras']
        
        color_map = {'CLARO': COLORS['claro'], 'VIVO': COLORS['vivo'], 'TIM': COLORS['tim'], 'OI': COLORS['oi'], 'ALGAR': COLORS['algar']}
        colors_list = [color_map.get(op.upper(), COLORS['secondary']) for op in df_op['Operadora']]
        
        fig = go.Figure(data=[go.Pie(
            labels=df_op['Operadora'],
            values=df_op['Qtd'],
            hole=0.5,
            marker=dict(colors=colors_list, line=dict(color='white', width=4)),
            textfont=dict(size=18, family='Inter', color='white', weight=800),
            textinfo='label+percent'
        )])
        
        fig.update_layout(
            title=dict(text="Por Operadora", font=dict(size=22, family='Inter', color=COLORS['primary'])),
            height=450,
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        df_proj = dados_graficos['projetos']
        
        fig = go.Figure(data=[go.Bar(
            x=df_proj['Qtd'],
            y=df_proj['Projeto'],
            orientation='h',
            marker=dict(color=COLORS['secondary'], line=dict(color='white', width=3)),
            text=df_proj['Qtd'].apply(lambda x: f"{x:,}".replace(',', '.')),
            textposition='outside',
            textfont=dict(size=16, family='Inter', color=COLORS['primary'], weight=800)
        )])
        
        fig.update_layout(
            title=dict(text="Top 10 Projetos", font=dict(size=22, family='Inter', color=COLORS['primary'])),
            height=450,
            yaxis=dict(categoryorder='total ascending', tickfont=dict(size=14, weight=700)),
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📅 Análise de Vencimentos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        venc_cat = dados_graficos['venc_categorias']
        labels = ['0-30 dias', '31-90 dias', '91-180 dias', '181-365 dias', 'Mais de 1 ano']
        colors_v = [COLORS['danger'], COLORS['warning'], COLORS['info'], COLORS['accent'], COLORS['secondary']]
        
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=venc_cat.values,
            marker=dict(color=colors_v, line=dict(color='white', width=3)),
            text=venc_cat.values,
            textposition='outside',
            textfont=dict(size=18, family='Inter', color=COLORS['primary'], weight=800)
        )])
        
        fig.update_layout(
            title=dict(text="Vencimentos por Período", font=dict(size=22, family='Inter', color=COLORS['primary'])),
            height=400,
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        venc_mensal = dados_graficos['venc_mensal']
        
        if not venc_mensal.empty:
            fig = go.Figure(data=[go.Scatter(
                x=venc_mensal['mes'],
                y=venc_mensal['Quantidade'],
                mode='lines+markers',
                line=dict(color=COLORS['danger'], width=5, shape='spline'),
                marker=dict(size=14, color=COLORS['danger'], line=dict(color='white', width=3)),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.15)'
            )])
            
            fig.update_layout(
                title=dict(text="Timeline - Próximos 12 Meses", font=dict(size=22, family='Inter', color=COLORS['primary'])),
                height=400,
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 2 ====================
with tab2:
    st.markdown("### 💬 Assistente IA")
    
    perguntas = {
        "📊 Resumo": "Resumo executivo com principais métricas e insights",
        "⚠️ Riscos": "Principais riscos e alertas críticos",
        "📈 Operadoras": "Análise da distribuição por operadora",
        "🏆 Projetos": "Performance e saúde dos projetos",
        "📅 Vencimentos": "Análise de vencimentos e prioridades",
        "💡 Ações": "Recomendações estratégicas urgentes"
    }
    
    cols = st.columns(3)
    for idx, (label, pergunta) in enumerate(perguntas.items()):
        with cols[idx % 3]:
            if st.button(label, key=f"btn_{idx}", use_container_width=True):
                load_spot = st.empty()
                with load_spot:
                    show_loading(f"Analisando")
                
                result = process_chat_fast(pergunta, df)
                load_spot.empty()
                
                st.session_state.messages.append({"role": "user", "content": label})
                st.session_state.messages.append({"role": "assistant", "content": result["answer"], "time": result["time"]})
                st.rerun()
    
    st.markdown("---")
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.info("💡 Clique em um botão ou digite sua pergunta")
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and "time" in msg:
                    st.caption(f"⏱️ {msg['time']:.1f}s | 🤖 Groq AI")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if user_input := st.chat_input("💭 Digite sua pergunta..."):
        load_spot = st.empty()
        with load_spot:
            show_loading("Processando")
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        result = process_chat_fast(user_input, df)
        load_spot.empty()
        
        st.session_state.messages.append({"role": "assistant", "content": result["answer"], "time": result["time"]})
        st.rerun()

st.markdown("---")
st.caption("Base Mobile 2026 | Sistema Enterprise de Gestão de Licenças")
