import os
import logging

from herbalia import create_app
app = create_app()

# Configuração do log
app.logger.setLevel(logging.INFO)
log_handler = logging.FileHandler('app.log')
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(log_handler)


