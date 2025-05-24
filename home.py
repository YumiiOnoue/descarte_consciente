import streamlit as st
import google.generativeai as genai
import warnings

# Para ignorar mensagens de aviso
warnings.filterwarnings("ignore")

# Lista de produtos para descarte consciente
PRODUTOS = [
    "Plástico", "Papel", "Metal", "Lâmpadas", "Móveis", "Vidro",
    "Roupa velha", "Esponja de cozinha", "Pilhas e baterias",
    "Eletrônicos", "Óleo de cozinha usado", "Medicamentos vencidos"
]

# Função para converter texto para Markdown com bullets
def to_streamlit_markdown(text):
    text = text.replace('•', '  *')
    return text

# Função para obter instruções de descarte
def como_descartar(produto: str, modelo):
    prompt = f"""
Você é um assistente de pesquisa especializado em sustentabilidade. Responda com instruções claras e sucintas,
e em bullet points sobre como descartar corretamente o seguinte item:
Item: {produto}
Apresente somente as instruções de descarte do produto selecionado em bullet points claros e concisos.
"""
    resposta = modelo.generate_content(prompt)
    return resposta.text.strip()

# Função para obter locais de coleta
def contato_local(produto: str, localizacao: str, modelo):
    prompt = f"""
Você é um assistente. Liste possíveis locais de coleta ou descarte para o item "{produto}" em "{localizacao}".
Se possível, inclua somente na resposta:
- Nome do Local
- Endereço
- Telefone
- Horário de funcionamento
Dê a resposta sucinta em bullet points por local.
"""
    resposta = modelo.generate_content(prompt)
    return resposta.text.strip()

# --- Interface Streamlit ---

st.set_page_config(page_title="♻️ Descarte Consciente", layout="wide")

st.title("♻️ Sistema de Descarte Consciente ♻️")
st.markdown("Bem-vindo! Encontre informações sobre como descartar seus resíduos corretamente.")

# Configuração da API Key do Google
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❗️ A chave da API não foi encontrada.")
    st.stop()

# Inicialização do modelo
genai.configure(api_key=GOOGLE_API_KEY)
modelo = genai.GenerativeModel("gemini-2.0-flash")

# Estado da sessão
if 'instrucoes_descarte' not in st.session_state:
    st.session_state.instrucoes_descarte = ""
if 'locais_coleta' not in st.session_state:
    st.session_state.locais_coleta = ""
if 'produto_selecionado' not in st.session_state:
    st.session_state.produto_selecionado = None
if 'localizacao_usuario' not in st.session_state:
    st.session_state.localizacao_usuario = ""

# Inputs do usuário
st.header("Informações para Descarte")

col1, col2 = st.columns(2)

with col1:
    localizacao_usuario = st.text_input(
        "📍 Sua cidade e estado (ex: São Paulo, São Paulo):",
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

# Botão de busca
if st.button("🔍 Buscar Informações de Descarte", type="primary", use_container_width=True):
    if not st.session_state.localizacao_usuario.strip():
        st.warning("Por favor, insira sua localização.")
    elif not st.session_state.produto_selecionado:
        st.warning("Por favor, selecione um produto.")
    else:
        with st.spinner(f"Buscando informações para descarte de {st.session_state.produto_selecionado}..."):
            try:
                instrucoes = como_descartar(st.session_state.produto_selecionado, modelo)
                locais = contato_local(st.session_state.produto_selecionado, st.session_state.localizacao_usuario, modelo)

                st.session_state.instrucoes_descarte = to_streamlit_markdown(instrucoes)
                st.session_state.locais_coleta = to_streamlit_markdown(locais)

                if not instrucoes and not locais:
                    st.error("Não foi possível encontrar informações. Tente novamente ou verifique os termos da busca.")

            except Exception as e:
                st.error(f"Ocorreu um erro ao buscar as informações: {e}")
                st.session_state.instrucoes_descarte = ""
                st.session_state.locais_coleta = ""

# Exibição dos resultados
if st.session_state.produto_selecionado:
    st.markdown("---")
    st.subheader(f"🔎 Resultados para descartar: {st.session_state.produto_selecionado} em {st.session_state.localizacao_usuario}")

    if st.session_state.instrucoes_descarte:
        st.markdown("### 🗑️ Instruções para Descarte Correto")
        st.markdown(st.session_state.instrucoes_descarte, unsafe_allow_html=True)
    else:
        st.info("Nenhuma instrução de descarte encontrada para este item.")

    if st.session_state.locais_coleta:
        st.markdown("### 📍 Locais de Coleta Próximos")
        st.markdown(st.session_state.locais_coleta, unsafe_allow_html=True)
    else:
        st.info("Nenhum local de coleta encontrado para esta localização.")

st.markdown("---")
st.caption("Desenvolvido com Gemini e Streamlit.")


