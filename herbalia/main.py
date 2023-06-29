from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
main = Blueprint('main', __name__)
import paho.mqtt.client as mqtt
from .crud import create_new_plant
from . import db
import json

# Define as informações de conexão do servidor MQTT
MQTT_BROKER = 'broker.hivemq.com'
MQTT_PORT = 1883

@main.route('/', methods=['GET', 'POST'])
def index():    
    return render_template('index.html')

@main.route('/new_plant', methods=['GET', 'POST'])
@login_required
def new_plant():
    if request.method == 'POST':
        # Retrieve data from the form
        data0 = request.form['data0']
        data1 = request.form['data1']
        data2 = request.form['data2']
        data3 = request.form['data3']
        # Process the data or perform any necessary operations

        create_new_plant(current_user.get_id(), data0, data1, data2, data3)
        # Fetch all plants belonging to the current user
    
        return render_template('new_plant.html')
    return render_template('new_plant.html')


@main.route('/plant/<int:plant_id>')
@login_required
def view_plant(plant_id):
    from .models import Plants
    plant = Plants.query.get(plant_id)
    return render_template('plant_details.html', plant=plant)

@main.route('/plant/delete/<int:plant_id>')
@login_required
def delete_plant(plant_id):
    from .models import Plants
    plant = Plants.query.get(plant_id)
    if plant:
        # Delete the plant from the database
        db.session.delete(plant)
        db.session.commit()
    
    return redirect(url_for('main.index'))

@main.route('/plant/send_mttq/<int:plant_id>')
@login_required
def send_mttq(plant_id):
    from .models import Plants
    plant = Plants.query.filter_by(id=plant_id).first()
    print("ID ", plant_id)
    print("GOT ", plant)
    if plant:
        
        payload = {
            'time_light_on': plant.time_light_on,
            'light_indice': plant.light_indice,
            'humidity_indice': plant.humidity_indice
        }
        
        import psutil
        import time
        client = mqtt.Client()

        # Conecta o cliente ao servidor MQTT
        client.connect(MQTT_BROKER, MQTT_PORT)

        # Envia o uso de memória do sistema a cada 5 segundos
        for i in range(1000):
           
            client.publish('herbalia', payload=str(payload))
            print("sent msg: ", str(payload))

    
    return redirect(url_for('main.index'))


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
