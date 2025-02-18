# -*- coding: utf-8 -*-
"""Untitled34.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1uWzrVZny02KjyV-dksZKIxUF3pKG9Cag
"""

from flask import Flask, request, send_file, jsonify
from obspy import read
import requests
import io
import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Para evitar problemas de GUI en entornos sin pantalla
from flask_cors import CORS #problemas de idx (Agredado)

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas(Agregado)

# Función auxiliar para calcular la diferencia de tiempo
def calculate_time_difference(start, end):
    start_time = datetime.datetime.fromisoformat(start)
    end_time = datetime.datetime.fromisoformat(end)
    return (end_time - start_time).total_seconds() / 60  # Diferencia en minutos

# Ruta principal para manejar gráficos dinámicamente
@app.route('/generate_graph', methods=['GET'])
def generate_graph():
    try:
        # Obtener parámetros de la solicitud
        start = request.args.get('start')
        end = request.args.get('end')
        net = request.args.get('net')
        sta = request.args.get('sta')
        loc = request.args.get('loc')
        cha = request.args.get('cha')

        # Verificar que todos los parámetros estén presentes
        if not all([start, end, net, sta, loc, cha]):
            return jsonify({"error": "Faltan parámetros requeridos"}), 400

        # Calcular la diferencia de tiempo para decidir el tipo de gráfico
        interval_minutes = calculate_time_difference(start, end)
        if interval_minutes <= 30:
            return generate_sismograma(net, sta, loc, cha, start, end)
        else:
            return generate_helicorder(net, sta, loc, cha, start, end)

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

# Ruta para generar específicamente sismogramas
@app.route('/generate_sismograma', methods=['GET'])
def generate_sismograma_route():
    try:
        # Extraer parámetros de la solicitud
        start = request.args.get('start')
        end = request.args.get('end')
        net = request.args.get('net')
        sta = request.args.get('sta')
        loc = request.args.get('loc')
        cha = request.args.get('cha')

        # Validar los parámetros
        if not all([start, end, net, sta, loc, cha]):
            return jsonify({"error": "Faltan parámetros requeridos"}), 400

        # Llamar a la función de generación de sismogramas
        return generate_sismograma(net, sta, loc, cha, start, end)

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

# Ruta para generar específicamente helicorders
@app.route('/generate_helicorder', methods=['GET'])
def generate_helicorder_route():
    try:
        # Extraer parámetros de la solicitud
        start = request.args.get('start')
        end = request.args.get('end')
        net = request.args.get('net')
        sta = request.args.get('sta')
        loc = request.args.get('loc')
        cha = request.args.get('cha')

        # Validar los parámetros
        if not all([start, end, net, sta, loc, cha]):
            return jsonify({"error": "Faltan parámetros requeridos"}), 400

        # Llamar a la función de generación de helicorders
        return generate_helicorder(net, sta, loc, cha, start, end)

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

# Función para generar un sismograma
def generate_sismograma(net, sta, loc, cha, start, end):
    try:
        # Construir la URL para descargar datos
        url = f"http://osso.univalle.edu.co/fdsnws/dataselect/1/query?starttime={start}&endtime={end}&network={net}&station={sta}&location={loc}&channel={cha}&nodata=404"
        
        # Realizar la solicitud al servidor remoto
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": f"Error al descargar datos: {response.status_code}"}), 500

        # Procesar los datos MiniSEED
        mini_seed_data = io.BytesIO(response.content)
        try:
            st = read(mini_seed_data)
        except Exception as e:
            return jsonify({"error": f"Error procesando MiniSEED: {str(e)}"}), 500

        # Crear gráfico del sismograma
        tr = st[0]
        start_time = tr.stats.starttime.datetime
        times = [start_time + datetime.timedelta(seconds=sec) for sec in tr.times()]
        data = tr.data

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(times, data, color='black', linewidth=0.8)
        ax.set_title(f"Universidad Industrial de Santander UIS\nRed Sísmica de Monitoreo REDNE\n{start} - {end}") #, fontsize=5)
                                                            # ax.set_title(f"{start} - {end}")
        ax.set_xlabel("Tiempo (UTC Colombia)") #, fontsize=5) #ax.set_xlabel("Tiempo")
        ax.set_ylabel("Amplitud (M/s)") #, fontsize=5)        #ax.set_ylabel("Amplitud")
        fig.autofmt_xdate()

        # Agregar información de la estación en la esquina superior izquierda
        station_info = f"{net}.{sta}.{loc}.{cha}"
        ax.text(0.02, 0.98, station_info, transform=ax.transAxes, fontsize=10,verticalalignment='top', bbox=dict(facecolor='white', edgecolor='black'))

        # Rotar las etiquetas del eje X para mayor claridad
        fig.autofmt_xdate()

        # Guardar el gráfico en memoria
        output_image = io.BytesIO()
        plt.savefig(output_image, format='png', dpi=100, bbox_inches="tight")
        output_image.seek(0)
        plt.close(fig)

        return send_file(output_image, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

# Función para generar un helicorder
def generate_helicorder(net, sta, loc, cha, start, end):
    try:
        # Construir la URL para descargar datos
        url = f"http://osso.univalle.edu.co/fdsnws/dataselect/1/query?starttime={start}&endtime={end}&network={net}&station={sta}&location={loc}&channel={cha}&nodata=404"
        
        # Realizar la solicitud al servidor remoto
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": f"Error al descargar datos: {response.status_code}"}), 500

        # Procesar los datos MiniSEED
        mini_seed_data = io.BytesIO(response.content)
        try:
            st = read(mini_seed_data)
        except Exception as e:
            return jsonify({"error": f"Error procesando MiniSEED: {str(e)}"}), 500

        # Crear helicorder utilizando ObsPy
        fig = st.plot(
            type="dayplot",
            interval=15,
            right_vertical_labels=True,
            vertical_scaling_range=2000,
            color=['k', 'r', 'b'],
            show_y_UTC_label=True,
            one_tick_per_line=True
            #size=(12, 6)  # Ajustar el tamaño del gráfico
        )

        # Ajustar el tamaño del helicorder (matplotlib se encarga del tamaño)
        fig.set_size_inches(12, 4)  # Configura el tamaño del gráfico (ancho x alto)

        # Informción en el Helicorder
        ax = fig.gca()  # Obtener el eje actual (para agregar el texto)
        ax.text(0.02, 1.05, "Universidad Industrial de Santander UIS", transform=ax.transAxes, fontsize=10, verticalalignment='bottom', ha='left', color='black')
        ax.text(0.02, 1.1, "Red Sísmica de Monitoreo REDNE", transform=ax.transAxes, fontsize=10, verticalalignment='bottom', ha='left', color='black')
        ax.text(0.02, 1.15, f"Estructura de la fecha de: {start} - {end}", transform=ax.transAxes, fontsize=10, verticalalignment='bottom', ha='left', color='black')

        # Guardar el gráfico en memoria
        output_image = io.BytesIO()
        fig.savefig(output_image, format='png', dpi=120, bbox_inches="tight")
        output_image.seek(0)
        plt.close(fig)

        return send_file(output_image, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

# Punto de entrada del servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
