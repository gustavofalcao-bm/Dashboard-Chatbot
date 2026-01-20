import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import warnings
import base64
import io
import hashlib

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

# ==================== PALETA PREMIUM ====================
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#8BC34A',
    'accent': '#4CAF50',
    'dark_green': '#2E7D32',
    'light_green': '#C5E1A5',
    'warning': '#FFB74D',
    'danger': '#E57373',
    'info': '#64B5F6',
    'light': '#FAFAFA',
    'gray': '#BDBDBD',
    'dark_gray': '#616161',
    'white': '#FFFFFF',
    'claro': '#FF5252',
    'vivo': '#7B1FA2',
    'tim': '#1976D2',
    'oi': '#FDD835',
    'algar': '#00C853'
}

# ==================== CSS PREMIUM 4.0 ====================
st.markdown(f"""
<style>
    /* FONTS & RESET */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* BACKGROUND */
    .stApp {{
        background: linear-gradient(135deg, #F8F9FA 0%, #E8EEF2 100%);
    }}
    
    /* SIDEBAR PREMIUM */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['secondary']} 0%, {COLORS['accent']} 60%, {COLORS['dark_green']} 100%) !important;
        box-shadow: 4px 0 30px rgba(0,0,0,0.12);
        border-right: 1px solid rgba(255,255,255,0.1);
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    [data-testid="stSidebar"] .stButton>button {{
        background: rgba(255,255,255,0.15) !important;
        border: 2px solid rgba(255,255,255,0.4) !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem !important;
    }}
    
    [data-testid="stSidebar"] .stButton>button:hover {{
        background: white !important;
        color: {COLORS['accent']} !important;
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: white !important;
    }}
    
    [data-testid="stSidebar"] .stButton>button:active {{
        transform: translateY(0) scale(0.98);
    }}
    
    /* HEADER PREMIUM */
    .header-container {{
        background: linear-gradient(135deg, rgba(44, 62, 80, 0.97), rgba(52, 73, 94, 0.97));
        padding: 2rem 3rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }}
    
    .header-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent 30%, rgba(139, 195, 74, 0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }}
    
    @keyframes shimmer {{
        0%, 100% {{ transform: translateX(-100%); }}
        50% {{ transform: translateX(100%); }}
    }}
    
    .header-logo {{
        background: white;
        padding: 1.2rem 1.8rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        display: inline-block;
    }}
    
    .header-title {{
        color: white;
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }}
    
    .header-subtitle {{
        color: {COLORS['secondary']};
        font-size: 1.15rem;
        margin: 0.5rem 0 0 0;
        font-weight: 600;
        position: relative;
        z-index: 1;
    }}
    
    /* METRIC CARDS PREMIUM */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .metric-card {{
        background: white;
        padding: 1.8rem 2rem;
        border-radius: 18px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.04);
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
        animation-fill-mode: both;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 5px;
        background: linear-gradient(180deg, {COLORS['secondary']}, {COLORS['dark_green']});
        border-radius: 18px 0 0 18px;
    }}
    
    .metric-card::after {{
        content: '';
        position: absolute;
        right: -50px;
        top: -50px;
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, rgba(139, 195, 74, 0.08) 0%, transparent 70%);
        border-radius: 50%;
    }}
    
    .metric-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 40px rgba(139, 195, 74, 0.25);
        border-color: {COLORS['secondary']};
    }}
    
    .metric-icon {{
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
        opacity: 0.9;
        display: inline-block;
        transition: transform 0.3s ease;
    }}
    
    .metric-card:hover .metric-icon {{
        transform: scale(1.15) rotate(5deg);
    }}
    
    .metric-value {{
        font-size: 2.8rem;
        font-weight: 900;
        color: {COLORS['primary']};
        line-height: 1;
        margin: 1rem 0 0.5rem 0;
        position: relative;
        z-index: 1;
    }}
    
    .metric-label {{
        font-size: 0.8rem;
        color: {COLORS['dark_gray']};
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
        position: relative;
        z-index: 1;
    }}
    
    .metric-change {{
        font-size: 0.85rem;
        margin-top: 0.5rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: 600;
    }}
    
    .metric-change.positive {{
        background: rgba(76, 175, 80, 0.1);
        color: {COLORS['accent']};
    }}
    
    .metric-change.negative {{
        background: rgba(229, 115, 115, 0.1);
        color: {COLORS['danger']};
    }}
    
    /* CHART CONTAINERS */
    .chart-container {{
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 6px 30px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.03);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }}
    
    .chart-container:hover {{
        box-shadow: 0 10px 45px rgba(0,0,0,0.12);
        transform: translateY(-4px);
    }}
    
    .chart-title {{
        font-size: 1.4rem;
        font-weight: 800;
        color: {COLORS['primary']};
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid {COLORS['light']};
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }}
    
    .chart-title i {{
        color: {COLORS['secondary']};
        font-size: 1.6rem;
    }}
    
    /* TABS PREMIUM */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin-bottom: 2rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 60px;
        padding: 0 2.5rem;
        border-radius: 14px;
        color: {COLORS['dark_gray']};
        font-weight: 700;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        background: transparent;
        border: 2px solid transparent;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(139, 195, 74, 0.08);
        border-color: {COLORS['light_green']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent']}) !important;
        color: white !important;
        border-color: {COLORS['dark_green']} !important;
        box-shadow: 0 4px 15px rgba(139, 195, 74, 0.3);
    }}
    
    /* LOADING STATE */
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    .skeleton {{
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: 12px;
    }}
    
    @keyframes loading {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    
    /* SCROLLBAR */
    ::-webkit-scrollbar {{
        width: 12px;
        height: 12px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {COLORS['light']};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {COLORS['secondary']}, {COLORS['accent']});
        border-radius: 10px;
        border: 2px solid {COLORS['light']};
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, {COLORS['accent']}, {COLORS['dark_green']});
    }}
    
    /* UTILITIES */
    .text-center {{ text-align: center; }}
    .mb-1 {{ margin-bottom: 0.5rem; }}
    .mb-2 {{ margin-bottom: 1rem; }}
    .mb-3 {{ margin-bottom: 1.5rem; }}
    .mb-4 {{ margin-bottom: 2rem; }}
    .mt-2 {{ margin-top: 1rem; }}
    .mt-3 {{ margin-top: 1.5rem; }}
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES AUXILIARES ====================

def show_loading(message="Carregando"):
    return st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; background: white; border-radius: 25px; box-shadow: 0 15px 50px rgba(0,0,0,0.08); margin: 3rem auto; max-width: 600px;">
        <div style="width: 90px; height: 90px; border: 8px solid {COLORS['light']}; border-top-color: {COLORS['secondary']}; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 2rem;"></div>
        <div style="color: {COLORS['primary']}; font-size: 1.5rem; font-weight: 800;">{message}...</div>
    </div>
    <style>
    @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    </style>
    """, unsafe_allow_html=True)

def normalizar_operadora(operadora):
    if pd.isna(operadora):
        return "NÃO INFORMADO"
    op = str(operadora).strip().upper().split()[0]
    mapeamento = {'CLAROTIM': 'CLARO', 'VIVOTIM': 'VIVO', 'TIMCLARO': 'TIM'}
    return mapeamento.get(op, op)

# ==================== CARREGAMENTO ====================

@st.cache_data(ttl=7200, show_spinner=False)
def load_excel_optimized(versao=4):
    """VERSÃO 4.0 PREMIUM"""
    try:
        excel_path = Path("MAPEAMENTO DE CHIPS.xlsx")
        if not excel_path.exists():
            return pd.DataFrame()
        
        cols_needed = [
            'PROJETO', 'ICCID', 'OPERADORA', 
            'DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO',
            'ÚLTIMA CONEXÃO', 'STATUS NA OP.'
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
        
        date_cols = ['DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO', 'ÚLTIMA CONEXÃO']
        for col in date_cols:
            if col in df_completo.columns:
                df_completo[col] = pd.to_datetime(df_completo[col], errors='coerce', format='mixed')
        
        hoje = pd.Timestamp.now().normalize()
        if 'DATA DE VENCIMENTO' in df_completo.columns:
            df_completo['STATUS_LICENCA'] = df_completo['DATA DE VENCIMENTO'].apply(
                lambda x: 'Expirado' if pd.notna(x) and x < hoje else 'Válido'
            )
        
        if 'ÚLTIMA CONEXÃO' in df_completo.columns:
            def categorizar_conexao(data_conexao):
                if pd.isna(data_conexao):
                    return 'Nunca Conectou'
                dias = (hoje - data_conexao).days
                if dias <= 30:
                    return '0-30 dias'
                elif dias <= 90:
                    return '31-90 dias'
                elif dias <= 180:
                    return '91-180 dias'
                else:
                    return 'Mais de 180 dias'
            
            df_completo['CATEGORIA_CONEXAO'] = df_completo['ÚLTIMA CONEXÃO'].apply(categorizar_conexao)
        
        if 'STATUS NA OP.' in df_completo.columns:
            df_completo['STATUS NA OP.'] = df_completo['STATUS NA OP.'].astype(str).str.strip().str.title()
        
        return df_completo
    
    except Exception as e:
        st.error(f"Erro: {e}")
        import traceback
        st.code(traceback.format_exc())
        return pd.DataFrame()

@st.cache_data(ttl=7200, show_spinner=False)
def calcular_metricas_rapido(total_rows, df_hash):
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
def agregar_dados_graficos(df_hash, filtros_hash, versao=4):
    """VERSÃO 4.0 PREMIUM com filtros"""
    df = st.session_state.df_loaded
    
    filtros = st.session_state.get('filtros_ativos', {})
    df_filtrado = df.copy()
    
    if filtros.get('projetos'):
        df_filtrado = df_filtrado[df_filtrado['PROJETO'].isin(filtros['projetos'])]
    
    if filtros.get('operadoras'):
        df_filtrado = df_filtrado[df_filtrado['OPERADORA'].isin(filtros['operadoras'])]
    
    if filtros.get('status_op'):
        df_filtrado = df_filtrado[df_filtrado['STATUS NA OP.'].isin(filtros['status_op'])]
    
    if filtros.get('status_licenca'):
        df_filtrado = df_filtrado[df_filtrado['STATUS_LICENCA'].isin(filtros['status_licenca'])]
    
    df_op = df_filtrado['OPERADORA'].value_counts().reset_index()
    df_op.columns = ['Operadora', 'Qtd']
    
    df_proj = df_filtrado['PROJETO'].value_counts().head(10).reset_index()
    df_proj.columns = ['Projeto', 'Qtd']
    
    hoje = pd.Timestamp.now().normalize()
    df_venc = df_filtrado[df_filtrado['DATA DE VENCIMENTO'].notna()].copy()
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
    
    if not df_venc_validos.empty:
        prox_ano = hoje + pd.DateOffset(months=12)
        df_prox = df_venc_validos[df_venc_validos['DATA DE VENCIMENTO'] <= prox_ano]
        df_prox['mes'] = df_prox['DATA DE VENCIMENTO'].dt.to_period('M')
        venc_mensal = df_prox.groupby('mes').size().reset_index(name='Quantidade')
        venc_mensal['mes'] = venc_mensal['mes'].dt.to_timestamp()
    else:
        venc_mensal = pd.DataFrame(columns=['mes', 'Quantidade'])
    
    if 'CATEGORIA_CONEXAO' in df_filtrado.columns:
        df_conexao = df_filtrado['CATEGORIA_CONEXAO'].value_counts().reset_index()
        df_conexao.columns = ['Categoria', 'Qtd']
    else:
        df_conexao = pd.DataFrame(columns=['Categoria', 'Qtd'])
    
    if 'STATUS NA OP.' in df_filtrado.columns:
        df_status_op = df_filtrado['STATUS NA OP.'].value_counts().reset_index()
        df_status_op.columns = ['Status', 'Qtd']
    else:
        df_status_op = pd.DataFrame(columns=['Status', 'Qtd'])
    
    if 'DATA DE ATIVAÇÃO' in df_filtrado.columns:
        df_ativ = df_filtrado[df_filtrado['DATA DE ATIVAÇÃO'].notna()].copy()
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
        'conexoes': df_conexao,
        'status_op': df_status_op,
        'crescimento': cresc_mensal
    }

def format_number(num):
    try:
        return f"{int(num):,}".replace(',', '.')
    except:
        return str(num)

# ==================== GRÁFICOS PREMIUM ====================

def criar_grafico_operadora_premium(dados):
    """Gráfico de Pizza Premium - Operadoras"""
    df = dados['operadoras']
    
    color_map = {
        'CLARO': COLORS['claro'],
        'VIVO': COLORS['vivo'],
        'TIM': COLORS['tim'],
        'OI': COLORS['oi'],
        'ALGAR': COLORS['algar']
    }
    colors_list = [color_map.get(op, COLORS['gray']) for op in df['Operadora']]
    
    fig = go.Figure(data=[go.Pie(
        labels=df['Operadora'],
        values=df['Qtd'],
        hole=0.55,
        marker=dict(
            colors=colors_list,
            line=dict(color='white', width=5)
        ),
        textfont=dict(size=15, family='Inter', color='white', weight=700),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b style="font-size:16px">%{label}</b><br>' +
                     '<span style="font-size:14px">Licenças: %{value:,.0f}</span><br>' +
                     '<span style="font-size:14px">Percentual: %{percent}</span>' +
                     '<extra></extra>',
        pull=[0.05 if i == 0 else 0 for i in range(len(df))]
    )])
    
    total = df['Qtd'].sum()
    fig.add_annotation(
        text=f'<b style="font-size:32px; color:{COLORS["primary"]}">{total:,.0f}</b><br>' +
             f'<span style="font-size:14px; color:{COLORS["dark_gray"]}">Total de Licenças</span>',
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(family='Inter')
    )
    
    fig.update_layout(
        title=None,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=13, family='Inter', color=COLORS['dark_gray']),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor=COLORS['light'],
            borderwidth=1
        ),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=100),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter",
            bordercolor=COLORS['light']
        )
    )
    
    return fig

def criar_grafico_conexoes_premium(dados):
    """Gráfico de Rosca Premium - Conexões"""
    df = dados['conexoes']
    
    if df.empty:
        return go.Figure()
    
    cores_conexao = {
        'Nunca Conectou': COLORS['danger'],
        'Mais de 180 dias': COLORS['warning'],
        '91-180 dias': COLORS['info'],
        '31-90 dias': COLORS['light_green'],
        '0-30 dias': COLORS['accent']
    }
    colors_list = [cores_conexao.get(cat, COLORS['gray']) for cat in df['Categoria']]
    
    fig = go.Figure(data=[go.Pie(
        labels=df['Categoria'],
        values=df['Qtd'],
        hole=0.6,
        marker=dict(
            colors=colors_list,
            line=dict(color='white', width=5)
        ),
        textfont=dict(size=14, family='Inter', color='white', weight=700),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b style="font-size:16px">%{label}</b><br>' +
                     '<span style="font-size:14px">Chips: %{value:,.0f}</span><br>' +
                     '<span style="font-size:14px">Percentual: %{percent}</span>' +
                     '<extra></extra>'
    )])
    
    total = df['Qtd'].sum()
    com_conexao = df[df['Categoria'] != 'Nunca Conectou']['Qtd'].sum()
    perc = (com_conexao / total * 100) if total > 0 else 0
    
    fig.add_annotation(
        text=f'<b style="font-size:30px; color:{COLORS["accent"]}">{com_conexao:,.0f}</b><br>' +
             f'<span style="font-size:16px; color:{COLORS["primary"]}">{perc:.1f}%</span><br>' +
             f'<span style="font-size:12px; color:{COLORS["dark_gray"]}">conectaram</span>',
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(family='Inter')
    )
    
    fig.update_layout(
        title=None,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=12, family='Inter', color=COLORS['dark_gray']),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor=COLORS['light'],
            borderwidth=1
        ),
        height=460,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=110),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter",
            bordercolor=COLORS['light']
        )
    )
    
    return fig

def criar_grafico_status_op_premium(dados):
    """Gráfico de Barras Premium - Status OP"""
    df = dados['status_op']
    
    if df.empty:
        return go.Figure()
    
    df = df.sort_values('Qtd', ascending=True)
    
    cores_status = {
        'Ativo': COLORS['accent'],
        'Bloqueado': COLORS['warning'],
        'Suspenso': COLORS['danger'],
        'Cancelado': COLORS['gray']
    }
    colors_list = [cores_status.get(s, COLORS['secondary']) for s in df['Status']]
    
    fig = go.Figure(data=[go.Bar(
        y=df['Status'],
        x=df['Qtd'],
        orientation='h',
        marker=dict(
            color=colors_list,
            line=dict(color='white', width=3),
            pattern_shape=""
        ),
        text=[f"<b>{q:,.0f}</b>".replace(',', '.') for q in df['Qtd']],
        textposition='outside',
        textfont=dict(size=14, family='Inter', color=COLORS['primary'], weight=700),
        hovertemplate='<b style="font-size:16px">%{y}</b><br>' +
                     '<span style="font-size:14px">Quantidade: %{x:,.0f}</span>' +
                     '<extra></extra>',
        width=0.7
    )])
    
    fig.update_layout(
        title=None,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.04)',
            gridwidth=1,
            showline=False,
            zeroline=False,
            tickfont=dict(size=12, family='Inter', color=COLORS['dark_gray'])
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            tickfont=dict(size=13, family='Inter', color=COLORS['primary'], weight=600)
        ),
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=120, r=80, t=20, b=40),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter",
            bordercolor=COLORS['light']
        )
    )
    
    return fig

def criar_grafico_vencimentos_premium(dados):
    """Gráfico de Área Premium - Vencimentos"""
    df = dados['venc_mensal']
    
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['mes'],
        y=df['Quantidade'],
        mode='lines+markers+text',
        fill='tozeroy',
        fillcolor=f'rgba(229, 115, 115, 0.15)',
        line=dict(color=COLORS['danger'], width=4, shape='spline'),
        marker=dict(
            size=12,
            color=COLORS['danger'],
            line=dict(color='white', width=3),
            symbol='circle'
        ),
        text=[f'<b>{q:,.0f}</b>'.replace(',', '.') if q > 0 else '' for q in df['Quantidade']],
        textposition='top center',
        textfont=dict(size=12, family='Inter', color=COLORS['danger'], weight=700),
        hovertemplate='<b style="font-size:16px">%{x|%B/%Y}</b><br>' +
                     '<span style="font-size:14px">Vencimentos: %{y:,.0f}</span>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title=None,
        xaxis=dict(
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor=COLORS['light'],
            tickfont=dict(size=11, family='Inter', color=COLORS['dark_gray']),
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.04)',
            gridwidth=1,
            showline=False,
            zeroline=False,
            tickfont=dict(size=11, family='Inter', color=COLORS['dark_gray'])
        ),
        height=420,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=40, t=40, b=80),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter",
            bordercolor=COLORS['light']
        )
    )
    
    return fig

def criar_grafico_projetos_premium(dados):
    """Gráfico de Barras Premium - Top Projetos"""
    df = dados['projetos']
    
    if df.empty:
        return go.Figure()
    
    df = df.sort_values('Qtd', ascending=True)
    
    fig = go.Figure(data=[go.Bar(
        y=df['Projeto'],
        x=df['Qtd'],
        orientation='h',
        marker=dict(
            color=df['Qtd'],
            colorscale=[[0, COLORS['light_green']], [0.5, COLORS['secondary']], [1, COLORS['dark_green']]],
            line=dict(color='white', width=3),
            showscale=False
        ),
        text=[f"<b>{q:,.0f}</b>".replace(',', '.') for q in df['Qtd']],
        textposition='outside',
        textfont=dict(size=13, family='Inter', color=COLORS['primary'], weight=700),
        hovertemplate='<b style="font-size:15px">%{y}</b><br>' +
                     '<span style="font-size:14px">Licenças: %{x:,.0f}</span>' +
                     '<extra></extra>',
        width=0.75
    )])
    
    fig.update_layout(
        title=None,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.04)',
            gridwidth=1,
            showline=False,
            zeroline=False,
            tickfont=dict(size=11, family='Inter', color=COLORS['dark_gray'])
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            tickfont=dict(size=11, family='Inter', color=COLORS['primary'], weight=500)
        ),
        height=480,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=180, r=100, t=20, b=40),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter",
            bordercolor=COLORS['light']
        )
    )
    
    return fig

# ==================== SESSION STATE ====================

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'df_loaded' not in st.session_state:
    st.session_state.df_loaded = None
if 'filtros_ativos' not in st.session_state:
    st.session_state.filtros_ativos = {}

# ==================== SIDEBAR ====================
with st.sidebar:
    if logo_icon:
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.15); border-radius: 20px; margin-bottom: 2rem; backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2);">
            <img src="data:image/png;base64,{logo_icon}" style="max-width: 100px; filter: drop-shadow(0 6px 12px rgba(0,0,0,0.4));">
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Gestão de Licenças")
    st.caption("Base Mobile 2026 • v4.0 Premium")
    st.markdown("---")
    
    # FILTROS
    st.markdown("### 🎯 Filtros Dinâmicos")
    
    if st.session_state.df_loaded is not None and not st.session_state.df_loaded.empty:
        df_temp = st.session_state.df_loaded
        
        projetos = st.multiselect("📍 Projetos", sorted(df_temp['PROJETO'].unique()), default=None)
        st.session_state.filtros_ativos['projetos'] = projetos
        
        operadoras = st.multiselect("📡 Operadoras", sorted(df_temp['OPERADORA'].unique()), default=None)
        st.session_state.filtros_ativos['operadoras'] = operadoras
        
        if 'STATUS NA OP.' in df_temp.columns:
            status_op = st.multiselect("🔌 Status na OP", sorted(df_temp['STATUS NA OP.'].unique()), default=None)
            st.session_state.filtros_ativos['status_op'] = status_op
        
        if 'STATUS_LICENCA' in df_temp.columns:
            status_lic = st.multiselect("✅ Status Licença", ['Válido', 'Expirado'], default=None)
            st.session_state.filtros_ativos['status_licenca'] = status_lic
        
        # Contador de filtros ativos
        total_filtros = sum(1 for v in st.session_state.filtros_ativos.values() if v)
        if total_filtros > 0:
            st.info(f"🎯 **{total_filtros} filtro(s) ativo(s)**")
        
        if st.button("🔄 Limpar Filtros", use_container_width=True):
            st.session_state.filtros_ativos = {}
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 🎛️ Ações Rápidas")
    
    if st.button("🔄 Recarregar Dados", key="reload", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state.clear()
        st.rerun()

# ==================== HEADER ====================
st.markdown(f"""
<div class="header-container">
    <div style="display: flex; align-items: center; gap: 2rem;">
        <div class="header-logo">
            {f'<img src="data:image/png;base64,{logo_full}" style="max-height: 55px;">' if logo_full else '<div style="font-size: 2rem; font-weight: 900; color: ' + COLORS['accent'] + ';">BASE MOBILE</div>'}
        </div>
        <div>
            <h1 class="header-title">Dashboard Gerencial de Licenças</h1>
            <p class="header-subtitle">Sistema Enterprise 4.0 Premium | Analytics & Intelligence</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== CARREGAMENTO ====================
if st.session_state.df_loaded is None:
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        show_loading("Processando base de dados")
    
    st.session_state.df_loaded = load_excel_optimized(versao=4)
    loading_placeholder.empty()

df = st.session_state.df_loaded

if df.empty:
    st.error("❌ Erro ao carregar dados")
    st.stop()

st.success(f"✅ **{len(df):,} licenças** carregadas | **{df['PROJETO'].nunique()} projetos** | **{df['OPERADORA'].nunique()} operadoras**".replace(',', '.'))
st.markdown("---")

# ==================== TABS ====================
tab1, tab2 = st.tabs(["📊 Dashboard Executivo", "💬 Assistente IA"])

with tab1:
    st.markdown("### 🎯 Indicadores Estratégicos")
    
    df_hash = hashlib.md5(str(len(df)).encode()).hexdigest()
    filtros_hash = hashlib.md5(str(st.session_state.filtros_ativos).encode()).hexdigest()
    metricas = calcular_metricas_rapido(len(df), df_hash)
    
    # CARDS DE MÉTRICAS
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    cards = [
        (col1, "📋", "Total de Licenças", metricas['total'], COLORS['secondary'], 0),
        (col2, "🔗", "Vinculadas", metricas['vinculadas'], COLORS['secondary'], 0.1),
        (col3, "📊", "Taxa Vinculação", f"{metricas['perc_vinculadas']:.0f}%", COLORS['info'], 0.2),
        (col4, "💼", "Saldo Disponível", metricas['saldo'], COLORS['accent'], 0.3),
        (col5, "✅", "Licenças Válidas", metricas['validas'], COLORS['accent'], 0.4),
        (col6, "❌", "Licenças Expiradas", metricas['expiradas'], COLORS['danger'], 0.5)
    ]
    
    for col, icon, label, value, color, delay in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card" style="animation-delay: {delay}s;">
                <div class="metric-icon" style="color: {color};">{icon}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color: {color};">{format_number(value) if isinstance(value, (int, float)) else value}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div class='mb-4'></div>", unsafe_allow_html=True)
    
    # GRÁFICOS
    st.markdown("### 📊 Análises Visuais")
    
    dados_graficos = agregar_dados_graficos(df_hash, filtros_hash, versao=4)
    
    # LINHA 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title"><i class="fas fa-chart-pie"></i> Distribuição por Operadora</div>
        """, unsafe_allow_html=True)
        fig_op = criar_grafico_operadora_premium(dados_graficos)
        st.plotly_chart(fig_op, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title"><i class="fas fa-signal"></i> Análise de Conexões</div>
        """, unsafe_allow_html=True)
        fig_conexao = criar_grafico_conexoes_premium(dados_graficos)
        st.plotly_chart(fig_conexao, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
    
    # LINHA 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title"><i class="fas fa-server"></i> Status nas Operadoras</div>
        """, unsafe_allow_html=True)
        fig_status = criar_grafico_status_op_premium(dados_graficos)
        st.plotly_chart(fig_status, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title"><i class="fas fa-building"></i> Top 10 Projetos</div>
        """, unsafe_allow_html=True)
        fig_proj = criar_grafico_projetos_premium(dados_graficos)
        st.plotly_chart(fig_proj, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
    
    # LINHA 3
    st.markdown("""
    <div class="chart-container">
        <div class="chart-title"><i class="fas fa-calendar-alt"></i> Timeline de Vencimentos (Próximos 12 Meses)</div>
    """, unsafe_allow_html=True)
    fig_venc = criar_grafico_vencimentos_premium(dados_graficos)
    st.plotly_chart(fig_venc, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.info("💬 **Assistente IA** - Em desenvolvimento para v4.1")

st.markdown("---")
st.caption("© 2026 Base Mobile | Dashboard Enterprise v4.0 Premium | Powered by Streamlit & Plotly")
