from . import db
from .models import Plants

def create_new_plant(id, name, time_light_on, light_indice, humidity_indice):
    new_plant = Plants(id, name, time_light_on, light_indice, humidity_indice)
    db.session.add(new_plant)
    db.session.commit()

