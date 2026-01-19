import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
from langchain_groq import ChatGroq
from io import BytesIO

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(
    page_title="Base Mobile - Dashboard Gerencial",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ESTILOS CSS ====================
st.markdown("""
<style>
    /* Cores Base Mobile */
    :root {
        --primary-green: #4CAF50;
        --secondary-green: #8BC34A;
        --dark-green: #2E7D32;
        --light-bg: #F5F5F5;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-weight: 700;
        margin: 0;
        font-size: 2.2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    
    /* Cards de Métricas */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #4CAF50;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2E7D32;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Gráficos */
    .plot-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #F5F5F5;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Chat */
    .chat-message {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #4CAF50;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
    }
    
    /* Filtros */
    .filter-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES DE CARREGAMENTO ====================

@st.cache_data(ttl=7200, show_spinner=False)
def carregar_dados_otimizado(uploaded_file):
    """Carrega dados do Excel com otimização máxima"""
    try:
        # Colunas necessárias (baseado no exemplo)
        colunas_usar = [
            'PROJETO', 'ICCID', 'ICCID ANTIGO', 'OPERADORA',
            'DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO',
            'ÚLTIMA CONEXÃO', 'STATUS NA OP.'
        ]
        
        # Parse de datas otimizado
        colunas_data = ['DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO', 'ÚLTIMA CONEXÃO']
        
        df = pd.read_excel(
            uploaded_file,
            usecols=colunas_usar,
            parse_dates=colunas_data,
            engine='openpyxl'
        )
        
        # Renomear para facilitar processamento
        df.columns = df.columns.str.strip().str.upper()
        
        # Normalizar OPERADORA (uppercase + primeira palavra)
        if 'OPERADORA' in df.columns:
            df['OPERADORA'] = df['OPERADORA'].astype(str).str.upper().str.split().str[0]
            # Mapeamento de operadoras conhecidas
            mapeamento_ops = {
                'ALGAR': 'ALGAR',
                'CLARO': 'CLARO',
                'VIVO': 'VIVO',
                'TIM': 'TIM',
                'OI': 'OI'
            }
            df['OPERADORA'] = df['OPERADORA'].map(lambda x: mapeamento_ops.get(x, x))
        
        # Calcular STATUS DA LICENÇA
        hoje = pd.Timestamp.now()
        df['STATUS_LICENCA'] = df['DATA DE VENCIMENTO'].apply(
            lambda x: 'Expirado' if pd.notna(x) and x < hoje else 'Válido'
        )
        
        # Calcular categoria de ÚLTIMA CONEXÃO
        def categorizar_conexao(data_conexao):
            if pd.isna(data_conexao):
                return 'Nunca Conectou'
            dias = (hoje - data_conexao).days
            if dias <= 30:
                return '0-30 dias'
            elif dias <= 60:
                return '31-60 dias'
            elif dias <= 90:
                return '61-90 dias'
            elif dias <= 180:
                return '91-180 dias'
            else:
                return 'Mais de 180 dias'
        
        df['CATEGORIA_CONEXAO'] = df['ÚLTIMA CONEXÃO'].apply(categorizar_conexao)
        
        # Normalizar STATUS NA OP
        if 'STATUS NA OP.' in df.columns:
            df['STATUS NA OP.'] = df['STATUS NA OP.'].astype(str).str.strip().str.title()
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return None

@st.cache_data(ttl=7200, show_spinner=False)
def agregar_dados_otimizado(df_hash, filtros_hash, versao=3):
    """Agrega dados com filtros aplicados - VERSÃO 3.0"""
    df = st.session_state.get('df_original')
    if df is None:
        return None
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    filtros = st.session_state.get('filtros_ativos', {})
    
    if filtros.get('projetos'):
        df_filtrado = df_filtrado[df_filtrado['PROJETO'].isin(filtros['projetos'])]
    
    if filtros.get('operadoras'):
        df_filtrado = df_filtrado[df_filtrado['OPERADORA'].isin(filtros['operadoras'])]
    
    if filtros.get('status_op'):
        df_filtrado = df_filtrado[df_filtrado['STATUS NA OP.'].isin(filtros['status_op'])]
    
    if filtros.get('status_licenca'):
        df_filtrado = df_filtrado[df_filtrado['STATUS_LICENCA'].isin(filtros['status_licenca'])]
    
    if filtros.get('data_venc_inicio'):
        df_filtrado = df_filtrado[df_filtrado['DATA DE VENCIMENTO'] >= filtros['data_venc_inicio']]
    
    if filtros.get('data_venc_fim'):
        df_filtrado = df_filtrado[df_filtrado['DATA DE VENCIMENTO'] <= filtros['data_venc_fim']]
    
    # Métricas principais
    metricas = {
        'total_licencas': len(df_filtrado),
        'licencas_validas': len(df_filtrado[df_filtrado['STATUS_LICENCA'] == 'Válido']),
        'licencas_expiradas': len(df_filtrado[df_filtrado['STATUS_LICENCA'] == 'Expirado']),
        'nunca_conectou': len(df_filtrado[df_filtrado['CATEGORIA_CONEXAO'] == 'Nunca Conectou']),
        'chips_ativos_op': len(df_filtrado[df_filtrado['STATUS NA OP.'] == 'Ativo']),
        'chips_suspensos_op': len(df_filtrado[df_filtrado['STATUS NA OP.'] == 'Suspenso'])
    }
    
    # Distribuição por Operadora
    dist_operadora = df_filtrado.groupby('OPERADORA', as_index=False).size()
    dist_operadora.columns = ['OPERADORA', 'QUANTIDADE']
    dist_operadora['PERCENTUAL'] = (dist_operadora['QUANTIDADE'] / dist_operadora['QUANTIDADE'].sum() * 100).round(2)
    
    # Status nas Operadoras
    dist_status_op = df_filtrado.groupby('STATUS NA OP.', as_index=False).size()
    dist_status_op.columns = ['STATUS', 'QUANTIDADE']
    dist_status_op['PERCENTUAL'] = (dist_status_op['QUANTIDADE'] / dist_status_op['QUANTIDADE'].sum() * 100).round(2)
    
    # Análise de Conexões
    dist_conexao = df_filtrado.groupby('CATEGORIA_CONEXAO', as_index=False).size()
    dist_conexao.columns = ['CATEGORIA', 'QUANTIDADE']
    dist_conexao['PERCENTUAL'] = (dist_conexao['QUANTIDADE'] / dist_conexao['QUANTIDADE'].sum() * 100).round(2)
    
    # Ordem das categorias
    ordem_conexao = ['Nunca Conectou', 'Mais de 180 dias', '91-180 dias', '61-90 dias', '31-60 dias', '0-30 dias']
    dist_conexao['CATEGORIA'] = pd.Categorical(dist_conexao['CATEGORIA'], categories=ordem_conexao, ordered=True)
    dist_conexao = dist_conexao.sort_values('CATEGORIA')
    
    # Vencimentos por mês
    df_temp = df_filtrado[df_filtrado['DATA DE VENCIMENTO'].notna()].copy()
    df_temp['MES_VENCIMENTO'] = df_temp['DATA DE VENCIMENTO'].dt.to_period('M').astype(str)
    vencimentos_mes = df_temp.groupby('MES_VENCIMENTO', as_index=False).size()
    vencimentos_mes.columns = ['MES', 'QUANTIDADE']
    vencimentos_mes = vencimentos_mes.sort_values('MES')
    
    # Matriz de Vencimentos (Projeto x Mês)
    matriz_vencimentos = df_temp.groupby(['PROJETO', 'MES_VENCIMENTO'], as_index=False).size()
    matriz_vencimentos.columns = ['PROJETO', 'MES', 'QUANTIDADE']
    
    # Chips Críticos (Válidos + Nunca Conectaram)
    chips_criticos = df_filtrado[
        (df_filtrado['STATUS_LICENCA'] == 'Válido') & 
        (df_filtrado['CATEGORIA_CONEXAO'] == 'Nunca Conectou')
    ]
    
    # Chips Válidos mas Suspensos
    chips_validos_suspensos = df_filtrado[
        (df_filtrado['STATUS_LICENCA'] == 'Válido') & 
        (df_filtrado['STATUS NA OP.'] == 'Suspenso')
    ]
    
    return {
        'df_filtrado': df_filtrado,
        'metricas': metricas,
        'dist_operadora': dist_operadora,
        'dist_status_op': dist_status_op,
        'dist_conexao': dist_conexao,
        'vencimentos_mes': vencimentos_mes,
        'matriz_vencimentos': matriz_vencimentos,
        'chips_criticos': chips_criticos,
        'chips_validos_suspensos': chips_validos_suspensos
    }

# ==================== FUNÇÕES DE VISUALIZAÇÃO ====================

def criar_grafico_operadora(dados):
    """Gráfico de Pizza - Distribuição por Operadora"""
    df = dados['dist_operadora']
    
    cores_operadoras = {
        'VIVO': '#660099',
        'CLARO': '#FF0000',
        'TIM': '#0033A0',
        'ALGAR': '#00A859',
        'OI': '#FFD700'
    }
    
    cores = [cores_operadoras.get(op, '#999999') for op in df['OPERADORA']]
    
    fig = go.Figure(data=[go.Pie(
        labels=df['OPERADORA'],
        values=df['QUANTIDADE'],
        hole=0.4,
        marker=dict(colors=cores),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=14, color='#333'),
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value:,.0f}<br>Percentual: %{percent}<extra></extra>'
    )])
    
    total = df['QUANTIDADE'].sum()
    
    fig.add_annotation(
        text=f'<b>{total:,.0f}</b><br>Licenças',
        x=0.5, y=0.5,
        font=dict(size=20, color='#2E7D32'),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(text='Distribuição por Operadora', font=dict(size=18, color='#333')),
        showlegend=True,
        height=400,
        margin=dict(t=80, b=40, l=40, r=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_grafico_status_op(dados):
    """Gráfico de Barras Horizontal - Status nas Operadoras"""
    df = dados['dist_status_op'].sort_values('QUANTIDADE', ascending=True)
    
    # Cores baseadas no dashboard validado
    cores_status = {
        'Ativo': '#4CAF50',
        'Bloqueado': '#8BC34A',
        'Suspenso': '#CDDC39',
        'Cancelado': '#AED581',
        'Não Está Na Operadora': '#E0E0E0'
    }
    
    cores = [cores_status.get(status, '#999999') for status in df['STATUS']]
    
    fig = go.Figure(data=[go.Bar(
        y=df['STATUS'],
        x=df['QUANTIDADE'],
        orientation='h',
        marker=dict(color=cores),
        text=[f"{q:,.0f} ({p:.1f}%)" for q, p in zip(df['QUANTIDADE'], df['PERCENTUAL'])],
        textposition='outside',
        textfont=dict(size=13, color='#333'),
        hovertemplate='<b>%{y}</b><br>Quantidade: %{x:,.0f}<br>Percentual: %{customdata:.2f}%<extra></extra>',
        customdata=df['PERCENTUAL']
    )])
    
    fig.update_layout(
        title=dict(text='Status das Licenças nas Operadoras', font=dict(size=18, color='#333')),
        xaxis=dict(title='Quantidade', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(title=''),
        height=350,
        margin=dict(t=80, b=60, l=150, r=100),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_grafico_conexoes(dados):
    """Gráfico de Rosca - Análise de Conexões"""
    df = dados['dist_conexao']
    
    # Cores baseadas na criticidade
    cores_conexao = {
        'Nunca Conectou': '#D32F2F',
        'Mais de 180 dias': '#F57C00',
        '91-180 dias': '#FBC02D',
        '61-90 dias': '#AFB42B',
        '31-60 dias': '#7CB342',
        '0-30 dias': '#388E3C'
    }
    
    cores = [cores_conexao.get(cat, '#999999') for cat in df['CATEGORIA']]
    
    fig = go.Figure(data=[go.Pie(
        labels=df['CATEGORIA'],
        values=df['QUANTIDADE'],
        hole=0.5,
        marker=dict(colors=cores),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=13, color='#333'),
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value:,.0f}<br>Percentual: %{percent}<extra></extra>'
    )])
    
    total = df['QUANTIDADE'].sum()
    com_conexao = df[df['CATEGORIA'] != 'Nunca Conectou']['QUANTIDADE'].sum()
    perc_conexao = (com_conexao / total * 100) if total > 0 else 0
    
    fig.add_annotation(
        text=f'<b>{com_conexao:,.0f}</b><br>{perc_conexao:.1f}%<br>com conexão',
        x=0.5, y=0.5,
        font=dict(size=16, color='#2E7D32'),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(text='Análise de Conexões das Licenças', font=dict(size=18, color='#333')),
        showlegend=True,
        height=450,
        margin=dict(t=80, b=40, l=40, r=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_grafico_vencimentos(dados):
    """Gráfico de Área - Vencimentos por Mês"""
    df = dados['vencimentos_mes'].head(12)  # Próximos 12 meses
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['MES'],
        y=df['QUANTIDADE'],
        mode='lines+markers+text',
        fill='tozeroy',
        fillcolor='rgba(76, 175, 80, 0.2)',
        line=dict(color='#4CAF50', width=3),
        marker=dict(size=10, color='#2E7D32'),
        text=[f'{q:,.0f}' for q in df['QUANTIDADE']],
        textposition='top center',
        textfont=dict(size=12, color='#333'),
        hovertemplate='<b>%{x}</b><br>Vencimentos: %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text='Projeção de Vencimentos (Próximos 12 Meses)', font=dict(size=18, color='#333')),
        xaxis=dict(
            title='Mês',
            showgrid=False,
            tickangle=-45
        ),
        yaxis=dict(
            title='Quantidade',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)'
        ),
        height=400,
        margin=dict(t=80, b=100, l=80, r=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_heatmap_vencimentos(dados):
    """Heatmap - Matriz de Vencimentos (Projeto x Mês)"""
    df = dados['matriz_vencimentos']
    
    # Pivot para criar matriz
    pivot = df.pivot_table(
        index='PROJETO',
        columns='MES',
        values='QUANTIDADE',
        fill_value=0,
        aggfunc='sum'
    )
    
    # Limitar a 12 meses
    pivot = pivot.iloc[:, :12]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Greens',
        text=pivot.values,
        texttemplate='%{text}',
        textfont=dict(size=10),
        hovertemplate='<b>%{y}</b><br>Mês: %{x}<br>Vencimentos: %{z}<extra></extra>',
        colorbar=dict(title='Quantidade')
    ))
    
    fig.update_layout(
        title=dict(text='Matriz de Vencimentos por Projeto', font=dict(size=18, color='#333')),
        xaxis=dict(title='Mês', tickangle=-45),
        yaxis=dict(title='Projeto'),
        height=max(400, len(pivot) * 30),
        margin=dict(t=80, b=100, l=200, r=80),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_grafico_sankey(dados):
    """Diagrama de Sankey - Fluxo Status Licença → Status OP → Conexão"""
    df = dados['df_filtrado']
    
    # Criar agregação
    fluxo = df.groupby(['STATUS_LICENCA', 'STATUS NA OP.', 'CATEGORIA_CONEXAO'], as_index=False).size()
    fluxo.columns = ['STATUS_LIC', 'STATUS_OP', 'CONEXAO', 'VALOR']
    
    # Criar nós únicos
    nos = []
    nos_map = {}
    idx = 0
    
    # Status Licença
    for status in fluxo['STATUS_LIC'].unique():
        nos.append(f"Licença: {status}")
        nos_map[('lic', status)] = idx
        idx += 1
    
    # Status OP
    for status in fluxo['STATUS_OP'].unique():
        nos.append(f"OP: {status}")
        nos_map[('op', status)] = idx
        idx += 1
    
    # Conexão
    for cat in fluxo['CONEXAO'].unique():
        nos.append(f"Conexão: {cat}")
        nos_map[('con', cat)] = idx
        idx += 1
    
    # Criar links
    source = []
    target = []
    value = []
    
    # Licença → OP
    for _, row in fluxo.groupby(['STATUS_LIC', 'STATUS_OP'])['VALOR'].sum().reset_index().iterrows():
        source.append(nos_map[('lic', row['STATUS_LIC'])])
        target.append(nos_map[('op', row['STATUS_OP'])])
        value.append(row['VALOR'])
    
    # OP → Conexão
    for _, row in fluxo.groupby(['STATUS_OP', 'CONEXAO'])['VALOR'].sum().reset_index().iterrows():
        source.append(nos_map[('op', row['STATUS_OP'])])
        target.append(nos_map[('con', row['CONEXAO'])])
        value.append(row['VALOR'])
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            label=nos,
            color='#4CAF50'
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color='rgba(76, 175, 80, 0.3)'
        )
    )])
    
    fig.update_layout(
        title=dict(text='Fluxo: Status Licença → Status OP → Conexão', font=dict(size=18, color='#333')),
        height=600,
        margin=dict(t=80, b=40, l=40, r=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# ==================== ASSISTENTE IA ====================

@st.cache_resource(show_spinner=False)
def init_llm():
    """Inicializa LLM com Groq"""
    try:
        if "GROQ_API_KEY" not in st.secrets:
            st.warning("⚠️ Configure GROQ_API_KEY nas secrets do Streamlit")
            return None
        
        llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0,
            groq_api_key=st.secrets["GROQ_API_KEY"],
            max_tokens=600
        )
        
        return llm
        
    except Exception as e:
        st.error(f"❌ Erro ao inicializar Groq: {str(e)}")
        return None

def gerar_contexto_gerencial(dados):
    """Gera contexto estruturado para o assistente"""
    metricas = dados['metricas']
    df_filtrado = dados['df_filtrado']
    
    # Resumo por projeto
    resumo_projetos = df_filtrado.groupby('PROJETO').agg({
        'ICCID': 'count',
        'OPERADORA': lambda x: x.mode()[0] if len(x) > 0 else 'N/A',
        'STATUS_LICENCA': lambda x: (x == 'Válido').sum(),
        'CATEGORIA_CONEXAO': lambda x: (x != 'Nunca Conectou').sum()
    }).reset_index()
    
    resumo_projetos.columns = ['Projeto', 'Total_Linhas', 'Operadora_Principal', 'Linhas_Validas', 'Linhas_Conectadas']
    
    contexto = f"""
# CONTEXTO BASE MOBILE - GESTÃO DE LICENÇAS

## GLOSSÁRIO DE TERMOS
- **PROJETO** = Estado/Cliente (ex: "Governo da Bahia" = projeto da Bahia)
- **ICCID = LINHA = LICENÇA = CHIP** (sinônimos)
- **ICCID ANTIGO** = Chips já substituídos (apenas contagem)
- **STATUS DA LICENÇA** = Válido (vencimento futuro) ou Expirado (vencimento passado)
- **STATUS NA OP** = Status do chip na operadora (Ativo/Suspenso/Bloqueado) - INDEPENDENTE do status da licença
- **ÚLTIMA CONEXÃO** = Data da última atividade do chip na rede

## MÉTRICAS GERAIS
- Total de Licenças: {metricas['total_licencas']:,}
- Licenças Válidas: {metricas['licencas_validas']:,}
- Licenças Expiradas: {metricas['licencas_expiradas']:,}
- Nunca Conectaram: {metricas['nunca_conectou']:,}
- Chips Ativos na OP: {metricas['chips_ativos_op']:,}
- Chips Suspensos na OP: {metricas['chips_suspensos_op']:,}

## DISTRIBUIÇÃO POR OPERADORA
{dados['dist_operadora'].to_string(index=False)}

## RESUMO POR PROJETO (TOP 10)
{resumo_projetos.head(10).to_string(index=False)}

## ANÁLISE DE CONEXÕES
{dados['dist_conexao'].to_string(index=False)}

## PRÓXIMOS VENCIMENTOS
{dados['vencimentos_mes'].head(6).to_string(index=False)}

## INSTRUÇÕES PARA RESPOSTAS
- Use SEMPRE tabelas Markdown para comparações e listas
- Formato exemplo:
  | Projeto | Total Linhas | Operadora | Conectadas | Vencimentos Fev/26 |
  |---------|--------------|-----------|------------|-------------------|
  | Bahia   | 5.234        | CLARO     | 4.890      | 1.234             |
  
- Para perguntas sobre vencimentos, agrupe por mês/ano
- Para análise de conexões, classifique por tempo desde última conexão
- Identifique chips críticos: válidos + nunca conectaram OU válidos + suspensos
"""
    
    return contexto

def processar_pergunta_ia(pergunta, dados):
    """Processa pergunta usando Groq"""
    llm = init_llm()
    if llm is None:
        return "❌ Assistente IA não disponível. Configure GROQ_API_KEY nas secrets."
    
    contexto = gerar_contexto_gerencial(dados)
    
    prompt = f"""{contexto}

## PERGUNTA DO USUÁRIO
{pergunta}

## IMPORTANTE
- Responda de forma GERENCIAL (formato executivo)
- Use tabelas Markdown sempre que possível
- Seja conciso mas completo
- Identifique insights e alertas importantes
- Ao falar de "linhas", "chips", "licenças" ou "ICCID", são sinônimos
"""
    
    try:
        with st.spinner("🤖 Analisando dados..."):
            resposta = llm.invoke(prompt)
            return resposta.content
    except Exception as e:
        return f"❌ Erro ao processar: {str(e)}"

# ==================== EXPORT ====================

def gerar_excel_completo(dados):
    """Gera arquivo Excel com múltiplas abas"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Aba 1: Resumo Executivo
        resumo = pd.DataFrame([dados['metricas']]).T
        resumo.columns = ['Valor']
        resumo.to_excel(writer, sheet_name='Resumo Executivo')
        
        # Aba 2: Distribuição Operadora
        dados['dist_operadora'].to_excel(writer, sheet_name='Operadoras', index=False)
        
        # Aba 3: Status OP
        dados['dist_status_op'].to_excel(writer, sheet_name='Status OP', index=False)
        
        # Aba 4: Conexões
        dados['dist_conexao'].to_excel(writer, sheet_name='Conexões', index=False)
        
        # Aba 5: Vencimentos
        dados['vencimentos_mes'].to_excel(writer, sheet_name='Vencimentos', index=False)
        
        # Aba 6: Matriz Vencimentos
        dados['matriz_vencimentos'].to_excel(writer, sheet_name='Matriz Vencimentos', index=False)
        
        # Aba 7: Chips Críticos
        dados['chips_criticos'][['ICCID', 'PROJETO', 'OPERADORA', 'DATA DE VENCIMENTO']].to_excel(
            writer, sheet_name='Chips Críticos', index=False
        )
        
        # Aba 8: Chips Válidos Suspensos
        dados['chips_validos_suspensos'][['ICCID', 'PROJETO', 'OPERADORA', 'STATUS NA OP.']].to_excel(
            writer, sheet_name='Válidos Suspensos', index=False
        )
    
    output.seek(0)
    return output

# ==================== INTERFACE PRINCIPAL ====================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📱 Dashboard Gerencial de Licenças</h1>
        <p>Base Mobile | Controle Inteligente de Chips e Licenças Móveis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Upload e Filtros
    with st.sidebar:
        st.markdown("### 📂 Upload de Dados")
        uploaded_file = st.file_uploader(
            "Envie o arquivo Excel",
            type=['xlsx', 'xls'],
            help="Arquivo com as colunas: PROJETO, ICCID, OPERADORA, etc."
        )
        
        if uploaded_file is not None:
            # Carregar dados
            if 'df_original' not in st.session_state or st.session_state.get('file_hash') != hashlib.md5(uploaded_file.getvalue()).hexdigest():
                with st.spinner("📊 Carregando dados..."):
                    df = carregar_dados_otimizado(uploaded_file)
                    if df is not None:
                        st.session_state.df_original = df
                        st.session_state.file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
                        st.success(f"✅ {len(df):,} registros carregados!")
            
            df = st.session_state.get('df_original')
            
            if df is not None:
                st.markdown("---")
                st.markdown("### 🎯 Filtros")
                
                # Inicializar filtros
                if 'filtros_ativos' not in st.session_state:
                    st.session_state.filtros_ativos = {}
                
                # Filtro de Projeto
                projetos_disponiveis = sorted(df['PROJETO'].unique())
                projetos_selecionados = st.multiselect(
                    "Projetos",
                    options=projetos_disponiveis,
                    default=None,
                    help="Selecione um ou mais projetos"
                )
                st.session_state.filtros_ativos['projetos'] = projetos_selecionados
                
                # Filtro de Operadora
                operadoras_disponiveis = sorted(df['OPERADORA'].unique())
                operadoras_selecionadas = st.multiselect(
                    "Operadoras",
                    options=operadoras_disponiveis,
                    default=None
                )
                st.session_state.filtros_ativos['operadoras'] = operadoras_selecionadas
                
                # Filtro de Status OP
                status_op_disponiveis = sorted(df['STATUS NA OP.'].unique())
                status_op_selecionados = st.multiselect(
                    "Status na Operadora",
                    options=status_op_disponiveis,
                    default=None
                )
                st.session_state.filtros_ativos['status_op'] = status_op_selecionados
                
                # Filtro de Status Licença
                status_lic_selecionados = st.multiselect(
                    "Status da Licença",
                    options=['Válido', 'Expirado'],
                    default=None
                )
                st.session_state.filtros_ativos['status_licenca'] = status_lic_selecionados
                
                st.markdown("---")
                st.markdown("### 📅 Período de Vencimento")
                
                col1, col2 = st.columns(2)
                with col1:
                    data_inicio = st.date_input("De", value=None, help="Data inicial")
                    if data_inicio:
                        st.session_state.filtros_ativos['data_venc_inicio'] = pd.Timestamp(data_inicio)
                    else:
                        st.session_state.filtros_ativos['data_venc_inicio'] = None
                
                with col2:
                    data_fim = st.date_input("Até", value=None, help="Data final")
                    if data_fim:
                        st.session_state.filtros_ativos['data_venc_fim'] = pd.Timestamp(data_fim)
                    else:
                        st.session_state.filtros_ativos['data_venc_fim'] = None
                
                # Botão limpar filtros
                if st.button("🔄 Limpar Filtros", use_container_width=True):
                    st.session_state.filtros_ativos = {}
                    st.rerun()
                
                st.markdown("---")
                st.markdown("### ℹ️ Sobre")
                st.caption("Dashboard desenvolvido para gestão inteligente de chips e licenças móveis da Base Mobile.")
                st.caption("Versão 3.0 Enterprise")
    
    # Conteúdo Principal
    if 'df_original' in st.session_state:
        df = st.session_state.df_original
        
        # Agregar dados com filtros
        df_hash = st.session_state.get('file_hash', '')
        filtros_hash = hashlib.md5(str(st.session_state.get('filtros_ativos', {})).encode()).hexdigest()
        
        with st.spinner("📊 Processando dados..."):
            dados = agregar_dados_otimizado(df_hash, filtros_hash, versao=3)
        
        if dados is None:
            st.error("❌ Erro ao processar dados")
            return
        
        # Tabs principais
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💬 Assistente IA", "📥 Exportar"])
        
        with tab1:
            # KPIs Principais
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            metricas = dados['metricas']
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total de Licenças</div>
                    <div class="metric-value">{metricas['total_licencas']:,}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Licenças Válidas</div>
                    <div class="metric-value">{metricas['licencas_validas']:,}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Licenças Expiradas</div>
                    <div class="metric-value">{metricas['licencas_expiradas']:,}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Nunca Conectou</div>
                    <div class="metric-value">{metricas['nunca_conectou']:,}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Ativos na OP</div>
                    <div class="metric-value">{metricas['chips_ativos_op']:,}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col6:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Suspensos na OP</div>
                    <div class="metric-value">{metricas['chips_suspensos_op']:,}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráficos Linha 1
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                fig_op = criar_grafico_operadora(dados)
                st.plotly_chart(fig_op, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                fig_conexao = criar_grafico_conexoes(dados)
                st.plotly_chart(fig_conexao, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Gráficos Linha 2
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                fig_status_op = criar_grafico_status_op(dados)
                st.plotly_chart(fig_status_op, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="plot-container">', unsafe_allow_html=True)
                fig_venc = criar_grafico_vencimentos(dados)
                st.plotly_chart(fig_venc, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Gráficos Linha 3
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            fig_heatmap = criar_heatmap_vencimentos(dados)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Gráfico Sankey
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            fig_sankey = criar_grafico_sankey(dados)
            st.plotly_chart(fig_sankey, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Alertas
            st.markdown("### ⚠️ Alertas Críticos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.warning(f"""
                **🔴 Chips Válidos que Nunca Conectaram**  
                {len(dados['chips_criticos']):,} chips com licença válida mas sem nenhuma conexão registrada.
                """)
            
            with col2:
                st.warning(f"""
                **🟡 Chips Válidos mas Suspensos na Operadora**  
                {len(dados['chips_validos_suspensos']):,} chips com licença válida mas suspensos pela operadora.
                """)
        
        with tab2:
            st.markdown("### 💬 Assistente Inteligente")
            st.caption("Faça perguntas sobre os dados ou use as análises pré-configuradas")
            
            # Análises Rápidas
            st.markdown("#### 🚀 Análises Rápidas")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Relatório do Diretor", use_container_width=True):
                    pergunta = """
                    Gere um relatório executivo completo perpassando por cada projeto, mostrando em formato de tabela:
                    - Total de chips/linhas
                    - Operadora principal
                    - Quantidade de chips que conectaram
                    - Status de conexão (distribuição por tempo)
                    - Próximos vencimentos (próximos 3 meses)
                    
                    Ordene por quantidade de chips (decrescente) e destaque insights importantes.
                    """
                    resposta = processar_pergunta_ia(pergunta, dados)
                    st.markdown('<div class="chat-message">', unsafe_allow_html=True)
                    st.markdown(resposta)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                if st.button("🔌 Análise de Conexões", use_container_width=True):
                    pergunta = """
                    Analise detalhadamente a situação das conexões dos chips:
                    - Quantos nunca conectaram (por projeto e operadora)
                    - Chips sem conexão há mais de 90 dias (crítico)
                    - Taxa de conectividade por operadora
                    - Identifique projetos com maior problema de conexão
                    """
                    resposta = processar_pergunta_ia(pergunta, dados)
                    st.markdown('<div class="chat-message">', unsafe_allow_html=True)
                    st.markdown(resposta)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                if st.button("⚠️ Chips Críticos", use_container_width=True):
                    pergunta = """
                    Identifique chips em situação crítica:
                    1. Válidos mas nunca conectaram
                    2. Válidos mas suspensos na operadora
                    3. Próximos a vencer (30 dias) sem conexão recente
                    
                    Apresente em tabela com projeto, operadora e quantidade.
                    """
                    resposta = processar_pergunta_ia(pergunta, dados)
                    st.markdown('<div class="chat-message">', unsafe_allow_html=True)
                    st.markdown(resposta)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Chat livre
            st.markdown("#### 💭 Pergunte Qualquer Coisa")
            
            pergunta_usuario = st.text_area(
                "Digite sua pergunta",
                placeholder="Ex: Quantas linhas da Bahia vão vencer em fevereiro?",
                height=100
            )
            
            if st.button("🤖 Analisar", type="primary"):
                if pergunta_usuario.strip():
                    resposta = processar_pergunta_ia(pergunta_usuario, dados)
                    st.markdown('<div class="chat-message">', unsafe_allow_html=True)
                    st.markdown(resposta)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Digite uma pergunta primeiro")
        
        with tab3:
            st.markdown("### 📥 Exportar Análises")
            st.caption("Baixe relatórios completos em Excel com múltiplas abas")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("📊 Gerar Relatório Completo", use_container_width=True, type="primary"):
                    with st.spinner("📝 Gerando arquivo Excel..."):
                        excel_file = gerar_excel_completo(dados)
                        
                        st.download_button(
                            label="⬇️ Baixar Relatório Excel",
                            data=excel_file,
                            file_name=f"base_mobile_relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        
                        st.success("✅ Relatório gerado com sucesso!")
                
                st.markdown("---")
                
                st.info("""
                **📋 O relatório inclui:**
                - Resumo Executivo
                - Distribuição por Operadora
                - Status nas Operadoras
                - Análise de Conexões
                - Vencimentos Mensais
                - Matriz de Vencimentos (Projeto x Mês)
                - Chips Críticos (válidos + nunca conectaram)
                - Chips Válidos Suspensos
                """)
    
    else:
        # Mensagem inicial
        st.info("👈 Faça upload do arquivo Excel na barra lateral para começar")
        
        st.markdown("""
        ### 📋 Estrutura Esperada do Arquivo
        
        O arquivo Excel deve conter as seguintes colunas:
        
        | Coluna | Descrição | Exemplo |
        |--------|-----------|---------|
        | **PROJETO** | Nome do projeto/cliente | Governo do estado da Bahia |
        | **ICCID** | Código do chip | 8955053176000247... |
        | **ICCID ANTIGO** | Código do chip substituído | 8955053284002347... |
        | **OPERADORA** | Nome da operadora | CLARO |
        | **DATA DE ENTREGA** | Data de entrega | 23/08/2023 |
        | **DATA DE ATIVAÇÃO** | Data de ativação | 23/11/2024 |
        | **DATA DE VENCIMENTO** | Data de vencimento | 23/11/2025 |
        | **ÚLTIMA CONEXÃO** | Data da última conexão | 18/04/2025 |
        | **STATUS NA OP.** | Status na operadora | ATIVO |
        
        ### ✨ Funcionalidades
        
        - 📊 **Dashboard Interativo** com gráficos dinâmicos
        - 🎯 **Filtros Avançados** por projeto, operadora, status e período
        - 💬 **Assistente IA** para análises personalizadas
        - 📥 **Export Excel** com múltiplas abas
        - ⚡ **Performance Otimizada** para 450k+ registros
        - 🔄 **Atualização em Tempo Real** com filtros dinâmicos
        """)

if __name__ == "__main__":
    main()
