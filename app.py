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
    
    /* Cards */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #4CAF50;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2E7D32;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #666;
        text-transform: uppercase;
    }
    
    /* Gráficos */
    .plot-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
</style>
""", unsafe_allow_html=True)

# ==================== CARREGAMENTO DE DADOS ====================

@st.cache_data(ttl=7200, show_spinner=False)
def carregar_planilha_otimizado(versao=3):
    """Carrega planilha Excel da pasta local - VERSÃO 3.0"""
    try:
        arquivo = "MAPEAMENTO DE CHIPS.xlsx"
        
        # Colunas necessárias
        colunas_usar = [
            'PROJETO', 'ICCID', 'ICCID ANTIGO', 'OPERADORA',
            'DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO',
            'ÚLTIMA CONEXÃO', 'STATUS NA OP.'
        ]
        
        # Parse de datas
        colunas_data = ['DATA DE ENTREGA', 'DATA DE ATIVAÇÃO', 'DATA DE VENCIMENTO', 'ÚLTIMA CONEXÃO']
        
        df = pd.read_excel(
            arquivo,
            usecols=colunas_usar,
            parse_dates=colunas_data,
            engine='openpyxl'
        )
        
        # Normalizar colunas
        df.columns = df.columns.str.strip().str.upper()
        
        # Normalizar OPERADORA (uppercase + primeira palavra)
        if 'OPERADORA' in df.columns:
            df['OPERADORA'] = df['OPERADORA'].astype(str).str.upper().str.split().str[0]
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
        
        # Calcular CATEGORIA DE CONEXÃO
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
        st.error(f"❌ Erro ao carregar planilha: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

@st.cache_data(ttl=7200, show_spinner=False)
def agregar_dados_graficos(df_hash, filtros_hash, versao=3):
    """Agrega dados com filtros - VERSÃO 3.0"""
    df = st.session_state.get('df_completo')
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
    
    # Métricas
    total = len(df_filtrado)
    validas = len(df_filtrado[df_filtrado['STATUS_LICENCA'] == 'Válido'])
    expiradas = len(df_filtrado[df_filtrado['STATUS_LICENCA'] == 'Expirado'])
    nunca_conectou = len(df_filtrado[df_filtrado['CATEGORIA_CONEXAO'] == 'Nunca Conectou'])
    ativos_op = len(df_filtrado[df_filtrado['STATUS NA OP.'] == 'Ativo'])
    suspensos_op = len(df_filtrado[df_filtrado['STATUS NA OP.'] == 'Suspenso'])
    
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
    
    # Ordem correta
    ordem_conexao = ['Nunca Conectou', 'Mais de 180 dias', '91-180 dias', '61-90 dias', '31-60 dias', '0-30 dias']
    dist_conexao['CATEGORIA'] = pd.Categorical(dist_conexao['CATEGORIA'], categories=ordem_conexao, ordered=True)
    dist_conexao = dist_conexao.sort_values('CATEGORIA')
    
    # Vencimentos por mês
    df_temp = df_filtrado[df_filtrado['DATA DE VENCIMENTO'].notna()].copy()
    df_temp['MES_VENCIMENTO'] = df_temp['DATA DE VENCIMENTO'].dt.to_period('M').astype(str)
    vencimentos_mes = df_temp.groupby('MES_VENCIMENTO', as_index=False).size()
    vencimentos_mes.columns = ['MES', 'QUANTIDADE']
    vencimentos_mes = vencimentos_mes.sort_values('MES')
    
    # Matriz Vencimentos (Projeto x Mês)
    matriz_venc = df_temp.groupby(['PROJETO', 'MES_VENCIMENTO'], as_index=False).size()
    matriz_venc.columns = ['PROJETO', 'MES', 'QUANTIDADE']
    
    # Chips Críticos
    chips_criticos = len(df_filtrado[
        (df_filtrado['STATUS_LICENCA'] == 'Válido') & 
        (df_filtrado['CATEGORIA_CONEXAO'] == 'Nunca Conectou')
    ])
    
    chips_validos_suspensos = len(df_filtrado[
        (df_filtrado['STATUS_LICENCA'] == 'Válido') & 
        (df_filtrado['STATUS NA OP.'] == 'Suspenso')
    ])
    
    return {
        'df_filtrado': df_filtrado,
        'total': total,
        'validas': validas,
        'expiradas': expiradas,
        'nunca_conectou': nunca_conectou,
        'ativos_op': ativos_op,
        'suspensos_op': suspensos_op,
        'chips_criticos': chips_criticos,
        'chips_validos_suspensos': chips_validos_suspensos,
        'dist_operadora': dist_operadora,
        'dist_status_op': dist_status_op,
        'dist_conexao': dist_conexao,
        'vencimentos_mes': vencimentos_mes,
        'matriz_venc': matriz_venc
    }

# ==================== GRÁFICOS ====================

def criar_grafico_operadora(dados):
    """Gráfico Pizza - Distribuição por Operadora"""
    df = dados['dist_operadora']
    
    cores_ops = {
        'VIVO': '#660099',
        'CLARO': '#FF0000',
        'TIM': '#0033A0',
        'ALGAR': '#00A859',
        'OI': '#FFD700'
    }
    cores = [cores_ops.get(op, '#999999') for op in df['OPERADORA']]
    
    fig = go.Figure(data=[go.Pie(
        labels=df['OPERADORA'],
        values=df['QUANTIDADE'],
        hole=0.4,
        marker=dict(colors=cores),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>%{value:,.0f} licenças<br>%{percent}<extra></extra>'
    )])
    
    fig.add_annotation(
        text=f'<b>{df["QUANTIDADE"].sum():,.0f}</b><br>Total',
        x=0.5, y=0.5,
        font=dict(size=18, color='#2E7D32'),
        showarrow=False
    )
    
    fig.update_layout(
        title='Distribuição por Operadora',
        height=400,
        margin=dict(t=60, b=20, l=20, r=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_grafico_status_op(dados):
    """Gráfico Barras - Status nas Operadoras"""
    df = dados['dist_status_op'].sort_values('QUANTIDADE', ascending=True)
    
    cores = {
        'Ativo': '#4CAF50',
        'Bloqueado': '#8BC34A',
        'Suspenso': '#CDDC39',
        'Cancelado': '#AED581'
    }
    cores_list = [cores.get(s, '#999') for s in df['STATUS']]
    
    fig = go.Figure(data=[go.Bar(
        y=df['STATUS'],
        x=df['QUANTIDADE'],
        orientation='h',
        marker=dict(color=cores_list),
        text=[f"{q:,.0f} ({p:.1f}%)" for q, p in zip(df['QUANTIDADE'], df['PERCENTUAL'])],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} licenças<extra></extra>'
    )])
    
    fig.update_layout(
        title='Status das Licenças nas Operadoras',
        xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        height=350,
        margin=dict(t=60, b=40, l=150, r=80),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_grafico_conexoes(dados):
    """Gráfico Rosca - Análise de Conexões"""
    df = dados['dist_conexao']
    
    cores = {
        'Nunca Conectou': '#D32F2F',
        'Mais de 180 dias': '#F57C00',
        '91-180 dias': '#FBC02D',
        '61-90 dias': '#AFB42B',
        '31-60 dias': '#7CB342',
        '0-30 dias': '#388E3C'
    }
    cores_list = [cores.get(c, '#999') for c in df['CATEGORIA']]
    
    fig = go.Figure(data=[go.Pie(
        labels=df['CATEGORIA'],
        values=df['QUANTIDADE'],
        hole=0.5,
        marker=dict(colors=cores_list),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>%{value:,.0f} chips<extra></extra>'
    )])
    
    total = df['QUANTIDADE'].sum()
    com_conexao = df[df['CATEGORIA'] != 'Nunca Conectou']['QUANTIDADE'].sum()
    perc = (com_conexao / total * 100) if total > 0 else 0
    
    fig.add_annotation(
        text=f'<b>{com_conexao:,.0f}</b><br>{perc:.1f}%<br>conectaram',
        x=0.5, y=0.5,
        font=dict(size=16, color='#2E7D32'),
        showarrow=False
    )
    
    fig.update_layout(
        title='Análise de Conexões',
        height=450,
        margin=dict(t=60, b=20, l=20, r=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_grafico_vencimentos(dados):
    """Gráfico Área - Vencimentos Mensais"""
    df = dados['vencimentos_mes'].head(12)
    
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
        hovertemplate='<b>%{x}</b><br>%{y:,.0f} vencimentos<extra></extra>'
    ))
    
    fig.update_layout(
        title='Vencimentos (Próximos 12 Meses)',
        xaxis=dict(title='Mês', tickangle=-45),
        yaxis=dict(title='Quantidade', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        height=400,
        margin=dict(t=60, b=80, l=60, r=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def criar_heatmap_vencimentos(dados):
    """Heatmap - Matriz Projeto x Mês"""
    df = dados['matriz_venc']
    
    pivot = df.pivot_table(
        index='PROJETO',
        columns='MES',
        values='QUANTIDADE',
        fill_value=0
    ).iloc[:, :12]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Greens',
        text=pivot.values,
        texttemplate='%{text}',
        hovertemplate='<b>%{y}</b><br>%{x}: %{z} vencimentos<extra></extra>'
    ))
    
    fig.update_layout(
        title='Matriz de Vencimentos (Projeto x Mês)',
        xaxis=dict(tickangle=-45),
        height=max(400, len(pivot) * 25),
        margin=dict(t=60, b=80, l=200, r=60),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# ==================== ASSISTENTE IA ====================

@st.cache_resource(show_spinner=False)
def init_llm():
    """LLM Groq"""
    try:
        if "GROQ_API_KEY" not in st.secrets:
            return None
        
        llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0,
            groq_api_key=st.secrets["GROQ_API_KEY"],
            max_tokens=600
        )
        return llm
    except Exception as e:
        st.error(f"❌ Erro Groq: {str(e)}")
        return None

def gerar_contexto_ia(dados):
    """Contexto para IA"""
    df = dados['df_filtrado']
    
    resumo_proj = df.groupby('PROJETO').agg({
        'ICCID': 'count',
        'OPERADORA': lambda x: x.mode()[0] if len(x) > 0 else 'N/A',
    }).reset_index()
    resumo_proj.columns = ['Projeto', 'Total_Linhas', 'Op_Principal']
    
    ctx = f"""
# BASE MOBILE - CONTEXTO

## GLOSSÁRIO
- PROJETO = Estado/Cliente (ex: "Governo da Bahia" = projeto Bahia)
- ICCID = LINHA = LICENÇA = CHIP (sinônimos)
- STATUS LICENÇA: Válido (vencimento futuro) ou Expirado (passou)
- STATUS NA OP: Ativo/Suspenso/Bloqueado (independente da licença)
- ÚLTIMA CONEXÃO: Quando o chip conectou pela última vez

## MÉTRICAS
Total: {dados['total']:,} | Válidas: {dados['validas']:,} | Expiradas: {dados['expiradas']:,}
Nunca Conectou: {dados['nunca_conectou']:,} | Ativos OP: {dados['ativos_op']:,} | Suspensos OP: {dados['suspensos_op']:,}

## OPERADORAS
{dados['dist_operadora'].to_string(index=False)}

## PROJETOS (TOP 10)
{resumo_proj.head(10).to_string(index=False)}

## CONEXÕES
{dados['dist_conexao'].to_string(index=False)}

## VENCIMENTOS
{dados['vencimentos_mes'].head(6).to_string(index=False)}

RESPONDA EM FORMATO EXECUTIVO COM TABELAS MARKDOWN.
"""
    return ctx

def processar_ia(pergunta, dados):
    """Processa pergunta"""
    llm = init_llm()
    if not llm:
        return "❌ IA indisponível"
    
    ctx = gerar_contexto_ia(dados)
    prompt = f"{ctx}\n\nPERGUNTA: {pergunta}\n\nRESPONDA:"
    
    try:
        resp = llm.invoke(prompt)
        return resp.content
    except Exception as e:
        return f"❌ Erro: {str(e)}"

# ==================== INTERFACE ====================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📱 Dashboard Gerencial de Licenças</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner("📊 Carregando planilha..."):
        df = carregar_planilha_otimizado(versao=3)
    
    if df is None:
        st.error("❌ Erro ao carregar dados")
        return
    
    st.session_state.df_completo = df
    df_hash = hashlib.md5(str(len(df)).encode()).hexdigest()
    
    # Sidebar - Filtros
    with st.sidebar:
        st.markdown("### 🎯 Filtros")
        
        if 'filtros_ativos' not in st.session_state:
            st.session_state.filtros_ativos = {}
        
        # Filtros
        projetos = st.multiselect("Projetos", sorted(df['PROJETO'].unique()), default=None)
        st.session_state.filtros_ativos['projetos'] = projetos
        
        operadoras = st.multiselect("Operadoras", sorted(df['OPERADORA'].unique()), default=None)
        st.session_state.filtros_ativos['operadoras'] = operadoras
        
        status_op = st.multiselect("Status na OP", sorted(df['STATUS NA OP.'].unique()), default=None)
        st.session_state.filtros_ativos['status_op'] = status_op
        
        status_lic = st.multiselect("Status Licença", ['Válido', 'Expirado'], default=None)
        st.session_state.filtros_ativos['status_licenca'] = status_lic
        
        if st.button("🔄 Limpar", use_container_width=True):
            st.session_state.filtros_ativos = {}
            st.rerun()
    
    # Agregar dados
    filtros_hash = hashlib.md5(str(st.session_state.filtros_ativos).encode()).hexdigest()
    dados = agregar_dados_graficos(df_hash, filtros_hash, versao=3)
    
    if dados is None:
        st.error("❌ Erro ao processar")
        return
    
    # Tabs
    tab1, tab2 = st.tabs(["📊 Dashboard", "💬 Assistente IA"])
    
    with tab1:
        # KPIs
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Total</div><div class="metric-value">{dados["total"]:,}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Válidas</div><div class="metric-value">{dados["validas"]:,}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Expiradas</div><div class="metric-value">{dados["expiradas"]:,}</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Nunca Conectou</div><div class="metric-value">{dados["nunca_conectou"]:,}</div></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Ativos OP</div><div class="metric-value">{dados["ativos_op"]:,}</div></div>', unsafe_allow_html=True)
        with col6:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Suspensos OP</div><div class="metric-value">{dados["suspensos_op"]:,}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(criar_grafico_operadora(dados), use_container_width=True)
        with col2:
            st.plotly_chart(criar_grafico_conexoes(dados), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(criar_grafico_status_op(dados), use_container_width=True)
        with col2:
            st.plotly_chart(criar_grafico_vencimentos(dados), use_container_width=True)
        
        st.plotly_chart(criar_heatmap_vencimentos(dados), use_container_width=True)
        
        # Alertas
        st.markdown("### ⚠️ Alertas")
        col1, col2 = st.columns(2)
        with col1:
            st.warning(f"🔴 **Chips Válidos Nunca Conectaram:** {dados['chips_criticos']:,}")
        with col2:
            st.warning(f"🟡 **Chips Válidos Suspensos:** {dados['chips_validos_suspensos']:,}")
    
    with tab2:
        st.markdown("### 💬 Assistente")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Relatório Diretor", use_container_width=True):
                pergunta = "Gere relatório executivo por projeto mostrando: total chips, operadora principal, conexões e próximos vencimentos em tabela"
                resp = processar_ia(pergunta, dados)
                st.markdown(f'<div class="chat-message">{resp}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("🔌 Análise Conexões", use_container_width=True):
                pergunta = "Analise chips que nunca conectaram por projeto e operadora, identifique críticos"
                resp = processar_ia(pergunta, dados)
                st.markdown(f'<div class="chat-message">{resp}</div>', unsafe_allow_html=True)
        
        with col3:
            if st.button("⚠️ Chips Críticos", use_container_width=True):
                pergunta = "Liste chips válidos mas suspensos OU nunca conectaram, agrupe por projeto"
                resp = processar_ia(pergunta, dados)
                st.markdown(f'<div class="chat-message">{resp}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        pergunta_livre = st.text_area("Sua pergunta:", height=100)
        if st.button("🤖 Perguntar", type="primary"):
            if pergunta_livre.strip():
                resp = processar_ia(pergunta_livre, dados)
                st.markdown(f'<div class="chat-message">{resp}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

