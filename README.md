# Trabalho 2 da disciplina de Engenharia de Software II.
O intuito do trabalho era colocar em prática conceitos sobre Data Warehouse vistos em sala de aula. Modelar um Data Warehouse, simples, com um objetivo genérico, realizar processos de ETL com a ferramenta Pentaho Data Integration, em cima de dados brutos em formato qualquer (csv, txt, json, ...), para popular o DataWarehouse.

Por fim realizar a elaboração de Dashboards com os dados do Data Warehouse.

---

O seguinte trabalho foi projetado para uma empresa fictícia de e-commerce que realiza vendas de produtos englobados no meio eletrônico usual.
---

<h3>Modelagem</h3> 
O Data Warehouse foi modelado, utilizando a ferramenta SQL Power Architect, da seguinte forma:

<img src='https://github.com/NickolasCrema/imagens_readmes/blob/main/Trabalho_2_ES2/modelo_logico.png?raw=true'/>

---

<h3>Os dados</h3>
Todos os dados contidos nesse trabalho foram fabricados, alguns à mão, alguns utilizando ferramentas auxiliares como ChatGPT.

---

<h3>ETL</h3>
As extrações, transformações e carregamento dos dados das fontes de dados brutos para o Data Warehouse foram feitas pela ferramenta Pentaho Data Integration.

---

<h3>Dashboards</h3>
As dashboards foram implementadas em Python, utilizando os módulos Streamlit e Plotly. Com intuito de demonstrar o desempenho da empresa no primeiro semestre do ano de 2023, e as geolocalizações mais impactantes em seu negócio (para uma possível estratégia de marketing).

<h4>Dashboard de receita</h4>
<img src='https://github.com/NickolasCrema/imagens_readmes/blob/main/Trabalho_2_ES2/Dashboard_receita.png?raw=true'/>

<h4>Dashboard de vendas</h4>
<img src='https://github.com/NickolasCrema/imagens_readmes/blob/main/Trabalho_2_ES2/Dashboard_vendas.png?raw=true'/>
