import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import warnings
from langchain_groq import ChatGroq
import time
import base64
import io

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Base Mobile | Gestão de Licenças",
    page_icon="📊",
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

logo_icon = load_logo(["BM-Icone.png", "BM Ícone.png", "BM-Icone.jpg"])
logo_full = load_logo(["BASE-MOBILE-Fundo-Transparente.png", "BASE MOBILE - Fundo Transparente.png"])

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
    
    [data-testid="stSidebar"] .stButton>button {{
        background: rgba(255,255,255,0.2);
        border: 2px solid white;
        color: white !important;
        font-weight: 700;
    }}
    
    [data-testid="stSidebar"] .stButton>button:hover {{
        background: white;
        color: {COLORS['accent']} !important;
        transform: translateX(5px);
    }}
    
    .metric-card {{
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border-left: 5px solid {COLORS['secondary']};
        transition: all 0.3s;
        height: 100%;
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
        border: 3px solid transparent;
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
    
    /* CHAT COM SCROLL COMPLETO */
    .chat-container {{
        max-height: 600px;
        overflow-y: auto !important;
        overflow-x: hidden;
        padding: 1.5rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 2px solid {COLORS['light']};
    }}
    
    .chat-container::-webkit-scrollbar {{ 
        width: 14px; 
        display: block !important;
    }}
    
    .chat-container::-webkit-scrollbar-track {{ 
        background: {COLORS['light']}; 
        border-radius: 10px; 
    }}
    
    .chat-container::-webkit-scrollbar-thumb {{ 
        background: linear-gradient(180deg, {COLORS['secondary']}, {COLORS['accent']}); 
        border-radius: 10px;
        border: 3px solid white;
    }}
    
    .chat-container::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['accent']};
    }}
    
    /* Mensagens do chat */
    .stChatMessage {{
        margin-bottom: 1.5rem !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        background: #f8f9fa !important;
        border-left: 4px solid {COLORS['secondary']} !important;
    }}
    
    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    @keyframes glow {{ 0%, 100% {{ box-shadow: 0 0 30px {COLORS['secondary']}; }} 50% {{ box-shadow: 0 0 60px {COLORS['accent']}; }} }}
    
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
        animation: spin 1s linear infinite, glow 2s ease-in-out infinite;
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

# ==================== DADOS OTIMIZADOS ====================

@st.cache_data(ttl=1800, show_spinner=False)  # 30 minutos
def load_excel_data_optimized():
    """Carrega TODAS as sheets de uma vez - MUITO MAIS RÁPIDO"""
    try:
        excel_path = Path("MAPEAMENTO DE CHIPS.xlsx")
        if not excel_path.exists():
            return pd.DataFrame()
        
        # Lê TODAS as sheets de uma vez
        all_sheets = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
        
        dfs = []
        for sheet_name, df in all_sheets.items():
            df.columns = df.columns.str.strip().str.upper()
            if 'PROJETO' not in df.columns:
                df['PROJETO'] = sheet_name
            dfs.append(df)
        
        if dfs:
            df_completo = pd.concat(dfs, ignore_index=True)
            
            # Converter datas de uma vez
            date_cols = ['DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO']
            for col in date_cols:
                if col in df_completo.columns:
                    df_completo[col] = pd.to_datetime(df_completo[col], errors='coerce')
            
            return df_completo
        
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=1800, show_spinner=False)
def calcular_metricas_cached(df_hash):
    """Métricas cacheadas para evitar recálculo"""
    df = st.session_state.df_loaded
    
    hoje = pd.Timestamp.now().normalize()
    total = len(df)
    df_com_venc = df[df['DATA DE VENCIMENTO'].notna()].copy()
    validas = len(df_com_venc[df_com_venc['DATA DE VENCIMENTO'] > hoje])
    expiradas = len(df_com_venc[df_com_venc['DATA DE VENCIMENTO'] <= hoje])
    
    return {
        'total': total,
        'vinculadas': total,
        'perc_vinculadas': 100.0,
        'saldo': 0,
        'validas': validas,
        'expiradas': expiradas
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
    try:
        from langchain_groq import ChatGroq
        
        api_key = st.secrets.get("OoIzqDaLupPS80u8934nWGdyb3FYpBpLP9vwxnIti9bAV7juaxiA", None)
        
        if not api_key:
            st.error("⚠️ Configure GROQ_API_KEY nas secrets do Streamlit")
            return None
        
        return ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0,
            max_tokens=300,
            api_key=api_key
        )
    except Exception as e:
        st.error(f"Erro ao inicializar Groq: {e}")
        return None



def process_chat_optimized(question, df):
    """Chat otimizado com respostas mais rápidas"""
    if df is None or df.empty:
        return {"answer": "❌ Dados não disponíveis.", "time": 0}
    
    # Hash para cache
    df_hash = hash(len(df))
    metricas = calcular_metricas_cached(df_hash)
    
    dist_op = df['OPERADORA'].value_counts().head(3).to_dict() if 'OPERADORA' in df.columns else {}
    dist_proj = df['PROJETO'].value_counts().head(3).to_dict() if 'PROJETO' in df.columns else {}
    
    hoje = datetime.now()
    df_venc = df[df['DATA DE VENCIMENTO'].notna()].copy()
    df_venc_fut = df_venc[df_venc['DATA DE VENCIMENTO'] > hoje]
    prox_30d = len(df_venc_fut[df_venc_fut['DATA DE VENCIMENTO'] <= hoje + timedelta(days=30)])
    
    contexto = f"""
BASE MOBILE - Licenças:

MÉTRICAS:
- Total: {metricas['total']:,}
- Válidas: {metricas['validas']:,}
- Expiradas: {metricas['expiradas']:,}
- Expirando 30d: {prox_30d:,}

OPERADORAS: {dist_op}
PROJETOS: {dist_proj}

PERGUNTA: {question}

Responda em português brasileiro, seja executivo e direto. Use Markdown (negrito, listas).
Máximo 250 palavras.
"""
    
    try:
        start = time.time()
        
        # Inicializar LLM se necessário
        if st.session_state.llm_initialized is None:
            st.session_state.llm_initialized = init_llm_optimized()
        
        llm = st.session_state.llm_initialized
        
        if llm is None:
            return {"answer": "⚠️ **Ollama indisponível**", "time": 0}
        
        resposta = llm.invoke(contexto)
        elapsed = time.time() - start
        
        return {"answer": resposta, "time": elapsed}
    
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
    
    st.markdown("### 🎛️ Ações Rápidas")
    
    if st.button("🔄 Recarregar", key="reload", width="stretch"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📤 Exportar")
    
    if st.session_state.df_loaded is not None and not st.session_state.df_loaded.empty:
        df = st.session_state.df_loaded
        hoje = pd.Timestamp.now().normalize()
        
        df_expirando = df[df['DATA DE VENCIMENTO'].notna()].copy()
        df_expirando = df_expirando[
            (df_expirando['DATA DE VENCIMENTO'] > hoje) & 
            (df_expirando['DATA DE VENCIMENTO'] <= hoje + timedelta(days=30))
        ]
        
        if not df_expirando.empty:
            excel_exp = export_to_excel(df_expirando, "expirando.xlsx")
            st.download_button(
                label="⚠️ Expirando 30d",
                data=excel_exp,
                file_name=f"expirando_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )
        
        excel_all = export_to_excel(df, "todas.xlsx")
        st.download_button(
            label="📋 Todas",
            data=excel_all,
            file_name=f"todas_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
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
            Monitoramento em Tempo Real | Base Mobile 2026
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== PRÉ-CARREGAMENTO ====================
if st.session_state.df_loaded is None:
    loading_placeholder = st.empty()
    
    with loading_placeholder.container():
        show_loading("Carregando base de dados")
    
    st.session_state.df_loaded = load_excel_data_optimized()
    
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
    metricas = calcular_metricas_cached(df_hash)
    
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'OPERADORA' in df.columns:
            df_op = df['OPERADORA'].value_counts().reset_index()
            df_op.columns = ['Operadora', 'Qtd']
            
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
            
            st.plotly_chart(fig, width="stretch")
    
    with col2:
        if 'PROJETO' in df.columns:
            df_proj = df['PROJETO'].value_counts().head(10).reset_index()
            df_proj.columns = ['Projeto', 'Qtd']
            
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
            
            st.plotly_chart(fig, width="stretch")

# ==================== TAB 2 COM SCROLL ====================
with tab2:
    st.markdown("### 💬 Assistente IA")
    
    perguntas = {
        "📊 Resumo": "Resumo executivo por projeto com chips, expirando e insights",
        "⚠️ Riscos": "Principais riscos e alertas",
        "📈 Operadoras": "Análise por operadora",
        "🏆 Projetos": "Performance dos projetos",
        "📅 Vencimentos": "Análise de vencimentos",
        "💡 Ações": "Recomendações estratégicas"
    }
    
    cols = st.columns(3)
    for idx, (label, pergunta) in enumerate(perguntas.items()):
        with cols[idx % 3]:
            if st.button(label, key=f"btn_{idx}", width="stretch"):
                load_spot = st.empty()
                with load_spot:
                    show_loading(f"Analisando: {label}")
                
                result = process_chat_optimized(pergunta, df)
                load_spot.empty()
                
                st.session_state.messages.append({"role": "user", "content": label})
                st.session_state.messages.append({"role": "assistant", "content": result["answer"], "time": result["time"]})
                st.rerun()
    
    st.markdown("---")
    
    # CONTAINER COM SCROLL
    st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.info("💡 Clique em um botão ou digite sua pergunta")
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and "time" in msg:
                    st.caption(f"⏱️ {msg['time']:.1f}s")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto-scroll
    st.markdown("""
    <script>
    var chatContainer = document.getElementById('chat-container');
    if(chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    </script>
    """, unsafe_allow_html=True)
    
    # INPUT
    if user_input := st.chat_input("💭 Digite..."):
        load_spot = st.empty()
        with load_spot:
            show_loading("Processando")
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        result = process_chat_optimized(user_input, df)
        load_spot.empty()
        
        st.session_state.messages.append({"role": "assistant", "content": result["answer"], "time": result["time"]})
        st.rerun()

st.markdown("---")
st.caption("Base Mobile 2026 | Gestão de Licenças")
