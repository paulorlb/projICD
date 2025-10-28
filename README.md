

# ICD 2025 2026
Este projeto suporta a componente aplicada da disciplina de [Introdução à Ciência dos Dados](https://www.ua.pt/pt/uc/15127), do plano curricular do [Mestrado em Ciência dos Dados para Ciências Sociais](http://cdcs.web.ua.pt/?page_id=616) da [Universidade de Aveiro](https://www.ua.pt/pt/c/473/p).


#### -- Estado do projeto: [ATIVO]


## Descrição e objetivos do projetos
Pretende-se, com este projeto, apoiar os estudantes - na sua maioria das ciências sociais - no desenvolvimento do trabalho prático, assente na aprendizagem e utilização de métodos e técnicas das áreas disciplinares das ciências dos dados para apoiar a produção de conhecimento sobre um dado tema.
Os alunos são convidados a inspirar-se em métodos de análise e revisão de literatura científica por forma a produzir conhecimento baseado em evidência que suporte a decisão.
Desta forma, os alunos serão convidados a definir e delimitar um tema, especificando os seus objectivos / o que querem saber (O quê?) desenhando procedimentos para obter respostas (Como?) e analisar os resultados obtidos (Porquê?).

## Objetivos de aprendizagem
Pretende-se que ao longo do projeto os alunos possam adquirir e aplicar conhecimento em domínios da ciência de dados particularmente próximos das disciplinas de ciênciais sociais, nomeadamente: análise de redes (sociais), aprendizagem automática a partir de dados textuais ("text mining" - incluindo processamento de linguagem natural e análise de contéudo / tópicos), culminando com a experimentação em  técnicas visuais de sistematização e comunicação de informação, que permita sumarizar (e comunicar) o conhecimento produzido.  


### Ferramentas Utilizadas
* API & Requests library
* JSON processing
* Pandas
* etc.

### Principais tecnologias
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)
![Scopus](https://a11ybadges.com/badge?logo=scopus)




## Requisitos

- recomenda-se a utilização do gestor de pacotes [Miniforge](https://github.com/conda-forge/miniforge), o qual suporta a criação de ambientes virtuais e a instalação de pacotes de forma eficiente de forma similar ao software conda (a maioria dos comandos conda podem ser accionados com mamba).

## Instruções iniciais

1. Clonar o [repositório](https://github.com/paulorlb/projICD).
2. Utilizar o ficheiro `projICDEnv.yaml` para criar um novo ambiente conda / mamba com o nome `projICD` e com todas as dependências necessárias para o projeto. Para isso, executar o seguinte comando no terminal do miniforge:
   ```
    mamba env create -f "./environment/projICDEnv.yaml"
    ```
3. Configurar / criar a pasta `data` para diretório de armazenamento de dados local.
4. Criar o ficheiro ".env" e inserir a "chave" pessoal da API Scopus"
5. etc...

  *Não esquecer: a pasta 'data' e o ficheiro .env não devem ser partilhados no GitHub!! Configurar corretamente o ficheiro '.gitignore' por forma assegurar*  




# Autor : [Paulo Batista](https://github.com/paulorlb])


