import streamlit as st
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types as genai_types
import google.generativeai as genai
import os
import textwrap
import warnings
import asyncio
import nest_asyncio 

# Para ignorar todas as mensagens de aviso
warnings.filterwarnings("ignore")

nest_asyncio.apply()

# Lista de produtos para descarte consciente
PRODUTOS = [
    "Plástico", "Papel", "Metal", "Lâmpadas", "Móveis", "Vidro",
    "Roupa velha", "Esponja de cozinha", "Pilhas e baterias",
    "Eletrônicos", "Óleo de cozinha usado", "Medicamentos vencidos"
]

MODELO_GEMINI = "gemini-2.0-flash"

# Função auxiliar que envia uma mensagem para um agente via Runner e retorna a resposta final
def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="streamlit_user", session_id="streamlit_session")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = genai_types.Content(role="user", parts=[genai_types.Part(text=message_text)])

    final_response = ""
    

    async def get_response(runner, content): # Passe runner e content como argumentos
        res = ""
        # Verifique se runner.run() é uma corrotina que retorna um iterador assíncrono
        # Se sim, use 'await' aqui. Se não, o problema pode estar no próprio runner.run()
        async for event in runner.run(user_id="streamlit_user", session_id="streamlit_session", new_message=content):
            if event.is_final_response():
                for part in event.content.parts:
                    if part.text is not None:
                        res += part.text
                        res += "\n"
        return res

    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            final_response = loop.run_until_complete(get_response())
        else:
            final_response = asyncio.run(get_response())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            st.error("Erro de loop de eventos asyncio. Considere usar `nest_asyncio` ou executar a chamada do agente em um thread separado para Streamlit.")
            final_response = "Erro ao processar a chamada do agente devido a conflito de loop de eventos."
        elif "There is no current event loop in thread" in str(e):
            # Tenta criar um novo loop de eventos se não houver um.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            final_response = loop.run_until_complete(get_response())
            loop.close()
        else:
            st.error(f"Erro inesperado com asyncio: {e}")
            final_response = "Erro ao processar a chamada do agente."

    return final_response

# Função para formatar texto para Markdown 
def to_streamlit_markdown(text):
  text = text.replace('•', '  *')
  return text

# Agente 2 - Como descartar 
def como_descartar(produto_selecionado: str, api_key: str):
    genai.configure(api_key=api_key) # Configura a API key para esta chamada
    
    buscar_agent = Agent(
        name="como_descartar_streamlit",
        model=MODELO_GEMINI, # Use o modelo configurado
        instruction="""
        Você é um assistente de pesquisa especializado em sustentabilidade.
        Sua tarefa é usar a ferramenta de busca do Google (google_search) para encontrar e listar
        a forma correta de descarte para o produto fornecido.
        Apresente somente as instruções de descarte do produto selecionado em bullet points claros e concisos.
        Priorize informações de fontes confiáveis e especialistas da área.
        Se houver múltiplas formas de descarte, mencione as mais recomendadas.
        """,
        description="Agente que busca informações de descarte no Google",
        tools=[google_search]
    )
    forma_descarte_query = f"Como descartar corretamente o seguinte item: {produto_selecionado}?"
    return call_agent(buscar_agent, forma_descarte_query)

# Agente 3 - Locais de Descarte e Contatos
def contato_local(produto_selecionado: str, minha_localizacao: str, api_key: str):
    genai.configure(api_key=api_key) # Configura a API key para esta chamada

    local_agent = Agent(
        name="contato_local_streamlit",
        model=MODELO_GEMINI, # Use o modelo configurado
        instruction=f"""
        Você é um assistente pessoal. Sua tarefa é, usando a ferramenta de pesquisa do Google (google_search),
        encontrar local de coleta ou descarte para o '{produto_selecionado}', considerando a seguinte localização: '{minha_localizacao}'.
        Liste informações de contato desses locais.
        Para cada local encontrado, forneça de forma sucinta (se disponível na pesquisa):
        - Nome do Local:
        - Endereço:
        - Telefone:
        - Horário de funcionamento:
        Se informações detalhadas não estiverem disponíveis para todos os campos, forneça o que encontrar.
        Priorize informações de contato direto.
        """,
        description="Agente que busca o contato dos locais de coleta no Google",
        tools=[google_search]
    )
    contato_coleta_query = (
        f"Liste informações de contato (nome, endereço, telefone, horário) de locais "
        f"que coletam '{produto_selecionado}' em '{minha_localizacao}'."
    )
    return call_agent(local_agent, contato_coleta_query)

# --- Interface Streamlit ---

st.set_page_config(page_title="♻️ Descarte Consciente", layout="wide")

st.title("♻️ Sistema de Descarte Consciente ♻️")
st.markdown("Bem-vindo! Encontre informações sobre como descartar seus resíduos corretamente.")

# Configuração da API Key do Google
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

# Inicializar o estado da sessão para armazenar os resultados
if 'instrucoes_descarte' not in st.session_state:
    st.session_state.instrucoes_descarte = ""
if 'locais_coleta' not in st.session_state:
    st.session_state.locais_coleta = ""
if 'produto_selecionado' not in st.session_state:
    st.session_state.produto_selecionado = None
if 'localizacao_usuario' not in st.session_state:
    st.session_state.localizacao_usuario = ""

# Inputs do Usuário
st.header("Informações para Descarte")

col1, col2 = st.columns(2)

with col1:
    localizacao_usuario = st.text_input(
        "📍 Sua cidade e estado (ex: Maringá, Paraná):",
        value=st.session_state.localizacao_usuario
    )
    st.session_state.localizacao_usuario = localizacao_usuario


with col2:
    produto_selecionado_ui = st.selectbox(
        "🗑️ Selecione o produto para descarte:",
        options=[""] + PRODUTOS,  
        index=0 if not st.session_state.produto_selecionado else PRODUTOS.index(st.session_state.produto_selecionado) + 1,
        format_func=lambda x: "Selecione um item..." if x == "" else x
    )
    if produto_selecionado_ui: 
        st.session_state.produto_selecionado = produto_selecionado_ui
    else: 
        st.session_state.produto_selecionado = None


if st.button("🔍 Buscar Informações de Descarte", type="primary", use_container_width=True):
    if not GOOGLE_API_KEY:
        st.error("Por favor, configure sua GOOGLE_API_KEY na barra lateral.")
    elif not st.session_state.localizacao_usuario or not st.session_state.localizacao_usuario.strip():
        st.warning("Por favor, insira sua localização.")
    elif not st.session_state.produto_selecionado:
        st.warning("Por favor, selecione um produto.")
    else:
        with st.spinner(f"Buscando informações para descarte de {st.session_state.produto_selecionado}..."):
            try:
                instrucoes = como_descartar(st.session_state.produto_selecionado, GOOGLE_API_KEY)
                st.session_state.instrucoes_descarte = to_streamlit_markdown(instrucoes)

                locais = contato_local(st.session_state.produto_selecionado, st.session_state.localizacao_usuario, GOOGLE_API_KEY)
                st.session_state.locais_coleta = to_streamlit_markdown(locais)

                if not st.session_state.instrucoes_descarte and not st.session_state.locais_coleta:
                    st.error("Não foi possível encontrar informações. Tente novamente ou verifique os termos da busca.")

            except Exception as e:
                st.error(f"Ocorreu um erro ao buscar as informações: {e}")
                st.session_state.instrucoes_descarte = ""
                st.session_state.locais_coleta = ""

# Exibição dos Resultados
if st.session_state.produto_selecionado:
    st.markdown("---")
    st.subheader(f"🔎 Resultados para: {st.session_state.produto_selecionado} em {st.session_state.localizacao_usuario}")

    if st.session_state.instrucoes_descarte:
        st.markdown("### 🗑️ Instruções para Descarte Correto")
        st.markdown(st.session_state.instrucoes_descarte, unsafe_allow_html=True) 
    else:
        # Se o botão foi clicado mas não houve resultado para instruções
        if st.session_state.get('_search_triggered_flag', False): # Flag para saber se a busca foi tentada
             st.info("Nenhuma instrução de descarte encontrada para este item.")


    if st.session_state.locais_coleta:
        st.markdown("### 📍 Locais de Coleta Próximos")
        st.markdown(st.session_state.locais_coleta, unsafe_allow_html=True)
    else:
        if st.session_state.get('_search_triggered_flag', False):
            st.info(f"Nenhum local de coleta encontrado para '{st.session_state.produto_selecionado}' em '{st.session_state.localizacao_usuario}'.")

# Para o flag de busca:
if st.button: # Se o botão foi pressionado na última execução
    st.session_state._search_triggered_flag = True
else:
    if '_search_triggered_flag' not in st.session_state: # Inicializa se não existir
        st.session_state._search_triggered_flag = False
    # Não reseta aqui, para que a mensagem "nenhum resultado" persista até nova busca ou mudança de inputs

st.markdown("---")
st.caption("Desenvolvido com IA e Streamlit.")