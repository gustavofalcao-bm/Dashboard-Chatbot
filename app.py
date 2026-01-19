import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import warnings
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

# ==================== CSS PROFISSIONAL ====================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    
    .stApp {{ background: linear-gradient(135deg, #f5f7fa 0%, #e8ecef 100%); }}
    
    /* SIDEBAR COM ÍCONES VISÍVEIS */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['secondary']} 0%, {COLORS['accent']} 50%, #2ecc71 100%) !important;
        box-shadow: 5px 0 20px rgba(0,0,0,0.1);
    }}
    
    [data-testid="stSidebar"] * {{ 
        color: white !important; 
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }}
    
    [data-testid="stSidebar"] .stButton>button {{
        background: rgba(255,255,255,0.25) !important;
        border: 2px solid white !important;
        color: white !important;
        font-weight: 700;
        transition: all 0.3s;
        backdrop-filter: blur(10px);
    }}
    
    [data-testid="stSidebar"] .stButton>button:hover {{
        background: white !important;
        color: {COLORS['accent']} !important;
        transform: translateX(5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }}
    
    /* ÍCONES COM CONTRASTE */
    [data-testid="stSidebar"] .stMarkdown {{
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }}
    
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
    
    /* CHAT OTIMIZADO - SEM CAIXA BRANCA */
    .chat-container {{
        max-height: 600px;
        overflow-y: auto !important;
        padding: 0;
        background: transparent;
        margin-bottom: 1.5rem;
    }}
    
    .chat-container::-webkit-scrollbar {{ width: 14px; }}
    .chat-container::-webkit-scrollbar-track {{ background: {COLORS['light']}; border-radius: 10px; }}
    .chat-container::-webkit-scrollbar-thumb {{ 
        background: linear-gradient(180deg, {COLORS['secondary']}, {COLORS['accent']}); 
        border-radius: 10px;
    }}
    
    /* Mensagens com estilo limpo */
    .stChatMessage {{
        background: white !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        border-left: 4px solid {COLORS['secondary']} !important;
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

# ==================== NORMALIZAÇÃO DE OPERADORAS ====================

def normalizar_operadora(operadora):
    """
    Normaliza operadoras:
    - CLARO, Claro → CLARO
    - ALGAR VIVO, ALGAR TIM → ALGAR
    - Pega só primeira palavra em maiúsculo
    """
    if pd.isna(operadora):
        return "NÃO INFORMADO"
    
    op = str(operadora).strip().upper().split()[0]
    
    mapeamento = {
        'CLAROTIM': 'CLARO',
        'VIVOTIM': 'VIVO',
        'TIMCLARO': 'TIM'
    }
    
    return mapeamento.get(op, op)

# ==================== CARREGAMENTO ULTRA OTIMIZADO ====================

@st.cache_data(ttl=7200, show_spinner=False)
def load_excel_optimized():
    """Carregamento otimizado com normalização"""
    try:
        excel_path = Path("MAPEAMENTO DE CHIPS.xlsx")
        if not excel_path.exists():
            return pd.DataFrame()
        
        cols_needed = [
            'PROJETO', 'OPERADORA', 
            'DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO'
        ]
        
        all_sheets = pd.read_excel(
            excel_path, 
            sheet_name=None, 
            engine='openpyxl',
            usecols=lambda x: x.strip().upper() in cols_needed if isinstance(x, str) else False
        )
        
        dfs = []
        for sheet_name, df in all_sheets.items():
            df.columns = df.columns.str.strip().str.upper()
            
            if 'PROJETO' not in df.columns:
                df['PROJETO'] = sheet_name
            
            dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        df_completo = pd.concat(dfs, ignore_index=True)
        
        if 'OPERADORA' in df_completo.columns:
            df_completo['OPERADORA'] = df_completo['OPERADORA'].apply(normalizar_operadora)
        
        date_cols = ['DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO']
        for col in date_cols:
            if col in df_completo.columns:
                df_completo[col] = pd.to_datetime(df_completo[col], errors='coerce', format='mixed')
        
        return df_completo
    
    except Exception as e:
        st.error(f"Erro: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=7200, show_spinner=False)
def calcular_metricas_rapido(total_rows, df_hash):
    """Métricas rápidas"""
    df = st.session_state.df_loaded
    
    hoje = pd.Timestamp.now().normalize()
    df_com_venc = df[df['DATA DE VENCIMENTO'].notna()]
    
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
    """Dados agregados + novos gráficos - VERSÃO CORRIGIDA"""
    df = st.session_state.df_loaded
    
    # Operadoras
    df_op = df['OPERADORA'].value_counts().reset_index()
    df_op.columns = ['Operadora', 'Qtd']
    
    # Projetos
    df_proj = df['PROJETO'].value_counts().head(10).reset_index()
    df_proj.columns = ['Projeto', 'Qtd']
    
    # Vencimentos
    hoje = pd.Timestamp.now().normalize()
    df_venc = df[df['DATA DE VENCIMENTO'].notna()].copy()
    df_venc_validos = df_venc[df_venc['DATA DE VENCIMENTO'] > hoje]
    
    if not df_venc_validos.empty:
        df_venc_validos['dias'] = (df_venc_validos['DATA DE VENCIMENTO'] - hoje).dt.days
        bins = [0, 30, 90, 180, 365, float('inf')]
        labels = ['0-30 dias', '31-90 dias', '91-180 dias', '181-365 dias', '+1 ano']
        df_venc_validos['categoria'] = pd.cut(df_venc_validos['dias'], bins=bins, labels=labels, right=False)
        venc_cat = df_venc_validos['categoria'].value_counts().reindex(labels, fill_value=0)
    else:
        labels = ['0-30 dias', '31-90 dias', '91-180 dias', '181-365 dias', '+1 ano']
        venc_cat = pd.Series([0]*5, index=labels)
    
    # Timeline
    if not df_venc_validos.empty:
        prox_ano = hoje + pd.DateOffset(months=12)
        df_prox = df_venc_validos[df_venc_validos['DATA DE VENCIMENTO'] <= prox_ano]
        df_prox['mes'] = df_prox['DATA DE VENCIMENTO'].dt.to_period('M')
        venc_mensal = df_prox.groupby('mes').size().reset_index(name='Quantidade')
        venc_mensal['mes'] = venc_mensal['mes'].dt.to_timestamp()
    else:
        venc_mensal = pd.DataFrame(columns=['mes', 'Quantidade'])
    
    # CORRIGIDO: Taxa de ocupação por operadora
    total_geral = len(df)
    df_ocup = df.groupby('OPERADORA').size().reset_index(name='Total')
    df_ocup['Percentual'] = (df_ocup['Total'] / total_geral * 100).round(1)
    df_ocup = df_ocup.sort_values('Total', ascending=False)
    
    # CORRIGIDO: Crescimento temporal
    if 'DATA DE ATIVAÇÃO' in df.columns:
        df_ativ = df[df['DATA DE ATIVAÇÃO'].notna()].copy()
        if not df_ativ.empty:
            df_ativ['mes_ativ'] = df_ativ['DATA DE ATIVAÇÃO'].dt.to_period('M')
            cresc_mensal = df_ativ.groupby('mes_ativ').size().reset_index(name='Ativações')
            cresc_mensal['mes_ativ'] = cresc_mensal['mes_ativ'].dt.to_timestamp()
            cresc_mensal = cresc_mensal.sort_values('mes_ativ').tail(12)
        else:
            cresc_mensal = pd.DataFrame(columns=['mes_ativ', 'Ativações'])
    else:
        cresc_mensal = pd.DataFrame(columns=['mes_ativ', 'Ativações'])
    
    return {
        'operadoras': df_op,
        'projetos': df_proj,
        'venc_categorias': venc_cat,
        'venc_mensal': venc_mensal,
        'ocupacao': df_ocup,
        'crescimento': cresc_mensal
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

# ==================== CHATBOT COM TABELAS ====================

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'df_loaded' not in st.session_state:
    st.session_state.df_loaded = None
if 'llm_initialized' not in st.session_state:
    st.session_state.llm_initialized = None

@st.cache_resource(show_spinner=False)
def init_llm_optimized():
    """LLM Groq otimizado"""
    try:
        from langchain_groq import ChatGroq
        
        api_key = st.secrets["GROQ_API_KEY"]
        
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=400,
            timeout=60,
            groq_api_key=api_key
        )
        
    except Exception as e:
        st.error(f"❌ Erro Groq: {e}")
        return None

def gerar_contexto_gerencial(df):
    """Gera contexto gerencial estruturado"""
    hoje = datetime.now()
    
    total = len(df)
    df_venc = df[df['DATA DE VENCIMENTO'].notna()]
    validas = len(df_venc[df_venc['DATA DE VENCIMENTO'] > hoje])
    expiradas = len(df_venc[df_venc['DATA DE VENCIMENTO'] <= hoje])
    
    top_op = df['OPERADORA'].value_counts().head(5).to_dict()
    top_proj = df['PROJETO'].value_counts().head(5).to_dict()
    
    df_venc_fut = df_venc[df_venc['DATA DE VENCIMENTO'] > hoje]
    prox_30d = len(df_venc_fut[df_venc_fut['DATA DE VENCIMENTO'] <= hoje + timedelta(days=30)])
    prox_90d = len(df_venc_fut[df_venc_fut['DATA DE VENCIMENTO'] <= hoje + timedelta(days=90)])
    
    taxa_validas = (validas / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'validas': validas,
        'expiradas': expiradas,
        'prox_30d': prox_30d,
        'prox_90d': prox_90d,
        'taxa_validas': taxa_validas,
        'top_operadoras': top_op,
        'top_projetos': top_proj
    }

def process_chat_gerencial(question, df):
    """Chat com respostas gerenciais (tabelas e matrizes)"""
    if df is None or df.empty:
        return {"answer": "❌ Dados não disponíveis.", "time": 0}
    
    ctx = gerar_contexto_gerencial(df)
    
    contexto = f"""
Você é um ANALISTA SÊNIOR DE GESTÃO DE LICENÇAS da Base Mobile.

DADOS CONSOLIDADOS:
- Total de Licenças: {ctx['total']:,}
- Licenças Válidas: {ctx['validas']:,} ({ctx['taxa_validas']:.1f}%)
- Licenças Expiradas: {ctx['expiradas']:,}
- Expirando em 30 dias: {ctx['prox_30d']:,}
- Expirando em 90 dias: {ctx['prox_90d']:,}

TOP 5 OPERADORAS:
{ctx['top_operadoras']}

TOP 5 PROJETOS:
{ctx['top_projetos']}

PERGUNTA DO EXECUTIVO: {question}

INSTRUÇÕES PARA RESPOSTA:
1. Seja DIRETO e EXECUTIVO (máximo 300 palavras)
2. Use formatação Markdown SEMPRE (negrito, listas, tabelas)
3. Quando apresentar dados de projetos/operadoras, use TABELAS Markdown
4. Destaque RISCOS em **negrito** e OPORTUNIDADES em *itálico*
5. Termine com 2-3 RECOMENDAÇÕES PRÁTICAS
6. Use números e % para embasar análises

FORMATO DE TABELA ESPERADO:
| Projeto | Licenças | Status |
|---------|----------|--------|
| Projeto A | 10.000 | ⚠️ Crítico |

Responda em português brasileiro, como se estivesse em uma reunião de diretoria.
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
        <div style="text-align: center; padding: 1.2rem; background: rgba(255,255,255,0.2); border-radius: 15px; margin-bottom: 1.5rem; backdrop-filter: blur(10px);">
            <img src="data:image/png;base64,{logo_icon}" style="max-width: 90px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));">
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
        
        df_exp = df[df['DATA DE VENCIMENTO'].notna()]
        df_exp = df_exp[(df_exp['DATA DE VENCIMENTO'] > hoje) & (df_exp['DATA DE VENCIMENTO'] <= hoje + timedelta(days=30))]
        
        if not df_exp.empty:
            excel_exp = export_to_excel(df_exp.head(10000), "expirando.xlsx")
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
    
    if st.session_state.llm_initialized is None:
        st.session_state.llm_initialized = init_llm_optimized()
    
    loading_placeholder.empty()

df = st.session_state.df_loaded

if df.empty:
    st.error("❌ Erro ao carregar dados")
    st.stop()

st.success(f"✅ **{len(df):,} licenças** de **{df['PROJETO'].nunique()} projetos** | **{df['OPERADORA'].nunique()} operadoras**".replace(',', '.'))
st.markdown("---")

# ==================== TABS ====================
tab1, tab2 = st.tabs(["📊 Dashboard Executivo", "💬 Assistente IA"])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    st.markdown("### 🎯 Indicadores Principais")
    
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
    st.markdown("### 📊 Análises Estratégicas")
    
    dados_graficos = agregrar_dados_graficos(df_hash)
    
    # LINHA 1
    col1, col2 = st.columns(2)
    
    with col1:
        df_op = dados_graficos['operadoras']
        
        color_map = {'CLARO': COLORS['claro'], 'VIVO': COLORS['vivo'], 'TIM': COLORS['tim'], 'OI': COLORS['oi'], 'ALGAR': COLORS['algar']}
        colors_list = [color_map.get(op, COLORS['secondary']) for op in df_op['Operadora']]
        
        fig = go.Figure(data=[go.Pie(
            labels=df_op['Operadora'],
            values=df_op['Qtd'],
            hole=0.5,
            marker=dict(colors=colors_list, line=dict(color='white', width=4)),
            textfont=dict(size=16, family='Inter', color='white'),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Licenças: %{value:,}<br>%{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text="<b>Distribuição por Operadora</b>", font=dict(size=20, family='Inter', color=COLORS['primary']), x=0.5, xanchor='center'),
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=12)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=60, b=80)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        df_proj = dados_graficos['projetos']
        
        fig = go.Figure(data=[go.Bar(
            x=df_proj['Qtd'],
            y=df_proj['Projeto'],
            orientation='h',
            marker=dict(
                color=df_proj['Qtd'],
                colorscale=[[0, COLORS['accent']], [1, COLORS['primary']]],
                line=dict(color='white', width=2)
            ),
            text=df_proj['Qtd'].apply(lambda x: f"{x:,}".replace(',', '.')),
            textposition='outside',
            textfont=dict(size=14, family='Inter', color=COLORS['primary']),
            hovertemplate='<b>%{y}</b><br>Licenças: %{x:,}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text="<b>Top 10 Projetos</b>", font=dict(size=20, family='Inter', color=COLORS['primary']), x=0.5, xanchor='center'),
            height=400,
            yaxis=dict(categoryorder='total ascending', tickfont=dict(size=11, color=COLORS['primary'])),
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=50, t=60, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # LINHA 2
    col1, col2 = st.columns(2)
    
    with col1:
        venc_cat = dados_graficos['venc_categorias']
        labels = venc_cat.index.tolist()
        colors_v = [COLORS['danger'], COLORS['warning'], COLORS['info'], COLORS['accent'], COLORS['secondary']]
        
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=venc_cat.values,
            marker=dict(color=colors_v, line=dict(color='white', width=2)),
            text=venc_cat.values,
            textposition='outside',
            textfont=dict(size=16, family='Inter', color=COLORS['primary']),
            hovertemplate='<b>%{x}</b><br>Licenças: %{y:,}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text="<b>Vencimentos por Período</b>", font=dict(size=20, family='Inter', color=COLORS['primary']), x=0.5, xanchor='center'),
            height=400,
            xaxis=dict(tickfont=dict(size=11, color=COLORS['primary'])),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=40, t=60, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        venc_mensal = dados_graficos['venc_mensal']
        
        if not venc_mensal.empty:
            fig = go.Figure(data=[go.Scatter(
                x=venc_mensal['mes'],
                y=venc_mensal['Quantidade'],
                mode='lines+markers',
                line=dict(color=COLORS['danger'], width=4),
                marker=dict(size=12, color=COLORS['danger'], line=dict(color='white', width=2)),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.1)',
                hovertemplate='<b>%{x|%b/%Y}</b><br>Vencimentos: %{y:,}<extra></extra>'
            )])
            
            fig.update_layout(
                title=dict(text="<b>Timeline - Próximos 12 Meses</b>", font=dict(size=20, family='Inter', color=COLORS['primary']), x=0.5, xanchor='center'),
                height=400,
                xaxis=dict(tickfont=dict(size=11), showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=50, r=40, t=60, b=60)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # LINHA 3
    col1, col2 = st.columns(2)
    
    with col1:
        df_ocup = dados_graficos['ocupacao']
        
        fig = go.Figure(data=[go.Bar(
            x=df_ocup['Operadora'],
            y=df_ocup['Percentual'],
            marker=dict(
                color=df_ocup['Percentual'],
                colorscale=[[0, COLORS['info']], [1, COLORS['accent']]],
                line=dict(color='white', width=2)
            ),
            text=df_ocup['Percentual'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside',
            textfont=dict(size=14, family='Inter', color=COLORS['primary']),
            hovertemplate='<b>%{x}</b><br>Ocupação: %{y:.1f}%<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text="<b>Taxa de Ocupação por Operadora</b>", font=dict(size=20, family='Inter', color=COLORS['primary']), x=0.5, xanchor='center'),
            height=400,
            xaxis=dict(tickfont=dict(size=11, color=COLORS['primary'])),
            yaxis=dict(title="Percentual (%)", showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=60, r=40, t=60, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        cresc_mensal = dados_graficos['crescimento']
        
        if not cresc_mensal.empty:
            fig = go.Figure(data=[go.Bar(
                x=cresc_mensal['mes_ativ'],
                y=cresc_mensal['Ativações'],
                marker=dict(color=COLORS['accent'], line=dict(color='white', width=2)),
                text=cresc_mensal['Ativações'],
                textposition='outside',
                textfont=dict(size=14, family='Inter', color=COLORS['primary']),
                hovertemplate='<b>%{x|%b/%Y}</b><br>Ativações: %{y:,}<extra></extra>'
            )])
            
            fig.update_layout(
                title=dict(text="<b>Ativações Mensais - Últimos 12 Meses</b>", font=dict(size=20, family='Inter', color=COLORS['primary']), x=0.5, xanchor='center'),
                height=400,
                xaxis=dict(tickfont=dict(size=11)),
                yaxis=dict(title="Ativações", showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=60, r=40, t=60, b=60)
            )
            
            st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 2: CHAT ====================
with tab2:
    st.markdown("### 💬 Assistente Executivo IA")
    st.caption("Análises estratégicas com tabelas e recomendações práticas")
    
    perguntas = {
        "📊 Resumo Executivo": "Forneça um resumo executivo completo com tabela dos principais projetos, métricas consolidadas e insights estratégicos",
        "⚠️ Análise de Riscos": "Identifique os principais riscos operacionais com tabela de criticidade e recomendações urgentes",
        "📈 Performance Operadoras": "Analise a performance por operadora com tabela comparativa e oportunidades de otimização",
        "🏆 Ranking Projetos": "Crie ranking dos projetos com tabela de saúde operacional e ações recomendadas",
        "📅 Gestão Vencimentos": "Análise detalhada dos vencimentos com tabela de prioridades e plano de ação",
        "💡 Plano de Ação": "Monte um plano de ação executivo com tabela de prioridades e responsabilidades"
    }
    
    cols = st.columns(3)
    for idx, (label, pergunta) in enumerate(perguntas.items()):
        with cols[idx % 3]:
            if st.button(label, key=f"btn_{idx}", use_container_width=True):
                load_spot = st.empty()
                with load_spot:
                    show_loading("Gerando análise")
                
                result = process_chat_gerencial(pergunta, df)
                load_spot.empty()
                
                st.session_state.messages.insert(0, {"role": "assistant", "content": result["answer"], "time": result["time"]})
                st.session_state.messages.insert(0, {"role": "user", "content": label})
                st.rerun()
    
    st.markdown("---")
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        st.info("💡 **Dica:** Clique em um botão acima para análises estratégicas ou digite perguntas personalizadas")
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])
                if msg["role"] == "assistant" and "time" in msg:
                    st.caption(f"⏱️ {msg['time']:.1f}s | 🤖 Groq AI | 📊 Análise Gerencial")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if user_input := st.chat_input("💭 Digite sua pergunta executiva..."):
        load_spot = st.empty()
        with load_spot:
            show_loading("Processando")
        
        result = process_chat_gerencial(user_input, df)
        load_spot.empty()
        
        st.session_state.messages.insert(0, {"role": "assistant", "content": result["answer"], "time": result["time"]})
        st.session_state.messages.insert(0, {"role": "user", "content": user_input})
        st.rerun()

st.markdown("---")
st.caption("Base Mobile 2026 | Sistema Enterprise de Gestão de Licenças | Powered by Groq AI")
