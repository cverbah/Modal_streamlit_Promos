# :construction: Streamlit App :construction:
Project powered mainly by langchain :bird: , streamlit, selenium, beautifulsoup and pandas<br>
- The main idea of this project is to extract relevant data from promotions/banners from retails home pages using multimodal models:
  - Websites Scrapping
  - Data extraction from images using multimodal models
  - Dashboards
  - AI Assistants built with LLMs models from: Google, OpenAI
  - Tables and Plot generation from dataframes using LLM models
    
- under construction ... :construction:

For running the app: <br>
1. `pip install -r requirements.txt`
2. `streamlit run Home.py`  <br>

For scrapping a retail and analyzing the promos: <br>
1. `python scrapper.py {retail_name}` 
2. `python promos_analyzer.py {retail_name}`

available retail_names: {'falabella', 'paris', 'lider-supermercado', 'lider-catalogo', 'jumbo'}

* Be sure to be running the same version of  the lib: chromedriver-py and chrome, otherwise the script wont work.
