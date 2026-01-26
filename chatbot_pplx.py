import streamlit as st
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = "sonar-pro"


def inicializar_chatbot():
    """Inicializa o estado do chatbot"""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_client" not in st.session_state:
        if not PERPLEXITY_API_KEY:
            st.error("⚠️ API Key da Perplexity não encontrada! Configure o arquivo .env")
            st.stop()
        st.session_state.chat_client = OpenAI(
            api_key=PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )


def formatar_numero(num):
    """Formata número com separador de milhar"""
    try:
        if pd.isna(num):
            return "0"
        return f"{int(num):,}".replace(",", ".")
    except:
        return str(num)


def buscar_coluna(df, variacoes):
    """Helper para buscar coluna com múltiplas variações"""
    for variacao in variacoes:
        if variacao in df.columns:
            return variacao
    return None


def detectar_projeto_mencionado(pergunta, df):
    """Detecta projeto mencionado - VERSÃO CORRIGIDA"""
    if 'PROJETO' not in df.columns:
        return None
    
    projetos_disponiveis = df['PROJETO'].unique()
    pergunta_clean = pergunta.strip()
    pergunta_upper = pergunta_clean.upper()
    
    stopwords = ['RESUMO', 'DO', 'DA', 'DE', 'DOS', 'DAS', 'PROJETO', 'COMPLETO', 
                 'FAÇA', 'FACA', 'UM', 'UMA', 'O', 'A', 'ME', 'DÊ', 'DE', 'SOBRE',
                 'PARA', 'NO', 'NA', 'EM', 'COM', 'POR', 'SEM', 'ATE', 'ATÉ', 
                 'VENCEM', 'VENCIMENTO', 'QUAIS', 'QUANTOS', 'DIAS']
    
    palavras = pergunta_upper.split()
    palavras_filtradas = [p for p in palavras if p not in stopwords and len(p) > 1]
    texto_limpo = ' '.join(palavras_filtradas)
    
    # 1. MATCH EXATO
    for projeto in projetos_disponiveis:
        if projeto.upper() == texto_limpo or projeto.upper() == pergunta_upper:
            return projeto
    
    # 2. MATCH COMPLETO
    for projeto in projetos_disponiveis:
        projeto_upper = projeto.upper()
        
        if projeto_upper in pergunta_upper:
            if len(projeto) <= 2:
                pattern = r'\b' + re.escape(projeto_upper) + r'\b'
                if re.search(pattern, pergunta_upper):
                    return projeto
            else:
                return projeto
    
    # 3. MATCH POR PALAVRA-CHAVE
    palavras_significativas = [p for p in palavras_filtradas if len(p) >= 3]
    
    for palavra in palavras_significativas:
        for projeto in projetos_disponiveis:
            if palavra in projeto.upper():
                return projeto
    
    # 4. MATCH REVERSO
    for projeto in projetos_disponiveis:
        palavras_projeto = [p for p in projeto.upper().split() 
                           if p not in stopwords and len(p) >= 3]
        
        for palavra_proj in palavras_projeto:
            if palavra_proj in palavras_significativas:
                return projeto
    
    return None


def listar_projetos_disponiveis(df):
    """Lista todos os projetos disponíveis"""
    if 'PROJETO' not in df.columns:
        return "❌ Coluna PROJETO não encontrada."
    
    projetos = sorted(df['PROJETO'].unique())
    
    resposta = "## 📁 Projetos Disponíveis na Base\n\n"
    resposta += f"**Total:** {len(projetos)} projetos\n\n"
    
    for i, projeto in enumerate(projetos, 1):
        qtd = len(df[df['PROJETO'] == projeto])
        resposta += f"{i}. **{projeto}** ({formatar_numero(qtd)} chips)\n"
    
    resposta += "\n💡 *Para relatório completo, digite:* **Resumo do projeto [NOME]**"
    
    return resposta


def gerar_relatorio_completo_projeto(df, projeto):
    """Gera relatório executivo COMPLETO com TODAS as seções"""
    hoje = pd.Timestamp.now().normalize()
    limite_30d = hoje + pd.Timedelta(days=30)
    limite_90d = hoje + pd.Timedelta(days=90)
    
    df_proj = df[df['PROJETO'] == projeto].copy()
    
    if len(df_proj) == 0:
        return f"❌ Projeto **{projeto}** não encontrado.\n\n{listar_projetos_disponiveis(df)}"
    
    total_chips = len(df_proj)
    
    resposta = f"## 📊 Relatório Executivo - {projeto}\n\n"
    resposta += f"**Total de Chips:** {formatar_numero(total_chips)}\n\n"
    
    # Variáveis para insights
    venc_30d = 0
    ativados = 0
    inativos_180_count = 0
    top_operadora = None
    pct_top_operadora = 0
    
    # ===== SEÇÃO 1: DISTRIBUIÇÃO POR OPERADORA =====
    if 'OPERADORA' in df_proj.columns:
        por_operadora = df_proj['OPERADORA'].value_counts()
        
        resposta += "### 📶 Distribuição por Operadora\n\n"
        resposta += "| Operadora | Chips | % |\n"
        resposta += "|-----------|-------|---------|\n"
        
        emojis = {"CLARO": "🔴", "VIVO": "🟣", "TIM": "🔵", "OI": "🟡", "ALGAR": "🟢"}
        
        for operadora, qtd in por_operadora.items():
            pct = (qtd / total_chips) * 100
            emoji = emojis.get(operadora, "📡")
            resposta += f"| {emoji} {operadora} | {formatar_numero(qtd)} | {pct:.1f}% |\n"
        
        if len(por_operadora) > 0:
            top_operadora = por_operadora.index[0]
            pct_top_operadora = (por_operadora.iloc[0] / total_chips) * 100
        
        resposta += "\n"
    
    # ===== SEÇÃO 2: VENCIMENTOS + PRÓXIMOS VENCIMENTOS =====
    col_venc = buscar_coluna(df_proj, ['DATA DE VENCIMENTO', 'DATA_VENCIMENTO', 'VENCIMENTO'])
    
    if col_venc:
        try:
            if df_proj[col_venc].dtype == 'object':
                df_proj[col_venc] = pd.to_datetime(df_proj[col_venc], errors='coerce')
            
            df_venc = df_proj[df_proj[col_venc].notna()]
            
            validas = len(df_venc[df_venc[col_venc] >= hoje])
            expiradas = len(df_venc[df_venc[col_venc] < hoje])
            venc_30d = len(df_venc[(df_venc[col_venc] >= hoje) & 
                                    (df_venc[col_venc] <= limite_30d)])
            venc_90d = len(df_venc[(df_venc[col_venc] >= hoje) & 
                                    (df_venc[col_venc] <= limite_90d)])
            
            resposta += "### 📅 Status de Vencimentos\n\n"
            resposta += "| Status | Quantidade | % |\n"
            resposta += "|--------|------------|---|\n"
            resposta += f"| ✅ Válidas | {formatar_numero(validas)} | {(validas/total_chips*100):.1f}% |\n"
            resposta += f"| ❌ Expiradas | {formatar_numero(expiradas)} | {(expiradas/total_chips*100):.1f}% |\n"
            resposta += f"| ⚠️ Vencem em 30d | {formatar_numero(venc_30d)} | {(venc_30d/total_chips*100):.1f}% |\n"
            resposta += f"| 🟡 Vencem em 90d | {formatar_numero(venc_90d)} | {(venc_90d/total_chips*100):.1f}% |\n"
            
            # PRÓXIMOS VENCIMENTOS (top 5 datas)
            if venc_30d > 0:
                df_prox_venc = df_venc[(df_venc[col_venc] >= hoje) & 
                                       (df_venc[col_venc] <= limite_30d)].copy()
                
                top_datas = df_prox_venc[col_venc].value_counts().head(5).sort_index()
                
                resposta += "\n**📆 Próximos Vencimentos (Top 5 Datas):**\n\n"
                resposta += "| Data | Quantidade |\n"
                resposta += "|------|------------|\n"
                
                for data, qtd in top_datas.items():
                    resposta += f"| {data.strftime('%d/%m/%Y')} | {formatar_numero(qtd)} chips |\n"
            
            resposta += "\n"
        except Exception as e:
            resposta += f"### 📅 Vencimentos\n\n⚠️ Erro: {str(e)}\n\n"
    
    # ===== SEÇÃO 3: ATIVAÇÕES =====
    col_ativ = buscar_coluna(df_proj, ['DATA DE ATIVAÇÃO', 'DATA_ATIVACAO', 'ATIVACAO'])
    
    if col_ativ:
        ativados = len(df_proj[df_proj[col_ativ].notna()])
        pendentes = total_chips - ativados
        
        resposta += "### 📡 Status de Ativações\n\n"
        resposta += "| Status | Quantidade | % |\n"
        resposta += "|--------|------------|---|\n"
        resposta += f"| ✅ Ativados | {formatar_numero(ativados)} | {(ativados/total_chips*100):.1f}% |\n"
        resposta += f"| ⏳ Pendentes | {formatar_numero(pendentes)} | {(pendentes/total_chips*100):.1f}% |\n"
        resposta += "\n"
    
    # ===== SEÇÃO 4: CONEXÕES DETALHADAS =====
    col_conexao = buscar_coluna(df_proj, ['CATEGORIACONEXAO', 'CATEGORIA_CONEXAO', 'CONEXAO'])
    
    if col_conexao:
        por_categoria = df_proj[col_conexao].value_counts()
        
        resposta += "### 🌐 Status de Conexões\n\n"
        resposta += "| Período | Chips | % |\n"
        resposta += "|---------|-------|---------|\n"
        
        # Ordem lógica
        ordem_categorias = ['0-30 dias', '31-90 dias', '91-180 dias', 'Mais de 180 dias', 'Nunca Conectou']
        
        for cat in ordem_categorias:
            if cat in por_categoria.index:
                qtd = por_categoria[cat]
                pct = (qtd / total_chips) * 100
                
                if '0-30' in cat:
                    emoji = "🟢"
                elif '31-90' in cat:
                    emoji = "🟡"
                elif '91-180' in cat:
                    emoji = "🟠"
                else:
                    emoji = "🔴"
                
                resposta += f"| {emoji} {cat} | {formatar_numero(qtd)} | {pct:.1f}% |\n"
                
                if cat == 'Mais de 180 dias':
                    inativos_180_count = qtd
        
        resposta += "\n"
    
    # ===== SEÇÃO 5: STATUS NA OPERADORA =====
    col_status = buscar_coluna(df_proj, ['STATUS NA OP.', 'STATUS_OP', 'STATUS'])
    
    if col_status:
        por_status = df_proj[col_status].value_counts().head(5)
        
        resposta += "### ⚙️ Status na Operadora (Top 5)\n\n"
        resposta += "| Status | Chips | % |\n"
        resposta += "|--------|-------|---|\n"
        
        for status, qtd in por_status.items():
            pct = (qtd / total_chips) * 100
            resposta += f"| {status} | {formatar_numero(qtd)} | {pct:.1f}% |\n"
        
        resposta += "\n"
    
    # ===== SEÇÃO 6: MINI TIMELINE =====
    if col_ativ and col_venc:
        resposta += "### 📈 Mini Timeline\n\n"
        
        try:
            # Ativações recentes (últimos 30 dias)
            if df_proj[col_ativ].dtype == 'object':
                df_proj[col_ativ] = pd.to_datetime(df_proj[col_ativ], errors='coerce')
            
            limite_ativ_30d = hoje - pd.Timedelta(days=30)
            ativ_recentes = len(df_proj[(df_proj[col_ativ].notna()) & 
                                        (df_proj[col_ativ] >= limite_ativ_30d)])
            
            resposta += "| Período | Evento | Quantidade |\n"
            resposta += "|---------|--------|------------|\n"
            resposta += f"| Últimos 30 dias | 🆕 Ativações recentes | {formatar_numero(ativ_recentes)} |\n"
            resposta += f"| Próximos 30 dias | ⚠️ Vencimentos | {formatar_numero(venc_30d)} |\n"
            resposta += f"| Próximos 90 dias | 🟡 Vencimentos | {formatar_numero(venc_90d)} |\n"
            resposta += "\n"
        except:
            pass
    
    # ===== INSIGHTS EXECUTIVOS =====
    resposta += "### 📌 Insights Executivos\n\n"
    
    insights = []
    
    if venc_30d > 0:
        pct_venc = (venc_30d / total_chips) * 100
        if pct_venc > 15:
            insights.append(f"🔴 **Crítico:** {formatar_numero(venc_30d)} licenças ({pct_venc:.1f}%) vencem em 30 dias - ação urgente")
        elif pct_venc > 5:
            insights.append(f"🟡 **Atenção:** {formatar_numero(venc_30d)} licenças vencem em 30 dias")
    
    if ativados > 0:
        taxa_ativ = (ativados / total_chips) * 100
        if taxa_ativ < 80:
            insights.append(f"🔴 **Ativação baixa:** {taxa_ativ:.1f}% dos chips ativados")
        elif taxa_ativ < 90:
            insights.append(f"🟡 **Ativação moderada:** {taxa_ativ:.1f}% dos chips ativados")
    
    if inativos_180_count > 0:
        pct_inativos = (inativos_180_count / total_chips) * 100
        if pct_inativos > 10:
            insights.append(f"🔴 **Alta inatividade:** {formatar_numero(inativos_180_count)} chips ({pct_inativos:.1f}%) sem conexão há 180+ dias")
    
    if top_operadora and pct_top_operadora > 60:
        insights.append(f"ℹ️ **Concentração:** {pct_top_operadora:.1f}% na operadora {top_operadora}")
    
    if insights:
        for insight in insights:
            resposta += f"- {insight}\n"
    else:
        resposta += "✅ Nenhum ponto crítico identificado - projeto em situação regular.\n"
    
    return resposta


def executar_consulta_sql(df, pergunta):
    """Executa consultas SQL - VERSÃO CORRIGIDA"""
    pergunta_lower = pergunta.lower()
    hoje = pd.Timestamp.now().normalize()
    limite_30d = hoje + pd.Timedelta(days=30)
    
    # ===== LISTAR PROJETOS =====
    if any(keyword in pergunta_lower for keyword in ['lista de projetos', 'projetos disponíveis', 'projetos disponiveis', 'liste os projetos']):
        return listar_projetos_disponiveis(df)
    
    # ===== VENCIMENTOS NOS PRÓXIMOS 30 DIAS - PRIORIDADE MÁXIMA =====
    if ("vencem" in pergunta_lower or "vencimento" in pergunta_lower or "vencendo" in pergunta_lower) and \
       ("30" in pergunta_lower or "próximos" in pergunta_lower or "proximos" in pergunta_lower) and \
       ("quais" in pergunta_lower or "projeto" in pergunta_lower):
        
        col_venc = buscar_coluna(df, ['DATA DE VENCIMENTO', 'DATA_VENCIMENTO', 'VENCIMENTO'])
        
        if not col_venc or 'PROJETO' not in df.columns:
            return "❌ Colunas necessárias não encontradas."
        
        try:
            if df[col_venc].dtype == 'object':
                df[col_venc] = pd.to_datetime(df[col_venc], errors='coerce')
            
            df_venc = df[(df[col_venc].notna()) & 
                         (df[col_venc] >= hoje) & 
                         (df[col_venc] <= limite_30d)].copy()
        except Exception as e:
            return f"❌ Erro ao processar vencimentos: {str(e)}"
        
        if len(df_venc) == 0:
            return f"## ✅ Vencimentos - Próximos 30 dias\n\n**Status:** Nenhuma licença vence."
        
        por_projeto = df_venc.groupby('PROJETO').size().sort_values(ascending=False)
        pct_total = (len(df_venc) / len(df)) * 100
        
        resposta = f"## 📅 Vencimentos - Próximos 30 dias\n\n"
        resposta += f"**Período:** {hoje.strftime('%d/%m/%Y')} → {limite_30d.strftime('%d/%m/%Y')}  \n"
        resposta += f"**Total:** {formatar_numero(len(df_venc))} licenças ({pct_total:.1f}%)\n\n"
        
        # Formato com próximas datas
        resposta += "### Por Projeto\n\n"
        resposta += "| Projeto | Licenças | % | Próximo Vencimento |\n"
        resposta += "|---------|----------|---|--------------------|\n"
        
        for projeto, qtd in por_projeto.items():
            pct = (qtd / len(df_venc)) * 100
            
            # Busca a próxima data de vencimento deste projeto
            df_proj_venc = df_venc[df_venc['PROJETO'] == projeto]
            prox_data = df_proj_venc[col_venc].min()
            
            resposta += f"| {projeto} | {formatar_numero(qtd)} | {pct:.1f}% | {prox_data.strftime('%d/%m/%Y')} |\n"
        
        top_projeto = por_projeto.index[0]
        resposta += f"\n**📌 Ação:** Priorizar renovações no **{top_projeto}**."
        
        return resposta
    
    # ===== DETECTA PROJETO MENCIONADO =====
    projeto_mencionado = detectar_projeto_mencionado(pergunta, df)
    
    if projeto_mencionado:
        if any(palavra in pergunta_lower for palavra in ['resumo', 'completo', 'relatório', 'relatorio', 'tudo', 'sobre', 'dados', 'informações', 'informacoes', 'status', 'situação', 'situacao']):
            return gerar_relatorio_completo_projeto(df, projeto_mencionado)
    
    # ===== CHIPS CANCELADOS =====
    if "cancelad" in pergunta_lower:
        col_status = buscar_coluna(df, ['STATUS NA OP.', 'STATUS', 'STATUS_OP'])
        
        if not col_status:
            return "❌ Coluna de STATUS não encontrada."
        
        df_cancelados = df[df[col_status].fillna('').astype(str).str.contains('Cancelad', case=False)]
        
        if len(df_cancelados) == 0:
            return "## ✅ Status de Cancelamentos\n\n**Total:** 0 chips cancelados."
        
        pct_total = (len(df_cancelados) / len(df)) * 100
        
        resposta = f"## ❌ Chips Cancelados\n\n"
        resposta += f"**Total:** {formatar_numero(len(df_cancelados))} chips ({pct_total:.1f}%)\n\n"
        
        if "operadora" in pergunta_lower and 'OPERADORA' in df.columns:
            por_operadora = df_cancelados.groupby('OPERADORA').size().sort_values(ascending=False)
            
            resposta += "| Operadora | Cancelados | % |\n"
            resposta += "|-----------|------------|---|\n"
            
            emojis = {"CLARO": "🔴", "VIVO": "🟣", "TIM": "🔵", "OI": "🟡", "ALGAR": "🟢"}
            
            for operadora, qtd in por_operadora.items():
                pct = (qtd / len(df_cancelados)) * 100
                emoji = emojis.get(operadora, "📡")
                resposta += f"| {emoji} {operadora} | {formatar_numero(qtd)} | {pct:.1f}% |\n"
        
        elif 'PROJETO' in df.columns:
            por_projeto = df_cancelados.groupby('PROJETO').size().sort_values(ascending=False).head(5)
            
            resposta += "**Top 5 Projetos:**\n\n"
            resposta += "| Projeto | Cancelados |\n"
            resposta += "|---------|------------|\n"
            
            for projeto, qtd in por_projeto.items():
                resposta += f"| {projeto} | {formatar_numero(qtd)} |\n"
        
        return resposta
    
    # ===== QUANTOS CHIPS POR PROJETO =====
    if ("quantos" in pergunta_lower or "total" in pergunta_lower) and \
       "chip" in pergunta_lower and "projeto" in pergunta_lower and \
       "cancelad" not in pergunta_lower and "venc" not in pergunta_lower:
        
        if 'PROJETO' not in df.columns:
            return "❌ Coluna PROJETO não encontrada."
        
        por_projeto = df.groupby('PROJETO').size().sort_values(ascending=False)
        
        resposta = f"## 📊 Distribuição de Chips por Projeto\n\n"
        resposta += f"**Total:** {formatar_numero(len(df))} chips em {len(por_projeto)} projetos\n\n"
        resposta += "| # | Projeto | Chips | % |\n"
        resposta += "|---|---------|-------|---------|\n"
        
        for i, (projeto, qtd) in enumerate(por_projeto.items(), 1):
            pct = (qtd / len(df)) * 100
            resposta += f"| {i} | {projeto} | {formatar_numero(qtd)} | {pct:.1f}% |\n"
        
        return resposta
    
    # ===== CHIPS SEM CONEXÃO 180+ DIAS =====
    if "180" in pergunta_lower or "sem conexão" in pergunta_lower or "sem conexao" in pergunta_lower:
        
        col_conexao = buscar_coluna(df, ['CATEGORIACONEXAO', 'CATEGORIA_CONEXAO', 'CATEGORIA CONEXAO', 'CONEXAO'])
        
        if not col_conexao:
            return "❌ Coluna de conexão não encontrada."
        
        categorias_disponiveis = df[col_conexao].unique()
        
        if 'Mais de 180 dias' not in categorias_disponiveis:
            return f"❌ Categoria 'Mais de 180 dias' não encontrada."
        
        sem_conexao = df[df[col_conexao] == 'Mais de 180 dias']
        
        if len(sem_conexao) == 0:
            return "## ✅ Conexões\n\n**Status:** Nenhum chip inativo há 180+ dias."
        
        pct = (len(sem_conexao) / len(df)) * 100
        
        resposta = f"## 🔴 Chips Inativos - 180+ dias\n\n"
        resposta += f"**Total:** {formatar_numero(len(sem_conexao))} chips ({pct:.1f}%)\n\n"
        
        if 'PROJETO' in df.columns:
            por_projeto = sem_conexao.groupby('PROJETO').size().sort_values(ascending=False)
            
            resposta += "| Projeto | Inativos | % |\n"
            resposta += "|---------|----------|---|\n"
            
            for projeto, qtd in por_projeto.items():
                pct_proj = (qtd / len(sem_conexao)) * 100
                resposta += f"| {projeto} | {formatar_numero(qtd)} | {pct_proj:.1f}% |\n"
            
            top_projeto = por_projeto.index[0]
            resposta += f"\n**📌 Ação:** Investigar inatividade no **{top_projeto}**."
        
        return resposta
    
    # ===== STATUS DAS ATIVAÇÕES =====
    if "ativa" in pergunta_lower and ("status" in pergunta_lower or "geral" in pergunta_lower):
        
        col_ativ = buscar_coluna(df, ['DATA DE ATIVAÇÃO', 'DATA_ATIVACAO', 'ATIVACAO'])
        
        if not col_ativ:
            return "❌ Coluna de ativação não encontrada."
        
        ativados = df[df[col_ativ].notna()]
        pct_ativados = (len(ativados) / len(df)) * 100
        
        resposta = f"## 📡 Status de Ativações\n\n"
        resposta += f"**Base:** {formatar_numero(len(df))} chips\n\n"
        resposta += "| Métrica | Quantidade | % |\n"
        resposta += "|---------|------------|---|\n"
        resposta += f"| ✅ Ativados | {formatar_numero(len(ativados))} | {pct_ativados:.1f}% |\n"
        resposta += f"| ⏳ Pendentes | {formatar_numero(len(df)-len(ativados))} | {100-pct_ativados:.1f}% |\n"
        
        if 'PROJETO' in df.columns and len(ativados) > 0:
            resposta += f"\n**Top 5 Projetos:**\n\n"
            resposta += "| Projeto | Ativados/Total | Taxa |\n"
            resposta += "|---------|----------------|------|\n"
            
            projetos_data = []
            for projeto in df['PROJETO'].unique():
                total_proj = len(df[df['PROJETO'] == projeto])
                ativ_proj = len(ativados[ativados['PROJETO'] == projeto])
                taxa = (ativ_proj / total_proj * 100) if total_proj > 0 else 0
                projetos_data.append((projeto, ativ_proj, total_proj, taxa))
            
            projetos_data.sort(key=lambda x: x[3], reverse=True)
            
            for projeto, ativ, total, taxa in projetos_data[:5]:
                emoji = "✅" if taxa >= 90 else "🟡" if taxa >= 75 else "🔴"
                resposta += f"| {projeto} | {formatar_numero(ativ)}/{formatar_numero(total)} | {taxa:.1f}% {emoji} |\n"
        
        return resposta
    
    # ===== DISTRIBUIÇÃO POR OPERADORA =====
    if "operadora" in pergunta_lower and "cancelad" not in pergunta_lower:
        
        if 'OPERADORA' not in df.columns:
            return "❌ Coluna OPERADORA não encontrada."
        
        por_operadora = df['OPERADORA'].value_counts().sort_values(ascending=False)
        
        resposta = f"## 📶 Distribuição por Operadora\n\n"
        resposta += f"**Total:** {formatar_numero(len(df))} chips\n\n"
        resposta += "| Operadora | Chips | % |\n"
        resposta += "|-----------|-------|---------|\n"
        
        emojis = {"CLARO": "🔴", "VIVO": "🟣", "TIM": "🔵", "OI": "🟡", "ALGAR": "🟢"}
        
        for operadora, qtd in por_operadora.items():
            pct = (qtd / len(df)) * 100
            emoji = emojis.get(operadora, "📡")
            resposta += f"| {emoji} {operadora} | {formatar_numero(qtd)} | {pct:.1f}% |\n"
        
        return resposta
    
    # ===== LICENÇAS EXPIRADAS =====
    if "expirad" in pergunta_lower or "vencidas" in pergunta_lower:
        
        col_venc = buscar_coluna(df, ['DATA DE VENCIMENTO', 'DATA_VENCIMENTO'])
        
        if not col_venc:
            return "❌ Coluna de vencimento não encontrada."
        
        try:
            if df[col_venc].dtype == 'object':
                df[col_venc] = pd.to_datetime(df[col_venc], errors='coerce')
            
            df_exp = df[(df[col_venc].notna()) & (df[col_venc] < hoje)]
        except:
            return "❌ Erro ao processar licenças expiradas."
        
        if len(df_exp) == 0:
            return "## ✅ Licenças Expiradas\n\n**Status:** Nenhuma licença expirada."
        
        pct_total = (len(df_exp) / len(df)) * 100
        
        resposta = f"## ⚠️ Licenças Expiradas\n\n"
        resposta += f"**Total:** {formatar_numero(len(df_exp))} licenças ({pct_total:.1f}%)\n\n"
        
        if 'PROJETO' in df.columns:
            por_projeto = df_exp.groupby('PROJETO').size().sort_values(ascending=False)
            
            resposta += "| Projeto | Expiradas | % do Projeto |\n"
            resposta += "|---------|-----------|-------------|\n"
            
            for projeto, qtd in por_projeto.items():
                total_proj = len(df[df['PROJETO'] == projeto])
                pct = (qtd / total_proj) * 100
                resposta += f"| {projeto} | {formatar_numero(qtd)} | {pct:.1f}% |\n"
        
        return resposta
    
    return None


def processar_pergunta(df, pergunta, dfcontratos=None, dftimeline=None):
    """Processa pergunta"""
    resposta_sql = executar_consulta_sql(df, pergunta)
    
    if resposta_sql:
        return resposta_sql
    
    colunas_disponiveis = df.columns.tolist()
    
    sugestoes = ["💡 **Não entendi a pergunta.**\n\n**Sugestões:**\n"]
    
    if 'PROJETO' in colunas_disponiveis:
        sugestoes.append("- Liste os projetos disponíveis")
        sugestoes.append("- Resumo do projeto [NOME]")
        sugestoes.append("- Quantos chips por projeto?")
    
    if 'DATA DE VENCIMENTO' in colunas_disponiveis or 'DATA_VENCIMENTO' in colunas_disponiveis:
        sugestoes.append("- Quais projetos vencem em 30 dias?")
        sugestoes.append("- Quantas licenças expiradas?")
    
    col_conexao = buscar_coluna(df, ['CATEGORIACONEXAO', 'CATEGORIA_CONEXAO'])
    if col_conexao:
        sugestoes.append("- Quantos chips sem conexão há 180 dias?")
    
    if 'OPERADORA' in colunas_disponiveis:
        sugestoes.append("- Qual a distribuição por operadora?")
    
    return "\n".join(sugestoes)


def render_chatbot(df, dfcontratos=None, dftimeline=None):
    """Renderiza chatbot com scroll - VERSÃO FINAL CORRIGIDA"""
    inicializar_chatbot()
    
    # Header
    st.markdown("""
    <div class="header-parallax">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">🤖</div>
            <div>
                <h1 style="color: white; font-size: 2rem; font-weight: 900; margin: 0;">Chatbot Inteligente</h1>
                <p style="color: #C5E1A5; font-size: 0.95rem; margin: 0.3rem 0 0 0; font-weight: 600;">
                    Análise de Dados • Business Intelligence • Base Mobile
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Botão limpar
    col1, col2, col3 = st.columns([1, 6, 1])
    with col3:
        if st.button("🗑️ Limpar", use_container_width=True, type="secondary"):
            st.session_state.chat_messages = []
            st.rerun()
    
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    # Perguntas sugeridas (SEM DUPLICAÇÃO - CHAVE ÚNICA)
    with st.expander("💬 **Análises Rápidas** (clique para expandir)", expanded=True):
        sugestoes = [
            ("📁", "Liste os projetos disponíveis"),
            ("📊", "Quantos chips por projeto?"),
            ("📅", "Quais projetos vencem em 30 dias?"),
            ("🔴", "Quantos chips sem conexão há 180 dias?"),
            ("📡", "Qual o status geral das ativações?"),
            ("📶", "Qual a distribuição por operadora?"),
        ]
        
        pergunta_escolhida = None
        
        for i in range(0, len(sugestoes), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(sugestoes):
                    emoji, texto = sugestoes[i]
                    # CHAVE ÚNICA: timestamp incluído
                    if st.button(f"{emoji}  {texto}", key=f"chatbot_sug_{i}", use_container_width=True, type="secondary"):
                        pergunta_escolhida = texto
            
            with col2:
                if i + 1 < len(sugestoes):
                    emoji, texto = sugestoes[i + 1]
                    # CHAVE ÚNICA: timestamp incluído
                    if st.button(f"{emoji}  {texto}", key=f"chatbot_sug_{i+1}", use_container_width=True, type="secondary"):
                        pergunta_escolhida = texto
    
    st.markdown("---")
    
    # ===== CHAT COM SCROLL - ALTURA 1100px =====
    st.markdown("### 💬 Conversação")
    
    chat_container = st.container(height=1100)
    
    with chat_container:
        if len(st.session_state.chat_messages) == 0:
            st.info("👋 Olá! Faça uma pergunta sobre os dados ou use os atalhos acima.")
        
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Input fixo
    st.markdown("---")
    
    prompt = pergunta_escolhida if pergunta_escolhida else st.chat_input("💭 Digite sua pergunta... (Ex: 'Resumo do projeto IAUPE')")
    
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with st.spinner("🔍 Analisando dados..."):
            resposta = processar_pergunta(df, prompt, dfcontratos, dftimeline)
            st.session_state.chat_messages.append({"role": "assistant", "content": resposta})
        
        st.rerun()
