conda create -n bot python=3.13 -y
conda activate bot
pip install aiogram
conda install setuptools
conda install sqlalchemy asyncpg
conda env export > environment.yml
pip freeze > requirements.txt
conda install config
conda install requests
pip install yandex-cloud-ml-sdk