import shlex
import subprocess
from pathlib import Path
from modal import Image, Mount, App, web_server
import db_dtypes

# docker image and libraries
image = (Image.debian_slim(python_version="3.11.9")
         .pip_install("streamlit==1.36.0", "numpy==1.26.4", "pandas==1.5.3", "openpyxl==3.1.2",
                      "matplotlib==3.7.1", "python-dotenv==1.0.0",
                      "google-cloud-aiplatform==1.48.0", "plotly==5.14.0", "pillow==10.3.0",
                      "google-auth==2.29.0", "db-dtypes==1.2.0", "unicode==2.9", "Unidecode==1.3.6",
                      "wordcloud==1.9.1.1",
                      "selenium==4.9.1", "beautifulsoup4==4.12.2", "chromedriver-py==130.0.6723.44b0",
                      "streamlit-extras==0.4.3",  "streamlit-carousel==0.0.4", "langchain-google-genai==1.0.8",
                      "langchain==0.2.14", "langchain-core==0.2.33",
                      "langchain-experimental==0.0.64", "streamlit-modal==0.1.2")
         )

# Modal app
app = App(name="streamlit-promociones-v1", image=image)

# folders and files mount
streamlit_script_local_path_folder = Path(__file__).parent
streamlit_script_remote_path_folder = Path("/root/")

streamlit_script_local_path = Path(__file__).parent / "Home.py"                   # main file to run streamlit
streamlit_script_remote_path = streamlit_script_remote_path_folder / "Home.py"

if not streamlit_script_local_path.exists():
    raise RuntimeError(
        "Inicio.py not found! Place the script with your streamlit app in the same directory."
    )

streamlit_script_mount = Mount.from_local_file(local_path=streamlit_script_local_path,
                                               remote_path=streamlit_script_remote_path,
)

streamlit_folder_mount = Mount.from_local_dir(local_path=streamlit_script_local_path_folder,
                                              remote_path=streamlit_script_remote_path_folder,
)


# Inside the container, we will run the Streamlit server in a background subprocess using
# `subprocess.Popen`. We also expose port 8000 using the `@web_server` decorator.
@app.function(
    allow_concurrent_inputs=100,
    mounts=[streamlit_script_mount,
            streamlit_folder_mount,
            ],
    timeout=7200,
)
@web_server(8000)
def run():
    target = shlex.quote(str(streamlit_script_remote_path))
    cmd = f"streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    subprocess.Popen(cmd, shell=True)
