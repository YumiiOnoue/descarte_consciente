# ♻️ Sistema de Descarte Consciente ♻️

Este projeto utiliza a API Places do Google para auxiliar usuários a encontrar locais de descarte consciente na localização desajada. 
Através de uma interface simples e intuitiva, o usuário pode buscar por diferentes tipos de materiais recicláveis e o sistema listará os pontos de coleta da sua cidade.

# Funcionalidades Principais

* **Busca por tipo de material:** Permite ao usuário selecionar o tipo de material que deseja descartar (ex: papel, plástico, metal, vidro, eletrônicos).
* **Instruções de Descarte:** Fornece instruções sobre a forma correta de descartar o produto selecionado, buscando informações relevantes e confiáveis na web.
* **Listagem de locais:** Exibe uma lista de locais de descarte, incluindo nome, endereço e informações adicionais como horário de funcionamento.

# Tecnologias Utilizadas
* **Google AI for Developers Kit (ADK):**
    * `google.adk.agents`: Para a criação dos agentes autônomos.
    * `google.adk.runners`: Para a execução dos agentes.
    * `google.adk.sessions`: Para o gerenciamento das sessões de interação.
    * `google.adk.tools.google_search`: Para a integração da busca do Google nos agentes.
* **Google Generative AI API:**
    * `google.genai`: Para a interação com os modelos de linguagem generativa.
    * `google.genai.types`: Para a definição dos tipos de conteúdo.
* **Bibliotecas Python:**
    * `datetime`: Para manipulação de datas.
    * `textwrap`: Para formatação de texto.
    * `requests`: Para requisições HTTP (uso potencial para interagir com APIs).
    * `warnings`: Para gerenciamento de avisos.
    * `os`: Para interação com o sistema operacional.
* **Google Colab:**
    * `google.colab.userdata`: Para acesso seguro a dados (como chaves de API).
    * `IPython.display`: Para exibição formatada de conteúdo (Markdown, HTML).

# Contexto do Projeto
Este projeto foi desenvolvido para aplicar os conhecimentos adquiridos na Imersão IA da Alura + Gemini, explorando o uso de agentes autônomos e modelos de linguagem na resolução de um problema prático.
