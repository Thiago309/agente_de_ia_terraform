# =======================================================
# Agente de IA Terraform com leitura de arquivo de saída.
# =======================================================
import os
import streamlit as st
import uuid
from crewai import Agent, Task, Crew
from crewai.process import Process
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Gerador IaC com Agente de IA",
    layout="wide"
)

st.title("Gerador de Scripts Terraform com Agente de IA utilizando LLM Groq.")
st.markdown("""
Esta ferramenta utiliza um Agente de IA de alta velocidade para converter suas descrições de infraestrutura em código Terraform (HCL).
""")

# Configuração do Modelo de Linguagem (LLM)
groq_llm = None
try:
    groq_llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="groq/llama3-70b-8192"
    )
except Exception as e:
    st.error(
        f"Erro ao inicializar o modelo da Groq: {e}. Verifique se a sua GROQ_API_KEY está configurada no arquivo .env.")

# Definição do Agente de IA
terraform_expert = Agent(
    role='Especialista Sênior em Infraestrutura como Código',
    goal='Criar scripts Terraform precisos, eficientes e seguros com base nos requisitos do usuário.',
    backstory=(
        "Você é um Engenheiro de DataOps altamente experiente com uma década de experiência na automação "
        "de provisionamento de infraestrutura na nuvem usando Terraform. Sua missão é traduzir "
        "descrições de alto nível da infraestrutura desejada em código Terraform pronto para produção."
    ),
    verbose=True,
    allow_delegation=False,
    llm=groq_llm
)

# Interface do Usuário
st.header("Descreva a Infraestrutura Desejada")

prompt = st.text_area(
    "Forneça um prompt claro e detalhado.",
    height=150,
    placeholder="Exemplo: Crie o código IaC com Terraform para um servidor web EC2 na AWS, usando uma instância t2.micro com a imagem AMI mais recente do Ubuntu 22.04 LTS."
)

if st.button("Gerar Script Terraform", type="primary", disabled=(not groq_llm)):
    if prompt:
        with st.spinner("O Agente de IA está trabalhando em alta velocidade..."):

            output_filename = "terraform_script.tf"

            try:
                # 1. DEFINIÇÃO DA TAREFA COM ARQUIVO DE SAÍDA
                terraform_task = Task(
                    description=(
                        "Sua única e exclusiva função é gerar um bloco de código Terraform (HCL). "
                        "Não escreva absolutamente nada antes ou depois do bloco de código. "
                        "Não inclua frases como 'Aqui está o código' ou 'Este script irá...'. "
                        "Sua saída deve começar diretamente com `provider \"aws\" {` ou `resource \"aws_s3_bucket\" \"main\" {` "
                        "e terminar com o último `}`. "
                        f"A solicitação do usuário é: '{prompt}'"
                    ),
                    expected_output='Um único bloco de código HCL, sem nenhum texto adicional, explicação, introdução ou conclusão.',
                    agent=terraform_expert,
                    output_file=output_filename
                )

                # 2. CRIAÇÃO E EXECUÇÃO DA EQUIPE
                terraform_crew = Crew(
                    agents=[terraform_expert],
                    tasks=[terraform_task],
                    process=Process.sequential,
                    verbose=True
                )

                # Executa a tarefa. O resultado com os logs é ignorado.
                terraform_crew.kickoff()

                # 3. LEITURA DO RESULTADO A PARTIR DO ARQUIVO
                with open(output_filename, 'r') as f:
                    result_code = f.read()

                # Exibição do Resultado
                st.header("Resultado Gerado")
                st.code(result_code, language='terraform')
                st.success("Script gerado com sucesso!")

            except Exception as e:
                st.error(f"Ocorreu um erro durante a execução da tarefa: {e}")
            finally:
                # 4. LIMPEZA
                if os.path.exists(output_filename):
                    os.remove(output_filename)
    else:
        st.warning("Por favor, insira uma descrição da infraestrutura.")