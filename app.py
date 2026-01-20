import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import warnings
import base64
import io
import hashlib
import os
from groq import Groq

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Base Mobile | Gestão de Licenças",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CONFIGURAÇÃO GROQ ====================

def get_groq_client():
    """Inicializa cliente Groq com API key"""
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not api_key:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Erro ao conectar com Groq: {e}")
        return None

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

# ==================== CSS PREMIUM 5.1 ====================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #F8F9FA 0%, #E8EEF2 100%);
    }}
    
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
    
    .text-center {{ text-align: center; }}
    .mb-2 {{ margin-bottom: 1rem; }}
    .mb-3 {{ margin-bottom: 1.5rem; }}
    .mb-4 {{ margin-bottom: 2rem; }}
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

def format_number(num):
    try:
        return f"{int(num):,}".replace(',', '.')
    except:
        return str(num)

# ==================== CARREGAMENTO DE DADOS ====================

@st.cache_data(ttl=7200, show_spinner=False)
def load_excel_optimized(versao=5):
    """VERSÃO 5.1 COM PARQUET CACHE - CORRIGIDO MIXED TYPES"""
    try:
        parquet_path = Path("MAPEAMENTO_DE_CHIPS.parquet")
        excel_path = Path("MAPEAMENTO DE CHIPS.xlsx")
        
        if not excel_path.exists():
            return pd.DataFrame()
        
        # Usar Parquet se existir e for mais recente
        if parquet_path.exists() and parquet_path.stat().st_mtime > excel_path.stat().st_mtime:
            return pd.read_parquet(parquet_path)
        
        # Carregar Excel
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
        
        # CONVERSÃO DE TIPOS PARA EVITAR ERRO NO PARQUET
        colunas_texto = ['PROJETO', 'ICCID', 'OPERADORA', 'STATUS NA OP.']
        for col in colunas_texto:
            if col in df_completo.columns:
                df_completo[col] = df_completo[col].astype(str)
        
        # Normalização
        if 'OPERADORA' in df_completo.columns:
            df_completo['OPERADORA'] = df_completo['OPERADORA'].apply(normalizar_operadora)
        
        # Datas
        date_cols = ['DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO', 'ÚLTIMA CONEXÃO']
        for col in date_cols:
            if col in df_completo.columns:
                df_completo[col] = pd.to_datetime(df_completo[col], errors='coerce', format='mixed')
        
        # Status da licença
        hoje = pd.Timestamp.now().normalize()
        if 'DATA DE VENCIMENTO' in df_completo.columns:
            df_completo['STATUS_LICENCA'] = df_completo['DATA DE VENCIMENTO'].apply(
                lambda x: 'Expirado' if pd.notna(x) and x < hoje else 'Válido'
            )
        
        # Categoria de conexão
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
            df_completo['STATUS NA OP.'] = df_completo['STATUS NA OP.'].str.strip().str.title()
        
        # CONVERSÃO FINAL - Garantir compatibilidade com Parquet
        for col in df_completo.columns:
            if df_completo[col].dtype == 'object' and col not in date_cols:
                df_completo[col] = df_completo[col].astype(str)
        
        # Salvar Parquet
        try:
            df_completo.to_parquet(parquet_path, compression='snappy', engine='pyarrow')
        except Exception as parquet_error:
            # Se falhar, continua sem cache
            pass
        
        return df_completo
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        import traceback
        st.code(traceback.format_exc())
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def aplicar_filtros(df, filtros_dict):
    """Aplica filtros com cache"""
    df_filtrado = df.copy()
    
    if filtros_dict.get('projetos'):
        df_filtrado = df_filtrado[df_filtrado['PROJETO'].isin(filtros_dict['projetos'])]
    if filtros_dict.get('operadoras'):
        df_filtrado = df_filtrado[df_filtrado['OPERADORA'].isin(filtros_dict['operadoras'])]
    if filtros_dict.get('status_op'):
        df_filtrado = df_filtrado[df_filtrado['STATUS NA OP.'].isin(filtros_dict['status_op'])]
    if filtros_dict.get('status_licenca'):
        df_filtrado = df_filtrado[df_filtrado['STATUS_LICENCA'].isin(filtros_dict['status_licenca'])]
    
    return df_filtrado

@st.cache_data(ttl=3600)
def calcular_metricas_rapido(df_filtrado):
    hoje = pd.Timestamp.now().normalize()
    df_com_venc = df_filtrado[df_filtrado['DATA DE VENCIMENTO'].notna()]
    
    validas = (df_com_venc['DATA DE VENCIMENTO'] > hoje).sum()
    expiradas = (df_com_venc['DATA DE VENCIMENTO'] <= hoje).sum()
    
    return {
        'total': len(df_filtrado),
        'vinculadas': len(df_filtrado),
        'perc_vinculadas': 100.0,
        'saldo': 0,
        'validas': int(validas),
        'expiradas': int(expiradas)
    }

@st.cache_data(ttl=3600)
def agregar_dados_graficos(df_filtrado):
    """Agrega dados para gráficos"""
    
    df_op = df_filtrado['OPERADORA'].value_counts().reset_index()
    df_op.columns = ['Operadora', 'Qtd']
    
    df_proj = df_filtrado['PROJETO'].value_counts().head(10).reset_index()
    df_proj.columns = ['Projeto', 'Qtd']
    
    hoje = pd.Timestamp.now().normalize()
    df_venc = df_filtrado[df_filtrado['DATA DE VENCIMENTO'].notna()].copy()
    df_venc_validos = df_venc[df_venc['DATA DE VENCIMENTO'] > hoje]
    
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
    
    return {
        'operadoras': df_op,
        'projetos': df_proj,
        'venc_mensal': venc_mensal,
        'conexoes': df_conexao,
        'status_op': df_status_op
    }

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
            line=dict(color='white', width=3)
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

# ==================== ALERTAS INTELIGENTES ====================

def gerar_alertas_inteligentes(df):
    """Identifica e exibe alertas importantes"""
    alertas = []
    hoje = pd.Timestamp.now().normalize()
    
    # Licenças expirando em 30 dias
    venc_30 = df[
        (df['DATA DE VENCIMENTO'] > hoje) &
        (df['DATA DE VENCIMENTO'] <= hoje + pd.Timedelta(days=30))
    ]
    if len(venc_30) > 0:
        alertas.append(("warning", f"⚠️ **{len(venc_30)} licenças** vencem nos próximos 30 dias"))
    
    # Chips sem conexão há mais de 180 dias
    if 'CATEGORIA_CONEXAO' in df.columns:
        sem_conexao_180 = df[df['CATEGORIA_CONEXAO'] == 'Mais de 180 dias']
        if len(sem_conexao_180) > 0:
            alertas.append(("error", f"🔴 **{len(sem_conexao_180)} chips** sem conexão há mais de 180 dias"))
    
    # Licenças já expiradas
    if 'STATUS_LICENCA' in df.columns:
        expiradas = df[df['STATUS_LICENCA'] == 'Expirado']
        if len(expiradas) > 0:
            alertas.append(("error", f"❌ **{len(expiradas)} licenças** já expiradas - renovação necessária"))
    
    # Taxa de chips nunca conectados
    if 'CATEGORIA_CONEXAO' in df.columns:
        nunca_conectou = df[df['CATEGORIA_CONEXAO'] == 'Nunca Conectou']
        taxa = len(nunca_conectou) / len(df) * 100 if len(df) > 0 else 0
        if taxa > 15:
            alertas.append(("info", f"📊 **{taxa:.1f}%** dos chips nunca conectaram - investigar"))
    
    # Exibir alertas
    if alertas:
        st.markdown("### 🚨 Alertas e Recomendações")
        for tipo, mensagem in alertas:
            if tipo == "warning":
                st.warning(mensagem)
            elif tipo == "error":
                st.error(mensagem)
            else:
                st.info(mensagem)
        st.markdown("---")

# ==================== EXPORTAÇÃO DE DADOS ====================

def criar_botoes_exportacao(df_filtrado):
    """Permite download dos dados filtrados"""
    st.markdown("### 📥 Exportar Dados")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_filtrado.to_excel(writer, sheet_name='Dados Filtrados', index=False)
            
            # Sheet de resumo
            resumo = df_filtrado.groupby('OPERADORA').size().reset_index(name='Qtd')
            resumo.to_excel(writer, sheet_name='Resumo por Operadora', index=False)
            
        st.download_button(
            label="📥 Baixar Excel",
            data=buffer,
            file_name=f'licencas_basemobile_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
            mime='application/vnd.ms-excel',
            use_container_width=True
        )
    
    with col2:
        # CSV
        csv = df_filtrado.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name=f'licencas_basemobile_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv',
            use_container_width=True
        )
    
    with col3:
        # JSON
        json_data = df_filtrado.to_json(orient='records', date_format='iso', force_ascii=False)
        st.download_button(
            label="📥 Baixar JSON",
            data=json_data,
            file_name=f'licencas_basemobile_{datetime.now().strftime("%Y%m%d_%H%M")}.json',
            mime='application/json',
            use_container_width=True
        )

# ==================== ASSISTENTE IA COM GROQ ====================

def criar_prompt_sistema(df_filtrado):
    """Cria prompt do sistema com contexto dos dados"""
    hoje = pd.Timestamp.now().strftime("%d/%m/%Y")
    
    resumo_operadoras = df_filtrado['OPERADORA'].value_counts().to_dict()
    top5_projetos = df_filtrado['PROJETO'].value_counts().head(5).to_dict()
    
    validas = (df_filtrado['STATUS_LICENCA'] == 'Válido').sum() if 'STATUS_LICENCA' in df_filtrado.columns else 0
    expiradas = (df_filtrado['STATUS_LICENCA'] == 'Expirado').sum() if 'STATUS_LICENCA' in df_filtrado.columns else 0
    
    prompt_sistema = f"""Você é o Assistente IA da Base Mobile, especializado em análise de dados de gestão de licenças de chips M2M/IoT.

🎯 DIRETRIZES FUNDAMENTAIS:
- Você é um especialista em telecomunicações e análise de dados
- Sempre responda em português brasileiro
- Use formatação Markdown para clareza
- Seja objetivo, técnico e profissional
- Forneça insights acionáveis com base nos dados
- Use emojis relevantes para melhor visualização
- Cite sempre números e percentuais quando relevante

📊 CONTEXTO DOS DADOS ATUAIS (atualizado em {hoje}):

**Resumo Geral:**
- Total de licenças: {len(df_filtrado):,}
- Projetos ativos: {df_filtrado['PROJETO'].nunique()}
- Licenças válidas: {validas:,}
- Licenças expiradas: {expiradas:,}

**Distribuição por Operadora:**
{chr(10).join([f'- {op}: {qtd:,} licenças' for op, qtd in resumo_operadoras.items()])}

**Top 5 Projetos:**
{chr(10).join([f'- {proj}: {qtd:,} licenças' for proj, qtd in top5_projetos.items()])}

🚫 GUARDRAILS (O QUE NÃO FAZER):
- NÃO invente dados ou números que não foram fornecidos
- NÃO responda sobre temas não relacionados a gestão de licenças/chips
- NÃO faça recomendações financeiras sem base nos dados
- NÃO compartilhe informações confidenciais de clientes

✅ VOCÊ PODE AJUDAR COM:
- Análises e insights sobre os dados de licenças
- Identificação de padrões e anomalias
- Recomendações operacionais baseadas em dados
- Explicações sobre métricas e indicadores
- Sugestões de otimização de recursos
- Interpretação de tendências temporais

Se a pergunta fugir do escopo, responda educadamente:
"Sou especializado em análise de dados de licenças da Base Mobile. Posso ajudar com análises, métricas, tendências e insights sobre gestão de chips. Como posso auxiliar com os dados de licenças?"
"""
    return prompt_sistema

def processar_mensagem_groq(client, mensagens, df_filtrado):
    """Processa mensagem com Groq e retorna resposta"""
    try:
        # Criar prompt do sistema
        prompt_sistema = criar_prompt_sistema(df_filtrado)
        
        # Preparar mensagens com contexto
        mensagens_completas = [
            {"role": "system", "content": prompt_sistema}
        ] + mensagens
        
        # Chamar Groq API com streaming
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensagens_completas,
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9,
            stream=True
        )
        
        return stream
    
    except Exception as e:
        st.error(f"Erro ao processar mensagem: {e}")
        return None

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
    st.caption("Base Mobile 2026 • v5.1 AI Edition")
    st.markdown("---")
    
    # FILTROS EM FORM
    with st.form("form_filtros"):
        st.markdown("### 🎯 Filtros Dinâmicos")
        
        if st.session_state.df_loaded is not None and not st.session_state.df_loaded.empty:
            df_temp = st.session_state.df_loaded
            
            projetos = st.multiselect("📍 Projetos", sorted(df_temp['PROJETO'].unique()))
            operadoras = st.multiselect("📡 Operadoras", sorted(df_temp['OPERADORA'].unique()))
            
            if 'STATUS NA OP.' in df_temp.columns:
                status_op = st.multiselect("🔌 Status na OP", sorted(df_temp['STATUS NA OP.'].unique()))
            else:
                status_op = []
            
            if 'STATUS_LICENCA' in df_temp.columns:
                status_lic = st.multiselect("✅ Status Licença", ['Válido', 'Expirado'])
            else:
                status_lic = []
            
            aplicar = st.form_submit_button("🔍 Aplicar Filtros", use_container_width=True)
            
            if aplicar:
                st.session_state.filtros_ativos = {
                    'projetos': projetos,
                    'operadoras': operadoras,
                    'status_op': status_op,
                    'status_licenca': status_lic
                }
                st.rerun()
    
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
        # Limpar cache do Parquet
        parquet_path = Path("MAPEAMENTO_DE_CHIPS.parquet")
        if parquet_path.exists():
            parquet_path.unlink()
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption("💡 **Dica:** Use o Assistente IA para análises avançadas")

# ==================== HEADER ====================
st.markdown(f"""
<div class="header-container">
    <div style="display: flex; align-items: center; gap: 2rem;">
        <div class="header-logo">
            {f'<img src="data:image/png;base64,{logo_full}" style="max-height: 55px;">' if logo_full else '<div style="font-size: 2rem; font-weight: 900; color: ' + COLORS['accent'] + ';">BASE MOBILE</div>'}
        </div>
        <div>
            <h1 class="header-title">Dashboard Gerencial de Licenças</h1>
            <p class="header-subtitle">Sistema Enterprise 5.1 AI Edition | Analytics & Intelligence</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== CARREGAMENTO ====================
if st.session_state.df_loaded is None:
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        show_loading("Processando base de dados")
    
    st.session_state.df_loaded = load_excel_optimized(versao=5)
    loading_placeholder.empty()

df = st.session_state.df_loaded

if df.empty:
    st.error("❌ Erro ao carregar dados. Verifique se o arquivo 'MAPEAMENTO DE CHIPS.xlsx' existe.")
    st.stop()

# Aplicar filtros
df_filtrado = aplicar_filtros(df, st.session_state.filtros_ativos)

st.success(f"✅ **{len(df_filtrado):,} licenças** carregadas | **{df_filtrado['PROJETO'].nunique()} projetos** | **{df_filtrado['OPERADORA'].nunique()} operadoras**".replace(',', '.'))
st.markdown("---")

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs(["📊 Dashboard Executivo", "💬 Assistente IA", "📋 Dados Detalhados"])

with tab1:
    st.markdown("### 🎯 Indicadores Estratégicos")
    
    metricas = calcular_metricas_rapido(df_filtrado)
    
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
    
    # ALERTAS INTELIGENTES
    gerar_alertas_inteligentes(df_filtrado)
    
    # GRÁFICOS
    st.markdown("### 📊 Análises Visuais")
    
    dados_graficos = agregar_dados_graficos(df_filtrado)
    
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
    
    # BOTÕES DE EXPORTAÇÃO
    st.markdown("---")
    criar_botoes_exportacao(df_filtrado)

with tab2:
    st.markdown("### 💬 Assistente IA de Análise de Dados")
    st.caption("Powered by Groq AI • Llama 3.3 70B")
    
    groq_client = get_groq_client()
    
    if groq_client:
        # Exibir histórico do chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Input do usuário
        if prompt := st.chat_input("Pergunte sobre os dados de licenças... 💭"):
            # Adicionar mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Gerar resposta com streaming
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                stream = processar_mensagem_groq(groq_client, st.session_state.messages, df_filtrado)
                
                if stream:
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                else:
                    full_response = "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
                    message_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Sugestões de perguntas
        st.markdown("---")
        with st.expander("💡 Perguntas Sugeridas", expanded=True):
            col1, col2 = st.columns(2)
            
            perguntas_exemplo = [
                "📊 Qual operadora tem mais licenças ativas?",
                "⏰ Quantas licenças vencem nos próximos 30 dias?",
                "🔴 Quais projetos têm mais chips sem conexão?",
                "📈 Qual a taxa de ativação por operadora?",
                "🚨 Identifique possíveis problemas ou alertas",
                "💡 Sugira otimizações para reduzir custos",
                "📉 Analise a tendência de vencimentos",
                "🎯 Quais projetos precisam de atenção imediata?"
            ]
            
            for i, pergunta in enumerate(perguntas_exemplo):
                col = col1 if i % 2 == 0 else col2
                with col:
                    if st.button(pergunta, key=f"sugestao_{i}", use_container_width=True):
                        st.session_state.messages.append({"role": "user", "content": pergunta})
                        st.rerun()
        
        # Botão para limpar conversa
        if st.button("🗑️ Limpar Conversa", type="secondary"):
            st.session_state.messages = []
            st.rerun()
    
    else:
        st.warning("⚠️ **Assistente IA Desabilitado**")
        st.info("""
        Para ativar o Assistente IA, configure sua chave API do Groq:
        
        1. Crie uma conta gratuita em [console.groq.com](https://console.groq.com)
        2. Gere uma API Key
        3. Adicione a chave no arquivo `.streamlit/secrets.toml`:
        
        ```toml
        GROQ_API_KEY = "sua-chave-aqui"
        ```
        
        Ou defina como variável de ambiente:
        
        ```bash
        export GROQ_API_KEY="sua-chave-aqui"
        ```
        """)

with tab3:
    st.markdown("### 📋 Visualização Detalhada de Dados")
    
    # Configurações de exibição
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        busca = st.text_input("🔍 Buscar ICCID ou Projeto", "")
    with col2:
        colunas_disponiveis = df_filtrado.columns.tolist()
        colunas_padrao = ['PROJETO', 'ICCID', 'OPERADORA', 'STATUS NA OP.', 'DATA DE VENCIMENTO']
        colunas_padrao = [c for c in colunas_padrao if c in colunas_disponiveis]
        
        colunas_visiveis = st.multiselect(
            "Colunas visíveis",
            options=colunas_disponiveis,
            default=colunas_padrao
        )
    with col3:
        linhas_por_pagina = st.selectbox("Linhas/página", [10, 25, 50, 100], index=1)
    
    # Aplicar busca
    if busca:
        mask = df_filtrado.astype(str).apply(lambda x: x.str.contains(busca, case=False, na=False)).any(axis=1)
        df_exibir = df_filtrado[mask]
    else:
        df_exibir = df_filtrado
    
    # Paginação
    total_linhas = len(df_exibir)
    total_paginas = (total_linhas // linhas_por_pagina) + (1 if total_linhas % linhas_por_pagina else 0)
    
    if total_paginas > 1:
        pagina_atual = st.number_input(
            f"Página (de {total_paginas})",
            min_value=1,
            max_value=max(1, total_paginas),
            value=1
        )
    else:
        pagina_atual = 1
    
    inicio = (pagina_atual - 1) * linhas_por_pagina
    fim = inicio + linhas_por_pagina
    
    # Exibir tabela
    if colunas_visiveis:
        st.dataframe(
            df_exibir[colunas_visiveis].iloc[inicio:fim],
            use_container_width=True,
            height=450
        )
        
        st.caption(f"Exibindo {inicio+1}-{min(fim, total_linhas)} de {total_linhas} registros")
    else:
        st.warning("⚠️ Selecione pelo menos uma coluna para visualizar")
    
    # Botões de exportação da tabela filtrada
    st.markdown("---")
    criar_botoes_exportacao(df_exibir)

st.markdown("---")
st.caption("© 2026 Base Mobile | Dashboard Enterprise v5.1 AI Edition | Powered by Streamlit, Plotly & Groq AI")
