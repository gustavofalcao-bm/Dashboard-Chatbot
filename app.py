import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import warnings
import base64

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Base Mobile | Gestão Integrada",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLORS = {
    'primary': '#1a1a1a', 'secondary': '#8BC34A', 'accent': '#4CAF50',
    'dark_green': '#2E7D32', 'light_green': '#C5E1A5', 'warning': '#FFB74D',
    'danger': '#E57373', 'info': '#64B5F6', 'light': '#FAFAFA',
    'gray': '#BDBDBD', 'dark_gray': '#616161', 'white': '#FFFFFF',
    'claro': '#FF5252', 'vivo': '#7B1FA2', 'tim': '#1976D2',
    'oi': '#FDD835', 'algar': '#00C853'
}

CORES_ACAO = {
    'ENTREGA': "#4FB853", 'ATIVAÇÃO': '#2196F3', 'VINCULAÇÃO': '#FF9800',
    'EXPIRAÇÃO': '#F44336', 'CANCELAMENTO': '#9C27B0', 'RENOVAÇÃO': '#00BCD4',
    'PAGAMENTO': '#8BC34A', 'SUBSTITUIÇÃO': '#FFC107'
}

def load_logo(variants):
    for v in variants:
        try:
            with open(v, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            continue
    return None

def normalizar_operadora(operadora):
    if pd.isna(operadora):
        return "NÃO INFORMADO"
    op = str(operadora).strip().upper().split()[0]
    return {'CLAROTIM': 'CLARO', 'VIVOTIM': 'VIVO', 'TIMCLARO': 'TIM'}.get(op, op)

def format_number(num):
    try:
        return f"{int(num):,}".replace(',', '.')
    except:
        return str(num)

def get_cache_signature(filtros_dict):
    return (
        tuple(sorted(filtros_dict.get('projetos', []))),
        tuple(sorted(filtros_dict.get('operadoras', []))),
        tuple(sorted(filtros_dict.get('status_op', []))),
        tuple(sorted(filtros_dict.get('status_licenca', [])))
    )

def show_premium_loading(message="Processando"):
    return f"""
    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(26, 26, 26, 0.97); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 9999; backdrop-filter: blur(12px);">
        <div style="position: relative; width: 140px; height: 140px;">
            <div style="position: absolute; width: 140px; height: 140px; border: 10px solid rgba(139, 195, 74, 0.1); border-top-color: #8BC34A; border-radius: 50%; animation: spin 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;"></div>
            <div style="position: absolute; top: 20px; left: 20px; width: 100px; height: 100px; border: 8px solid rgba(76, 175, 80, 0.1); border-bottom-color: #4CAF50; border-radius: 50%; animation: spin-reverse 1.8s linear infinite;"></div>
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 3rem; filter: drop-shadow(0 0 10px rgba(139, 195, 74, 0.5));">⚡</div>
        </div>
        <div style="margin-top: 2.5rem; font-size: 1.8rem; font-weight: 900; color: white; text-transform: uppercase; letter-spacing: 2px; animation: pulse 1.5s ease-in-out infinite;">{message}</div>
        <div style="margin-top: 1.5rem; width: 250px; height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 3px; overflow: hidden;">
            <div style="width: 100%; height: 100%; background: linear-gradient(90deg, #8BC34A, #4CAF50, #8BC34A); background-size: 200% 100%; animation: progress 2s ease-in-out infinite;"></div>
        </div>
    </div>
    <style>
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        @keyframes spin-reverse {{ 0% {{ transform: rotate(360deg); }} 100% {{ transform: rotate(0deg); }} }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.8; }} }}
        @keyframes progress {{ 0% {{ background-position: 0% 50%; }} 100% {{ background-position: 200% 50%; }} }}
    </style>
    """

def aplicar_css():
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        * {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f0 100%); }}

        [data-testid="stSidebar"] {{ 
            background: rgba(30, 58, 95, 0.85) !important;
            backdrop-filter: blur(20px) saturate(180%);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}
        [data-testid="stSidebar"] * {{ color: white !important; }}

        [data-testid="stSidebar"] .stButton > button {{ 
            background: linear-gradient(135deg, rgba(139, 195, 74, 0.2), rgba(76, 175, 80, 0.2)) !important;
            border: 2px solid rgba(139, 195, 74, 0.5) !important;
            color: white !important;
            font-weight: 700 !important;
            border-radius: 12px !important;
            transition: all 0.4s ease !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{ 
            background: linear-gradient(135deg, #8BC34A, #4CAF50) !important;
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(139, 195, 74, 0.4);
        }}

        .metric-card {{
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(20px);
            padding: 2rem 1.5rem;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
            transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
            text-align: center;
            cursor: pointer;
        }}
        .metric-card:hover {{
            transform: translateY(-15px) scale(1.02);
            box-shadow: 0 25px 80px rgba(139, 195, 74, 0.4);
        }}

        .metric-icon {{
            font-size: 2.8rem;
            margin-bottom: 0.8rem;
            transition: all 0.5s ease;
        }}
        .metric-card:hover .metric-icon {{
            transform: scale(1.3) rotate(10deg);
            animation: bounce 0.6s ease infinite;
        }}
        @keyframes bounce {{
            0%, 100% {{ transform: scale(1.3) rotate(10deg) translateY(0); }}
            50% {{ transform: scale(1.3) rotate(10deg) translateY(-5px); }}
        }}

        .metric-value {{
            font-size: 2.8rem;
            font-weight: 900;
            margin: 0.8rem 0;
        }}
        .metric-label {{
            font-size: 0.8rem;
            color: {COLORS['dark_gray']};
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 700;
        }}
        .metric-delta {{
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }}
        .metric-delta.positive {{ color: {COLORS['accent']}; }}
        .metric-delta.negative {{ color: {COLORS['danger']}; }}

        .filter-chip {{
            display: inline-block;
            background: linear-gradient(135deg, #8BC34A, #4CAF50);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 4px;
            font-size: 13px;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(139, 195, 74, 0.3);
        }}

        .header-parallax {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 25%, #8BC34A 75%, #4CAF50 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            padding: 2.5rem;
            border-radius: 24px;
            margin-bottom: 2rem;
        }}
        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}

        ::-webkit-scrollbar {{ width: 12px; }}
        ::-webkit-scrollbar-thumb {{ 
            background: linear-gradient(180deg, {COLORS['secondary']}, {COLORS['accent']}); 
            border-radius: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=7200, show_spinner=False)
def load_data_smart():
    try:
        excel_path = Path("MAPEAMENTO DE CHIPS.xlsx")
        parquet_path = Path(".cache_mapeamento.parquet")

        if parquet_path.exists() and excel_path.exists():
            excel_mtime = excel_path.stat().st_mtime
            parquet_mtime = parquet_path.stat().st_mtime
            if parquet_mtime >= excel_mtime:
                try:
                    return pd.read_parquet(parquet_path), True
                except:
                    pass

        if not excel_path.exists():
            return pd.DataFrame(), False

        all_sheets = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
        dfs = []
        for sheet_name, df_sheet in all_sheets.items():
            df_sheet.columns = df_sheet.columns.str.strip().str.upper()
            if 'PROJETO' not in df_sheet.columns:
                df_sheet['PROJETO'] = sheet_name
            dfs.append(df_sheet)

        df = pd.concat(dfs, ignore_index=True)

        if 'ICCID' in df.columns:
            df['ICCID'] = df['ICCID'].astype(str)
        if 'OPERADORA' in df.columns:
            df['OPERADORA'] = df['OPERADORA'].apply(normalizar_operadora)

        date_cols = ['DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO', 'ÚLTIMA CONEXÃO']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        hoje = pd.Timestamp.now().normalize()

        if 'DATA DE VENCIMENTO' in df.columns:
            df['STATUS_LICENCA'] = df['DATA DE VENCIMENTO'].apply(
                lambda x: 'Expirado' if pd.notna(x) and x < hoje else 'Válido')

        if 'ÚLTIMA CONEXÃO' in df.columns:
            def categorizar(data):
                if pd.isna(data):
                    return 'Nunca Conectou'
                dias = (hoje - data).days
                if dias <= 30:
                    return '0-30 dias'
                elif dias <= 90:
                    return '31-90 dias'
                elif dias <= 180:
                    return '91-180 dias'
                return 'Mais de 180 dias'
            df['CATEGORIA_CONEXAO'] = df['ÚLTIMA CONEXÃO'].apply(categorizar)

        if 'STATUS NA OP.' in df.columns:
            df['STATUS NA OP.'] = df['STATUS NA OP.'].fillna('Não Informado').astype(str).str.strip().str.title()

        try:
            df.to_parquet(parquet_path, compression='snappy', index=False)
        except:
            pass

        return df, False
    except Exception as e:
        st.error(f"❌ Erro ao carregar MAPEAMENTO: {str(e)}")
        return pd.DataFrame(), False

@st.cache_data(ttl=7200, show_spinner=False)
def load_dados_gerenciais():
    try:
        excel_path = Path("DADOS-GERENCIAIS.xlsx")
        if not excel_path.exists():
            return None, None

        df_contratos = pd.read_excel(excel_path, sheet_name='DADOS CONTRATUAIS', engine='openpyxl')
        df_timeline = pd.read_excel(excel_path, sheet_name='TIMELINE', engine='openpyxl')

        df_contratos = df_contratos.dropna(how='all').dropna(subset=['PROJETO'])
        df_timeline = df_timeline.dropna(how='all').dropna(subset=['PROJETO'])

        for df in [df_contratos, df_timeline]:
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()
            df.columns = df.columns.str.strip().str.upper()

        df_contratos.reset_index(drop=True, inplace=True)
        df_timeline.reset_index(drop=True, inplace=True)

        if 'DATA' in df_timeline.columns:
            df_timeline['DATA'] = pd.to_datetime(df_timeline['DATA'], errors='coerce')

        return df_contratos, df_timeline
    except Exception as e:
        st.warning(f"⚠️ Dados gerenciais não carregados: {str(e)}")
        return None, None

def aplicar_filtros(df, filtros):
    if not filtros or not any(filtros.values()):
        return df
    mask = pd.Series(True, index=df.index)
    if filtros.get('projetos'):
        mask &= df['PROJETO'].isin(filtros['projetos'])
    if filtros.get('operadoras'):
        mask &= df['OPERADORA'].isin(filtros['operadoras'])
    if filtros.get('status_op'):
        mask &= df['STATUS NA OP.'].isin(filtros['status_op'])
    if filtros.get('status_licenca'):
        mask &= df['STATUS_LICENCA'].isin(filtros['status_licenca'])
    return df[mask]

def calcular_preview(df, filtros_temp):
    if not any(filtros_temp.values()):
        return len(df)
    return len(aplicar_filtros(df, filtros_temp))

@st.cache_data(ttl=1800)
def calcular_metricas_cached(cache_signature):
    df = st.session_state.df_filtrado
    hoje = pd.Timestamp.now().normalize()
    df_venc = df[df['DATA DE VENCIMENTO'].notna()]

    validas = int((df_venc['DATA DE VENCIMENTO'] > hoje).sum())
    expiradas = int((df_venc['DATA DE VENCIMENTO'] <= hoje).sum())
    total = len(df)

    pct_validas = (validas / total * 100) if total > 0 else 0
    conectadas_30d = (df['CATEGORIA_CONEXAO'] == '0-30 dias').sum() if 'CATEGORIA_CONEXAO' in df.columns else 0
    pct_conectadas = (conectadas_30d / total * 100) if total > 0 else 0

    venc_30 = df[(df['DATA DE VENCIMENTO'] > hoje) & 
                 (df['DATA DE VENCIMENTO'] <= hoje + pd.Timedelta(days=30))]
    sem_alerta = total - len(venc_30)
    pct_sem_alerta = (sem_alerta / total * 100) if total > 0 else 0

    health_score = (pct_validas * 0.4) + (pct_conectadas * 0.3) + (pct_sem_alerta * 0.3)
    chips_com_conexao = df['ÚLTIMA CONEXÃO'].notna().sum() if 'ÚLTIMA CONEXÃO' in df.columns else 0
    taxa_utilizacao = (chips_com_conexao / total * 100) if total > 0 else 0

    return {
        'total': total, 'vinculadas': total, 'perc_vinculadas': 100.0,
        'saldo': 0, 'validas': validas, 'expiradas': expiradas,
        'health_score': round(health_score, 1),
        'taxa_utilizacao': round(taxa_utilizacao, 1),
        'conectadas_30d': conectadas_30d
    }

def calcular_entregas_por_projeto():
    df_chips = st.session_state.df_base
    df_contratos = st.session_state.df_contratos

    if df_contratos is None:
        return pd.DataFrame()

    entregas = []

    for projeto in df_chips['PROJETO'].unique():
        df_proj = df_chips[df_chips['PROJETO'] == projeto]
        total = len(df_proj)
        contrato = df_contratos[df_contratos['PROJETO'] == projeto]
        if contrato.empty:
            continue

        previstas = contrato['TOTAL DE LICENÇAS PREVISTAS'].values[0]
        pct_entregue = (total / previstas * 100) if previstas > 0 else 0

        claro = len(df_proj[df_proj['OPERADORA'] == 'CLARO'])
        vivo = len(df_proj[df_proj['OPERADORA'] == 'VIVO'])
        tim = len(df_proj[df_proj['OPERADORA'] == 'TIM'])
        algar = len(df_proj[df_proj['OPERADORA'] == 'ALGAR'])

        funcionais = len(df_proj[df_proj['STATUS NA OP.'].isin(['Ativo', 'Suspenso'])])
        pct_funcional = (funcionais / total * 100) if total > 0 else 0

        entregas.append({
            'PROJETO': projeto,
            'TOTAL ENTREGUES': total,
            '% ENTREGUES': round(pct_entregue, 1),
            'CLARO': claro,
            'VIVO': vivo,
            'TIM': tim,
            'ALGAR': algar,
            'FUNCIONAIS': funcionais,
            '% FUNCIONAIS': round(pct_funcional, 1)
        })

    return pd.DataFrame(entregas)

def gerar_html_tabela_entregas(df_entregas):
    """Gera HTML da tabela de entregas - USAR COM st.components.v1.html()"""
    if df_entregas.empty:
        return "<p>Nenhum dado disponível</p>"

    linhas = []
    for _, row in df_entregas.iterrows():
        pct_ent = row['% ENTREGUES']
        cor_ent = '#4CAF50' if pct_ent >= 90 else ('#FFB74D' if pct_ent >= 70 else '#E57373')

        pct_func = row['% FUNCIONAIS']
        cor_func = '#4CAF50' if pct_func >= 80 else ('#FFB74D' if pct_func >= 60 else '#E57373')

        linhas.append(f"""
        <tr style="border-bottom: 1px solid rgba(0,0,0,0.1);">
            <td style="padding: 0.8rem; font-weight: 600;">{row['PROJETO']}</td>
            <td style="padding: 0.8rem; text-align: center;">{format_number(row['TOTAL ENTREGUES'])}</td>
            <td style="padding: 0.8rem; text-align: center; background: {cor_ent}20; color: {cor_ent}; font-weight: 700;">{pct_ent:.1f}%</td>
            <td style="padding: 0.8rem; text-align: center;">{format_number(row['CLARO'])}</td>
            <td style="padding: 0.8rem; text-align: center;">{format_number(row['VIVO'])}</td>
            <td style="padding: 0.8rem; text-align: center;">{format_number(row['TIM'])}</td>
            <td style="padding: 0.8rem; text-align: center;">{format_number(row['ALGAR'])}</td>
            <td style="padding: 0.8rem; text-align: center;">{format_number(row['FUNCIONAIS'])}</td>
            <td style="padding: 0.8rem; text-align: center; background: {cor_func}20; color: {cor_func}; font-weight: 700;">{pct_func:.1f}%</td>
        </tr>
        """)

    html_final = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ font-family: 'Inter', sans-serif; margin: 0; padding: 0; }}
            body {{ background: transparent; }}
            .container {{
                background: rgba(255,255,255,0.7);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                padding: 1rem;
                overflow-x: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            thead tr {{
                background: linear-gradient(135deg, #1e3a5f, #2c5282);
                color: white;
            }}
            th {{
                padding: 1rem;
                text-align: center;
                font-weight: 700;
                font-size: 0.9rem;
            }}
            th:first-child {{
                text-align: left;
            }}
            tbody tr:hover {{
                background: rgba(139, 195, 74, 0.05);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <table>
                <thead>
                    <tr>
                        <th>PROJETO</th>
                        <th>TOTAL</th>
                        <th>% ENTREGUES</th>
                        <th>CLARO</th>
                        <th>VIVO</th>
                        <th>TIM</th>
                        <th>ALGAR</th>
                        <th>FUNCIONAIS</th>
                        <th>% FUNCIONAIS</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(linhas)}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    return html_final

def gerar_html_tabela_contratos(df_contratos):
    """Gera HTML da tabela de contratos - ESTILO IDÊNTICO À DE ENTREGAS"""
    if df_contratos.empty:
        return "<p>Nenhum dado disponível</p>"

    linhas = []
    for _, row in df_contratos.iterrows():
        status = row['STATUS ATUAL DO CONTRATO']

        # Cores por status
        if status == 'VÁLIDO':
            cor_status = '#4CAF50'
        elif status == 'EXPIRANDO':
            cor_status = '#FFB74D'
        elif status == 'EXPIRADO':
            cor_status = '#E57373'
        elif status == 'EM RENOVAÇÃO':
            cor_status = '#64B5F6'
        else:
            cor_status = '#BDBDBD'

        # Formatar datas
        data_inicial = pd.to_datetime(row['DATA INICIAL'], errors='coerce')
        data_inicial_fmt = data_inicial.strftime('%d/%m/%Y') if pd.notna(data_inicial) else '-'

        data_renovacao = pd.to_datetime(row['DATA DA ÚLTIMA RENOVAÇÃO CONTRATUAL'], errors='coerce')
        data_renovacao_fmt = data_renovacao.strftime('%d/%m/%Y') if pd.notna(data_renovacao) else '-'

        # Formatar licenças previstas
        try:
            licencas = format_number(row['TOTAL DE LICENÇAS PREVISTAS'])
        except:
            licencas = str(row['TOTAL DE LICENÇAS PREVISTAS']) if pd.notna(row['TOTAL DE LICENÇAS PREVISTAS']) else '-'

        # Formatar duração
        duracao = f"{row['DURAÇÃO CONTRATUAL (MESES)']} m" if pd.notna(row['DURAÇÃO CONTRATUAL (MESES)']) else '-'

        linhas.append(f"""
        <tr style="border-bottom: 1px solid rgba(0,0,0,0.1);">
            <td style="padding: 0.8rem; font-weight: 600;">{row['PROJETO']}</td>
            <td style="padding: 0.8rem; text-align: center;">{row['FOCAL POINT 1']}</td>
            <td style="padding: 0.8rem; text-align: center;">{row['FOCAL POINT 2']}</td>
            <td style="padding: 0.8rem; text-align: center;">{data_inicial_fmt}</td>
            <td style="padding: 0.8rem; text-align: center;">{row['SERVIÇOS CONTRATADOS']}</td>
            <td style="padding: 0.8rem; text-align: center; font-weight: 700;">{licencas}</td>
            <td style="padding: 0.8rem; text-align: center;">{data_renovacao_fmt}</td>
            <td style="padding: 0.8rem; text-align: center;">{duracao}</td>
            <td style="padding: 0.8rem; text-align: center; background: {cor_status}20; color: {cor_status}; font-weight: 700;">{status}</td>
        </tr>
        """)

    html_final = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ font-family: 'Inter', sans-serif; margin: 0; padding: 0; }}
            body {{ background: transparent; }}
            .container {{
                background: rgba(255,255,255,0.7);
                backdrop-filter: blur(20px);
                border-radius: 16px;
                padding: 1rem;
                overflow-x: auto;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 1200px;
            }}
            thead tr {{
                background: linear-gradient(135deg, #1e3a5f, #2c5282);
                color: white;
            }}
            th {{
                padding: 1rem 0.5rem;
                text-align: center;
                font-weight: 700;
                font-size: 0.8rem;
                white-space: nowrap;
            }}
            th:first-child {{
                text-align: left;
                padding-left: 0.8rem;
            }}
            tbody tr:hover {{
                background: rgba(139, 195, 74, 0.05);
                transition: all 0.3s ease;
            }}
            td {{
                font-size: 0.85rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <table>
                <thead>
                    <tr>
                        <th>PROJETO</th>
                        <th>FOCAL 1</th>
                        <th>FOCAL 2</th>
                        <th>DATA INICIAL</th>
                        <th>SERVIÇOS</th>
                        <th>LICENÇAS</th>
                        <th>ÚLT. RENOVAÇÃO</th>
                        <th>DURAÇÃO</th>
                        <th>STATUS</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(linhas)}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    return html_final

@st.cache_data(ttl=600)
def criar_grafico_pizza(cache_signature, coluna, titulo=""):
    df = st.session_state.df_filtrado
    dados = df[coluna].value_counts().reset_index()
    dados.columns = ['Label', 'Valor']

    if coluna == 'OPERADORA':
        color_map = {'CLARO': COLORS['claro'], 'VIVO': COLORS['vivo'], 
                    'TIM': COLORS['tim'], 'OI': COLORS['oi'], 'ALGAR': COLORS['algar']}
    elif coluna == 'CATEGORIA_CONEXAO':
        color_map = {'Nunca Conectou': COLORS['danger'], 'Mais de 180 dias': COLORS['warning'],
                    '91-180 dias': COLORS['info'], '31-90 dias': COLORS['light_green'], 
                    '0-30 dias': COLORS['accent']}
    else:
        color_map = {}

    colors = [color_map.get(label, COLORS['gray']) for label in dados['Label']]

    fig = go.Figure(data=[go.Pie(
        labels=dados['Label'], values=dados['Valor'], hole=0.55,
        marker=dict(colors=colors, line=dict(color='white', width=3)),
        textfont=dict(size=14, family='Inter', color='#1a1a1a'),
        textinfo='label+percent'
    )])

    fig.add_annotation(
        text=f'<b style="font-size:28px">{dados["Valor"].sum():,.0f}</b><br><span style="font-size:14px">{titulo}</span>',
        x=0.5, y=0.5, showarrow=False, font=dict(family='Inter', color='#1a1a1a')
    )

    fig.update_layout(
        showlegend=True, height=340,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    return fig

@st.cache_data(ttl=600)
def criar_grafico_barras(cache_signature, coluna):
    df = st.session_state.df_filtrado
    dados = df[coluna].value_counts().head(10).reset_index()
    dados.columns = ['Label', 'Valor']
    dados = dados.sort_values('Valor', ascending=True)

    fig = go.Figure(data=[go.Bar(
        y=dados['Label'], x=dados['Valor'], orientation='h',
        marker=dict(
            color=dados['Valor'],
            colorscale=[[0, 'rgba(197,225,165,0.9)'], [0.5, 'rgba(139,195,74,1)'], [1, 'rgba(46,125,50,1)']],
            showscale=False, line=dict(color='white', width=2)
        ),
        text=[f'<b>{v:,.0f}</b>' for v in dados['Valor']],
        textposition='outside',
        textfont=dict(size=12, family='Inter', color='#1a1a1a')
    )])

    fig.update_layout(
        showlegend=False, height=340,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=140, r=60, t=10, b=30),
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(showgrid=False)
    )
    return fig

@st.cache_data(ttl=600)
def criar_timeline_vencimentos(cache_signature):
    df = st.session_state.df_filtrado
    hoje = pd.Timestamp.now().normalize()
    df_venc = df[df['DATA DE VENCIMENTO'].notna()].copy()
    df_venc = df_venc[df_venc['DATA DE VENCIMENTO'] > hoje]

    if df_venc.empty:
        return go.Figure()

    prox_ano = hoje + pd.DateOffset(months=12)
    df_prox = df_venc[df_venc['DATA DE VENCIMENTO'] <= prox_ano]
    df_prox['mes'] = df_prox['DATA DE VENCIMENTO'].dt.to_period('M')
    venc_mensal = df_prox.groupby('mes').size().reset_index(name='Quantidade')
    venc_mensal['mes'] = venc_mensal['mes'].dt.to_timestamp()

    fig = go.Figure(data=[go.Scatter(
        x=venc_mensal['mes'], y=venc_mensal['Quantidade'],
        # MELHORIA #5: Rótulos visíveis na timeline de vencimentos
        mode='lines+markers+text',
        text=venc_mensal['Quantidade'],
        textposition='top center', fill='tozeroy',
        fillcolor='rgba(229, 115, 115, 0.2)',
        line=dict(color=COLORS['danger'], width=4),
        marker=dict(size=10, color=COLORS['danger'], line=dict(color='white', width=2))
    )])

    fig.update_layout(
        showlegend=False, height=340,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=30, t=10, b=50)
    )
    return fig

def criar_timeline_projetos(df_timeline, filtro_projetos=None, filtro_acoes=None, data_inicio=None, data_fim=None):
    if df_timeline is None or df_timeline.empty:
        return go.Figure()

    df_filtrado = df_timeline.copy()

    if filtro_projetos:
        df_filtrado = df_filtrado[df_filtrado['PROJETO'].isin(filtro_projetos)]
    if filtro_acoes:
        df_filtrado = df_filtrado[df_filtrado['AÇÃO'].isin(filtro_acoes)]
    if data_inicio:
        df_filtrado = df_filtrado[df_filtrado['DATA'] >= pd.Timestamp(data_inicio)]
    if data_fim:
        df_filtrado = df_filtrado[df_filtrado['DATA'] <= pd.Timestamp(data_fim)]

    if df_filtrado.empty:
        return go.Figure()

    fig = go.Figure()

    for acao in df_filtrado['AÇÃO'].unique():
        df_acao = df_filtrado[df_filtrado['AÇÃO'] == acao]
        cor = CORES_ACAO.get(acao, COLORS['gray'])

        fig.add_trace(go.Scatter(
            x=df_acao['DATA'], y=df_acao['QUANTIDADE'],
            mode='markers+text', name=acao,
            marker=dict(size=14, color=cor, line=dict(color='white', width=2)),
            text=df_acao['PROJETO'], textposition='top center',
            textfont=dict(size=10, color='#1a1a1a', family='Inter'),
            hovertemplate='<b>%{text}</b><br>%{y:,.0f} licenças<br>%{x|%d/%m/%Y}<extra></extra>'
        ))

    fig.update_layout(
        showlegend=True, height=500,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=30, t=20, b=50),
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)', title='Quantidade'),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

@st.cache_data(ttl=600)
def criar_gauge_health(cache_signature, health_score):
    if health_score >= 76:
        color, status = COLORS['accent'], "Excelente"
    elif health_score >= 51:
        color, status = COLORS['warning'], "Atenção"
    else:
        color, status = COLORS['danger'], "Crítico"

    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=health_score,
        title={'text': f"<b>{status}</b>", 'font': {'size': 18}},
        number={'suffix': "%", 'font': {'size': 42, 'color': color}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': 'rgba(229,115,115,0.2)'},
                {'range': [50, 75], 'color': 'rgba(255,183,77,0.2)'},
                {'range': [75, 100], 'color': 'rgba(139,195,74,0.2)'}
            ]
        }
    ))
    fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=50, b=10))
    return fig

@st.cache_data(ttl=600)
def criar_top_projetos_risco(cache_signature):
    df = st.session_state.df_filtrado
    hoje = pd.Timestamp.now().normalize()
    limite_30d = hoje + pd.Timedelta(days=30)

    df_risco = df[(df['DATA DE VENCIMENTO'] > hoje) & (df['DATA DE VENCIMENTO'] <= limite_30d)]
    if df_risco.empty:
        return go.Figure()

    top_risco = df_risco.groupby('PROJETO').size().nlargest(5).reset_index(name='Em Risco')
    top_risco = top_risco.sort_values('Em Risco', ascending=True)

    fig = go.Figure(data=[go.Bar(
        y=top_risco['PROJETO'], x=top_risco['Em Risco'], orientation='h',
        marker=dict(
            color=top_risco['Em Risco'],
            colorscale=[[0, 'rgba(255,183,77,0.8)'], [1, 'rgba(229,115,115,1)']],
            showscale=False
        ),
        text=[f'<b>{v:,.0f}</b>' for v in top_risco['Em Risco']],
        textposition='outside'
    )])

    fig.update_layout(
        showlegend=False, height=300,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=120, r=40, t=10, b=30)
    )
    return fig

def gerar_alertas(df):
    alertas = []
    hoje = pd.Timestamp.now().normalize()

    venc_30 = df[(df['DATA DE VENCIMENTO'] > hoje) & 
                 (df['DATA DE VENCIMENTO'] <= hoje + pd.Timedelta(days=30))]
    if len(venc_30) > 0:
        alertas.append(("warning", f"⚠️ {len(venc_30)} licenças vencem em 30 dias"))

    if 'CATEGORIA_CONEXAO' in df.columns:
        sem_conexao = df[df['CATEGORIA_CONEXAO'] == 'Mais de 180 dias']
        if len(sem_conexao) > 0:
            alertas.append(("error", f"🔴 {len(sem_conexao)} chips sem conexão há 180+ dias"))

    if 'STATUS_LICENCA' in df.columns:
        expiradas = df[df['STATUS_LICENCA'] == 'Expirado']
        if len(expiradas) > 0:
            alertas.append(("error", f"❌ {len(expiradas)} licenças expiradas"))

    return alertas

def gerar_alertas_contratuais():
    if st.session_state.df_contratos is None:
        return []

    alertas = []
    df = st.session_state.df_contratos

    expirados = df[df['STATUS ATUAL DO CONTRATO'] == 'EXPIRADO']
    if len(expirados) > 0:
        alertas.append(("error", f"🔴 {len(expirados)} contrato(s) EXPIRADO(S)"))

    expirando = df[df['STATUS ATUAL DO CONTRATO'] == 'EXPIRANDO']
    if len(expirando) > 0:
        alertas.append(("warning", f"⚠️ {len(expirando)} contrato(s) EXPIRANDO"))

    df_entregas = calcular_entregas_por_projeto()
    if not df_entregas.empty:
        baixa_entrega = df_entregas[df_entregas['% ENTREGUES'] < 80]
        if len(baixa_entrega) > 0:
            alertas.append(("warning", f"📉 {len(baixa_entrega)} projeto(s) com <80% de entregas"))

        baixa_funcional = df_entregas[df_entregas['% FUNCIONAIS'] < 70]
        if len(baixa_funcional) > 0:
            alertas.append(("error", f"⚙️ {len(baixa_funcional)} projeto(s) com <70% de licenças funcionais"))

    return alertas

# SESSION STATE
if 'df_base' not in st.session_state:
    st.session_state.df_base = None
if 'df_filtrado' not in st.session_state:
    st.session_state.df_filtrado = None
if 'df_contratos' not in st.session_state:
    st.session_state.df_contratos = None
if 'df_timeline' not in st.session_state:
    st.session_state.df_timeline = None
if 'filtros_ativos' not in st.session_state:
    st.session_state.filtros_ativos = {}
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = 'dashboard'
if 'timeline_expandida' not in st.session_state:
    st.session_state.timeline_expandida = False

aplicar_css()
logo_icon = load_logo(["BM-Icone.png", "BM Ícone.png"])

# SIDEBAR
with st.sidebar:
    if logo_icon:
        st.markdown(f'<div style="text-align:center; padding:1.2rem; background:rgba(255,255,255,0.1); border-radius:14px; margin-bottom:1.5rem;"><img src="data:image/png;base64,{logo_icon}" style="max-width:90px;"></div>', unsafe_allow_html=True)

    st.markdown("### 📊 Base Mobile")
    st.caption("Gestão Integrada • Projetos e Serviços")
    st.markdown("---")

    st.markdown("### 🎯 Navegação")

    if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.pagina_atual == 'dashboard' else "secondary"):
        st.session_state.pagina_atual = 'dashboard'
        st.rerun()

    if st.button("📋 Dados Contratuais", use_container_width=True, type="primary" if st.session_state.pagina_atual == 'contratos' else "secondary"):
        st.session_state.pagina_atual = 'contratos'
        st.rerun()
# ADIÇÃO DO CHATBOT - DELETAR SE FOR TIRAR 
    if st.button("🤖 Chatbot IA", use_container_width=True, 
                type="primary" if st.session_state.pagina_atual == "chatbot" else "secondary"):
        st.session_state.pagina_atual = "chatbot"
        st.rerun()


    st.markdown("---")

    # MELHORIA #1: Filtros sempre visíveis (mesmo durante carregamento/refresh)
    if st.session_state.pagina_atual == 'dashboard':
        st.markdown("### 🎛️ Filtros")

        carregando = (st.session_state.df_base is None)
        if carregando:
            st.info("⏳ Aguardando carregamento...")
            df_temp = pd.DataFrame(columns=['PROJETO','OPERADORA','STATUS NA OP.','STATUS_LICENCA'])
        else:
            df_temp = st.session_state.df_base

        filtros_temp = {}

        projetos_sel = st.multiselect(
            "Projetos",
            options=sorted(df_temp['PROJETO'].dropna().unique()) if 'PROJETO' in df_temp.columns else [],
            default=st.session_state.filtros_ativos.get('projetos', []),
            disabled=carregando
        )
        filtros_temp['projetos'] = projetos_sel

        operadoras_sel = st.multiselect(
            "Operadoras",
            options=sorted(df_temp['OPERADORA'].dropna().unique()) if 'OPERADORA' in df_temp.columns else [],
            default=st.session_state.filtros_ativos.get('operadoras', []),
            disabled=carregando
        )
        filtros_temp['operadoras'] = operadoras_sel

        if 'STATUS NA OP.' in df_temp.columns:
            status_op_sel = st.multiselect(
                "Status OP",
                options=sorted(df_temp['STATUS NA OP.'].dropna().unique()),
                default=st.session_state.filtros_ativos.get('status_op', []),
                disabled=carregando
            )
            filtros_temp['status_op'] = status_op_sel
        else:
            filtros_temp['status_op'] = []

        # Mantém o rótulo original (não muda o texto/visual)
        if 'STATUS_LICENCA' in df_temp.columns:
            status_lic_sel = st.multiselect(
                "Status Licença",
                options=['Válido','Expirado'],
                default=st.session_state.filtros_ativos.get('status_licenca', []),
                disabled=carregando
            )
            filtros_temp['status_licenca'] = status_lic_sel
        else:
            filtros_temp['status_licenca'] = []

        if carregando:
            st.caption("Preview: ⏳ aguardando base")
        else:
            preview_count = calcular_preview(df_temp, filtros_temp)
            st.caption(f"Preview: {format_number(preview_count)} registros")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Aplicar", use_container_width=True, type="primary", disabled=carregando):
                st.session_state.filtros_ativos = filtros_temp.copy()
                st.session_state.df_filtrado = None
                st.rerun()
        with col2:
            if st.button("Limpar", use_container_width=True, disabled=carregando):
                st.session_state.filtros_ativos = {}
                st.session_state.df_filtrado = None
                st.rerun()

        if any(st.session_state.filtros_ativos.values()):
            st.markdown("---")
            st.markdown("#### 🏷️ Filtros Ativos")
            chips = ""
            for filtro, valores in st.session_state.filtros_ativos.items():
                if valores:
                    for v in valores:
                        chips += f"<span class='filter-chip'>{v}</span>"
            st.markdown(chips, unsafe_allow_html=True)

        st.markdown("---")

    if st.button("Recarregar Tudo", use_container_width=True, key='btn_recarregar_tudo'):
        st.cache_data.clear()
        # FIX: não usar session_state.clear() (causa reempilhamento de widgets)
        st.session_state.df_base = None
        st.session_state.df_filtrado = None
        st.session_state.df_contratos = None
        st.session_state.df_timeline = None
        st.session_state.filtros_ativos = {}
        st.session_state.timeline_expandida = False
        st.rerun()

# CARREGAMENTO
# CARREGAMENTO
if st.session_state.df_base is None:
    loading = st.empty()
    loading.markdown(show_premium_loading("Carregando Bases"), unsafe_allow_html=True)
    st.session_state.df_base, _ = load_data_smart()
    st.session_state.df_contratos, st.session_state.df_timeline = load_dados_gerenciais()
    loading.empty()
    # MELHORIA #1: garante refresh da sidebar após o carregamento (evita 'Aguardando carregamento...' infinito)
    st.rerun()

# PÁGINA: DASHBOARD
if st.session_state.pagina_atual == 'dashboard':
    st.markdown("""
    <div class="header-parallax">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">📊</div>
            <div>
                <h1 style="color: white; font-size: 2rem; font-weight: 900; margin: 0;">Dashboard de Licenças</h1>
                <p style="color: #C5E1A5; font-size: 0.95rem; margin: 0.3rem 0 0 0; font-weight: 600;">Analytics & Business Intelligence • Base Mobile</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = st.session_state.df_base

    if df.empty:
        st.error("❌ Arquivo não encontrado: **MAPEAMENTO DE CHIPS.xlsx**")
        st.stop()

    if st.session_state.df_filtrado is None:
        st.session_state.df_filtrado = aplicar_filtros(df, st.session_state.filtros_ativos)

    df_filtrado = st.session_state.df_filtrado

    st.success(f"✅ **Visualizando:** {format_number(len(df_filtrado))} de {format_number(len(df))} registros")
    st.markdown("---")

    # MÉTRICAS
    st.markdown("### 🎯 Indicadores Estratégicos")

    cache_sig = get_cache_signature(st.session_state.filtros_ativos)
    metricas = calcular_metricas_cached(cache_sig)

    cols = st.columns(6)
    cards = [
        ("📋", "Total", metricas['total'], COLORS['secondary'], None),
        ("🔗", "Vinculadas", metricas['vinculadas'], COLORS['accent'], None),
        ("📊", "Taxa", f"{metricas['perc_vinculadas']:.0f}%", COLORS['info'], None),
        ("⚖️", "Saldo", metricas['saldo'], COLORS['warning'], None),
        ("✅", "Válidas", metricas['validas'], COLORS['dark_green'], "+12%"),
        ("❌", "Expiradas", metricas['expiradas'], COLORS['danger'], "-5%")
    ]

    for i, (icon, label, value, cor, delta) in enumerate(cards):
        with cols[i]:
            delta_html = f'<div class="metric-delta positive">{delta} ▲</div>' if delta and delta.startswith('+') else (f'<div class="metric-delta negative">{delta} ▼</div>' if delta else '')
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon" style="color: {cor};">{icon}</div>
                <div class="metric-value" style="color: {cor};">{value if isinstance(value, str) else format_number(value)}</div>
                <div class="metric-label">{label}</div>
                {delta_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # HEALTH SCORE
    st.markdown("### 🏥 Indicadores de Saúde")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(criar_gauge_health(cache_sig, metricas['health_score']), use_container_width=True)

    with col2:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); padding: 2rem; border-radius: 16px; text-align: center;">
            <div style="font-size: 3.5rem; font-weight: 900; color: {COLORS['accent']};">{metricas['taxa_utilizacao']}%</div>
            <div style="font-size: 0.9rem; color: #666;">Taxa de Utilização</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); padding: 2rem; border-radius: 16px; text-align: center;">
            <div style="font-size: 3.5rem; font-weight: 900; color: {COLORS['secondary']};">{format_number(metricas['conectadas_30d'])}</div>
            <div style="font-size: 0.9rem; color: #666;">Chips Ativos 30d</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ALERTAS
    alertas = gerar_alertas(df_filtrado)
    alertas_contratos = gerar_alertas_contratuais()

    # MELHORIA #3: Alertas em expander (sino clicável + contador)
    total_alertas = len(alertas) + len(alertas_contratos)
    with st.expander(f"🔔 Alertas ({total_alertas})", expanded=False):
        if total_alertas == 0:
            st.success("Nenhum alerta no momento.")
        else:
            for tipo, msg in alertas + alertas_contratos:
                if tipo == "warning":
                    st.warning(msg)
                else:
                    st.error(msg)
    st.markdown("---")

    # GRÁFICOS
    st.markdown("### 📊 Análises Visuais")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📡 Distribuição por Operadora")
        if 'OPERADORA' in df_filtrado.columns:
            st.plotly_chart(criar_grafico_pizza(cache_sig, 'OPERADORA', 'Total'), use_container_width=True)

        st.markdown("#### 🔌 Status Operadora")
        if 'STATUS NA OP.' in df_filtrado.columns:
            st.plotly_chart(criar_grafico_barras(cache_sig, 'STATUS NA OP.'), use_container_width=True)

    with col2:
        st.markdown("#### 🔄 Última Conexão")
        if 'CATEGORIA_CONEXAO' in df_filtrado.columns:
            st.plotly_chart(criar_grafico_pizza(cache_sig, 'CATEGORIA_CONEXAO', 'Total'), use_container_width=True)

        st.markdown("#### 📅 Timeline Vencimentos")
        st.plotly_chart(criar_timeline_vencimentos(cache_sig), use_container_width=True)

    # MELHORIA #6: Top 10 e Top 5 lado a lado (50/50)
    col_top10, col_top5 = st.columns(2)
    with col_top10:
        st.markdown("#### 🏆 Top 10 Projetos")
        st.plotly_chart(criar_grafico_barras(cache_sig, 'PROJETO'), use_container_width=True)
    with col_top5:
        st.markdown("### ⚠️ Top 5 Projetos em Risco")
        fig_risco = criar_top_projetos_risco(cache_sig)
        if fig_risco.data:
            st.plotly_chart(fig_risco, use_container_width=True)
        else:
            st.success("✅ Nenhum projeto com vencimentos críticos!")

    st.markdown("---")

    # PAINEL DE ENTREGAS
    st.markdown("### 📦 Painel de Entregas por Projeto")
    df_entregas = calcular_entregas_por_projeto()

    if not df_entregas.empty:
        html_tabela = gerar_html_tabela_entregas(df_entregas)
        components.html(html_tabela, height=600, scrolling=True)
    else:
        st.info("ℹ️ Dados contratuais não disponíveis para calcular entregas.")

    st.markdown("---")

    # TIMELINE DE PROJETOS
    st.markdown("### 📅 Timeline de Projetos")

    if st.session_state.df_timeline is not None and not st.session_state.df_timeline.empty:
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        with col1:
            projetos_timeline = st.multiselect(
                "📍 Filtrar Projetos",
                options=sorted(st.session_state.df_timeline['PROJETO'].unique()),
                default=[],
                key='filtro_timeline_projetos'
            )

        with col2:
            acoes_timeline = st.multiselect(
                "🎯 Filtrar Tipo de Ação",
                options=sorted(st.session_state.df_timeline['AÇÃO'].unique()),
                default=[],
                key='filtro_timeline_acoes'
            )

        with col3:
            data_min = st.session_state.df_timeline['DATA'].min().date()
            data_max = st.session_state.df_timeline['DATA'].max().date()

            range_datas = st.date_input(
                "📆 Período",
                value=(data_min, data_max),
                min_value=data_min,
                max_value=data_max,
                key='filtro_timeline_datas'
            )

        with col4:
            if st.button("🔍 Expandir Detalhes", use_container_width=True):
                st.session_state.timeline_expandida = not st.session_state.timeline_expandida

        data_inicio = range_datas[0] if isinstance(range_datas, tuple) and len(range_datas) == 2 else None
        data_fim = range_datas[1] if isinstance(range_datas, tuple) and len(range_datas) == 2 else range_datas

        fig_timeline = criar_timeline_projetos(
            st.session_state.df_timeline,
            filtro_projetos=projetos_timeline if projetos_timeline else None,
            filtro_acoes=acoes_timeline if acoes_timeline else None,
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        st.plotly_chart(fig_timeline, use_container_width=True)

        if st.session_state.timeline_expandida:
            st.markdown("#### 📋 Tabela Detalhada")

            df_timeline_vis = st.session_state.df_timeline.copy()

            if projetos_timeline:
                df_timeline_vis = df_timeline_vis[df_timeline_vis['PROJETO'].isin(projetos_timeline)]
            if acoes_timeline:
                df_timeline_vis = df_timeline_vis[df_timeline_vis['AÇÃO'].isin(acoes_timeline)]
            if data_inicio:
                df_timeline_vis = df_timeline_vis[df_timeline_vis['DATA'] >= pd.Timestamp(data_inicio)]
            if data_fim:
                df_timeline_vis = df_timeline_vis[df_timeline_vis['DATA'] <= pd.Timestamp(data_fim)]

            df_timeline_vis = df_timeline_vis.sort_values('DATA', ascending=False)

            df_timeline_display = df_timeline_vis[['PROJETO', 'AÇÃO', 'DATA', 'QUANTIDADE']].copy()
            df_timeline_display['DATA'] = df_timeline_display['DATA'].dt.strftime('%d/%m/%Y')
            df_timeline_display['QUANTIDADE'] = df_timeline_display['QUANTIDADE'].apply(format_number)

            st.dataframe(df_timeline_display, use_container_width=True, height=340, hide_index=True)
    else:
        st.info("ℹ️ Timeline não disponível. Adicione o arquivo DADOS-GERENCIAIS.xlsx")

    st.markdown("---")
    st.markdown(f'<p style="text-align:center; color:#999;"> Base Mobile v6.4 • {datetime.now().strftime("%d/%m/%Y")} • Todos os direitos reservados </p>', unsafe_allow_html=True)

# PÁGINA: DADOS CONTRATUAIS
elif st.session_state.pagina_atual == 'contratos':
    st.markdown("""
    <div class="header-parallax">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">📋</div>
            <div>
                <h1 style="color: white; font-size: 2rem; font-weight: 900; margin: 0;">Dados Contratuais</h1>
                <p style="color: #C5E1A5; font-size: 0.95rem; margin: 0.3rem 0 0 0; font-weight: 600;">Gestão de Contratos • Base Mobile</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.df_contratos is None or st.session_state.df_contratos.empty:
        st.error("❌ Arquivo não encontrado: **DADOS-GERENCIAIS.xlsx**")
        st.stop()

    df_contratos = st.session_state.df_contratos

    st.success(f"✅ **{len(df_contratos)} contratos** cadastrados")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.multiselect(
            "🔍 Filtrar por Status",
            options=sorted(df_contratos['STATUS ATUAL DO CONTRATO'].unique()),
            default=[]
        )

    with col2:
        focal_filter = st.multiselect(
            "👤 Filtrar por Focal Point",
            options=sorted(df_contratos['FOCAL POINT 1'].unique()),
            default=[]
        )

    with col3:
        projeto_filter = st.multiselect(
            "📍 Filtrar por Projeto",
            options=sorted(df_contratos['PROJETO'].unique()),
            default=[]
        )

    df_vis = df_contratos.copy()
    if status_filter:
        df_vis = df_vis[df_vis['STATUS ATUAL DO CONTRATO'].isin(status_filter)]
    if focal_filter:
        df_vis = df_vis[df_vis['FOCAL POINT 1'].isin(focal_filter)]
    if projeto_filter:
        df_vis = df_vis[df_vis['PROJETO'].isin(projeto_filter)]

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total = len(df_vis)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="color: {COLORS['secondary']};">📋</div>
            <div class="metric-value" style="color: {COLORS['secondary']};">{total}</div>
            <div class="metric-label">Total Contratos</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        validos = len(df_vis[df_vis['STATUS ATUAL DO CONTRATO'] == 'VÁLIDO'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="color: {COLORS['accent']};">✅</div>
            <div class="metric-value" style="color: {COLORS['accent']};">{validos}</div>
            <div class="metric-label">Válidos</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        expirando = len(df_vis[df_vis['STATUS ATUAL DO CONTRATO'] == 'EXPIRANDO'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="color: {COLORS['warning']};">⚠️</div>
            <div class="metric-value" style="color: {COLORS['warning']};">{expirando}</div>
            <div class="metric-label">Expirando</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        expirados = len(df_vis[df_vis['STATUS ATUAL DO CONTRATO'] == 'EXPIRADO'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="color: {COLORS['danger']};">❌</div>
            <div class="metric-value" style="color: {COLORS['danger']};">{expirados}</div>
            <div class="metric-label">Expirados</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # TABELA COM HTML ESTILIZADO (IGUAL ENTREGAS)
    html_contratos = gerar_html_tabela_contratos(df_vis)
    components.html(html_contratos, height=700, scrolling=True)

    st.markdown("---")
    st.markdown(f'<p style="text-align:center; color:#999;"> Base Mobile v6.4 • {datetime.now().strftime("%d/%m/%Y")} • Todos os direitos reservados </p>', unsafe_allow_html=True)
    
    # ==================== PÁGINA CHATBOT ====================
# ==================== PÁGINA CHATBOT ====================
elif st.session_state.pagina_atual == "chatbot":
    from chatbot_pplx import render_chatbot
    render_chatbot(
        df=st.session_state.df_filtrado if st.session_state.df_filtrado is not None else st.session_state.df_base,
        dfcontratos=st.session_state.df_contratos,
        dftimeline=st.session_state.df_timeline
    )
    
    st.markdown("---")
    st.markdown(f'<p style="text-align:center; color:#999;"> Base Mobile v6.4 • {datetime.now().strftime("%d/%m/%Y")} • Todos os direitos reservados </p>', unsafe_allow_html=True)
