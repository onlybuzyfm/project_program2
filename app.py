from flask import Flask, render_template, request, jsonify
import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl

app = Flask(__name__, static_url_path='/statics')

# Definir variables difusas
glucosa = ctrl.Antecedent(np.arange(50, 301, 1), 'glucosa')
imc = ctrl.Antecedent(np.arange(10, 50, 1), 'imc')
riesgo_diabetes = ctrl.Consequent(np.arange(0, 101, 1), 'riesgo_diabetes')

# Funciones de membresía
glucosa['normal'] = fuzz.trimf(glucosa.universe, [50, 80, 100])
glucosa['prediabetes'] = fuzz.trimf(glucosa.universe, [100, 120, 125])
glucosa['diabetes'] = fuzz.trimf(glucosa.universe, [125, 150, 300])

imc['bajo'] = fuzz.trimf(imc.universe, [10, 15, 18.5])
imc['normal'] = fuzz.trimf(imc.universe, [18.5, 22, 25])
imc['alto'] = fuzz.trimf(imc.universe, [24, 30, 50])

riesgo_diabetes['bajo'] = fuzz.trimf(riesgo_diabetes.universe, [0, 20, 40])
riesgo_diabetes['moderado'] = fuzz.trimf(riesgo_diabetes.universe, [30, 50, 70])
riesgo_diabetes['alto'] = fuzz.trimf(riesgo_diabetes.universe, [60, 80, 100])

# Reglas difusas
reglas = [
    ctrl.Rule(glucosa['normal'] & imc['bajo'], riesgo_diabetes['bajo']),
    ctrl.Rule(glucosa['normal'] & imc['normal'], riesgo_diabetes['bajo']),
    ctrl.Rule(glucosa['normal'] & imc['alto'], riesgo_diabetes['moderado']),
    ctrl.Rule(glucosa['prediabetes'] & imc['bajo'], riesgo_diabetes['moderado']),
    ctrl.Rule(glucosa['prediabetes'] & imc['normal'], riesgo_diabetes['alto']),
    ctrl.Rule(glucosa['prediabetes'] & imc['alto'], riesgo_diabetes['alto']),
    ctrl.Rule(glucosa['diabetes'] & imc['bajo'], riesgo_diabetes['alto']),
    ctrl.Rule(glucosa['diabetes'] & imc['normal'], riesgo_diabetes['alto']),
    ctrl.Rule(glucosa['diabetes'] & imc['alto'], riesgo_diabetes['alto'])
]

sistema_ctrl = ctrl.ControlSystem(reglas)
sistema = ctrl.ControlSystemSimulation(sistema_ctrl)

# Función para calcular IMC
def calcular_imc(peso, altura):
    if altura > 0:  #para que no se pueda ingresar valores negativos
        return peso / (altura ** 2)
    else: 
        raise ValueError("La altura debe ser mayor de 0.")

# Ruta principal para cargar la interfaz
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para procesar los datos
@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        datos = request.json
        print(f"Datos Recibidos:{datos}")
        peso = float(datos['peso'])
        altura = float(datos['altura'])
        glucosa_input = float(datos['glucosa'])
        imc_calculado = calcular_imc(peso, altura)
        print(f"Glucosa: {glucosa_input}, IMC: {imc_calculado}, Riesgo: {resultado}")


        # Asignar valores al sistema difuso
        sistema.input['glucosa'] = glucosa_input
        sistema.input['imc'] = imc_calculado
        sistema.compute()

        resultado = round(sistema.output['riesgo_diabetes'], 2)
        print(f"Resultado del riesgo: {resultado}")
        return jsonify({'riesgo_diabetes': resultado})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
