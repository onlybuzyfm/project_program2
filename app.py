from flask import Flask, render_template, request, jsonify
import numpy as np
import Fuzz_Ia as Fy
from Fuzz_Ia import TriangularMF

app = Flask(__name__)


# Función para calcular IMC
def calcular_imc(peso, altura):
    if altura > 0:  # para que no se pueda ingresar valores negativos
        return peso / (altura**2)
    else:
        raise ValueError("La altura debe ser mayor de 0.")


glucose = Fy.FuzzyVariable("Glucose", np.linspace(50, 300, 100))

glucose.add_term(TriangularMF("Normal", 50, 80, 99))
glucose.add_term(TriangularMF("Prediabetes", 90, 110, 125))
glucose.add_term(TriangularMF("Diabetes", 120, 150, 300))


imc = Fy.FuzzyVariable("IMC", np.linspace(10, 50, 100))

imc.add_term(TriangularMF("Bajo", 10, 15, 18.5))
imc.add_term(TriangularMF("Normal", 18, 22, 24.9))
imc.add_term(TriangularMF("Sobrepeso", 23, 27, 29.9))
imc.add_term(TriangularMF("Obesidad Leve", 28, 32, 34.9))
imc.add_term(TriangularMF("Obesidad Moderada", 33, 37, 39.9))
imc.add_term(TriangularMF("Obesidad Severa", 38, 45, 50))

r_d = Fy.FuzzyVariable("Diabetes_R", np.linspace(0, 100, 100))

r_d.add_term(TriangularMF("Bajo", 0, 10, 30))
r_d.add_term(TriangularMF("Moderado", 25, 40, 55))  # Se desplazó un poco
r_d.add_term(
    TriangularMF("Alto", 50, 65, 80)
)  # Se redujo solapamiento con Moderado y Muy Alto
r_d.add_term(TriangularMF("Muy Alto", 75, 85, 95))
r_d.add_term(
    TriangularMF("Crítico", 92, 100, 100)
)  # Se redujo el inicio de Crítico para menos solapamiento


fis = Fy.FuzzySystem()

fis.output_range = r_d.range

fis.add_variable(glucose)
fis.add_variable(imc)
fis.add_variable(r_d)

# Glucosa Normal (Riesgo Bajo o Moderado)
fis.add_rule({'if': {'Glucose': 'Normal', 'IMC': 'Bajo'}, 'then': ('Diabetes_R', 'Bajo')})  # Saludable
fis.add_rule({'if': {'Glucose': 'Normal', 'IMC': 'Normal'}, 'then': ('Diabetes_R', 'Bajo')})  # Saludable
fis.add_rule({'if': {'Glucose': 'Normal', 'IMC': 'Sobrepeso'}, 'then': ('Diabetes_R', 'Moderado')})  # Riesgo leve
fis.add_rule({'if': {'Glucose': 'Normal', 'IMC': 'Obesidad Leve'}, 'then': ('Diabetes_R', 'Moderado')})  # Riesgo leve
fis.add_rule({'if': {'Glucose': 'Normal', 'IMC': 'Obesidad Moderada'}, 'then': ('Diabetes_R', 'Alto')})  # Riesgo intermedio
fis.add_rule({'if': {'Glucose': 'Normal', 'IMC': 'Obesidad Severa'}, 'then': ('Diabetes_R', 'Alto')})  # Riesgo intermedio

# Glucosa Prediabetes (Riesgo Moderado a Muy Alto)
fis.add_rule({'if': {'Glucose': 'Prediabetes', 'IMC': 'Bajo'}, 'then': ('Diabetes_R', 'Moderado')})  # Riesgo leve
fis.add_rule({'if': {'Glucose': 'Prediabetes', 'IMC': 'Normal'}, 'then': ('Diabetes_R', 'Alto')})  # Riesgo intermedio
fis.add_rule({'if': {'Glucose': 'Prediabetes', 'IMC': 'Sobrepeso'}, 'then': ('Diabetes_R', 'Muy Alto')})  # Riesgo alto
fis.add_rule({'if': {'Glucose': 'Prediabetes', 'IMC': 'Obesidad Leve'}, 'then': ('Diabetes_R', 'Muy Alto')})  # Riesgo alto
fis.add_rule({'if': {'Glucose': 'Prediabetes', 'IMC': 'Obesidad Moderada'}, 'then': ('Diabetes_R', 'Crítico')})  # Riesgo crítico
fis.add_rule({'if': {'Glucose': 'Prediabetes', 'IMC': 'Obesidad Severa'}, 'then': ('Diabetes_R', 'Crítico')})  # Riesgo crítico

# Glucosa Diabetes (Riesgo Alto a Crítico)
fis.add_rule({'if': {'Glucose': 'Diabetes', 'IMC': 'Bajo'}, 'then': ('Diabetes_R', 'Alto')})  # Riesgo alto
fis.add_rule({'if': {'Glucose': 'Diabetes', 'IMC': 'Normal'}, 'then': ('Diabetes_R', 'Muy Alto')})  # Riesgo muy alto
fis.add_rule({'if': {'Glucose': 'Diabetes', 'IMC': 'Sobrepeso'}, 'then': ('Diabetes_R', 'Crítico')})  # Riesgo crítico
fis.add_rule({'if': {'Glucose': 'Diabetes', 'IMC': 'Obesidad Leve'}, 'then': ('Diabetes_R', 'Crítico')})  # Riesgo crítico
fis.add_rule({'if': {'Glucose': 'Diabetes', 'IMC': 'Obesidad Moderada'}, 'then': ('Diabetes_R', 'Crítico')})  # Riesgo crítico
fis.add_rule({'if': {'Glucose': 'Diabetes', 'IMC': 'Obesidad Severa'}, 'then': ('Diabetes_R', 'Crítico')})  # Riesgo crítico

# Ruta principal para cargar la interfaz
@app.route("/")
def index():
    return render_template("index.html")


# Ruta para procesar los datos
@app.route("/calcular", methods=["POST"])
def calcular():
    try:
        datos = request.json
        print(f"Datos Recibidos:{datos}")

        # Captura de datos
        peso = float(datos["peso"])
        altura = float(datos["altura"])
        glucosa_input = float(datos["glucosa"])

        # Cálculo del IMC
        imc_calculado = calcular_imc(peso, altura)

        print(imc_calculado)

        # Definir los inputs del sistema difuso
        inputs = {"Glucose": glucosa_input, "IMC": imc_calculado}

        print(inputs)

        # Simulación del sistema difuso
        output = fis.simulate(inputs)
        print(output)
        resultado = round(output, 2)
        print(resultado)

        print(f"Glucosa: {glucosa_input}, IMC: {imc_calculado}, Riesgo: {resultado}")
        return jsonify({"riesgo_diabetes": resultado})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)


# # Definir variables difusas
# glucosa = ctrl.Antecedent(np.arange(50, 301, 1), 'glucosa')
# imc = ctrl.Antecedent(np.arange(10, 50, 1), 'imc')
# riesgo_diabetes = ctrl.Consequent(np.arange(0, 101, 1), 'riesgo_diabetes')

# # Funciones de membresía
# glucosa['normal'] = fuzz.trimf(glucosa.universe, [50, 80, 100])
# glucosa['prediabetes'] = fuzz.trimf(glucosa.universe, [100, 120, 125])
# glucosa['diabetes'] = fuzz.trimf(glucosa.universe, [125, 150, 300])

# imc['bajo'] = fuzz.trimf(imc.universe, [10, 15, 18.5])
# imc['normal'] = fuzz.trimf(imc.universe, [18.5, 22, 25])
# imc['alto'] = fuzz.trimf(imc.universe, [24, 30, 50])

# riesgo_diabetes['bajo'] = fuzz.trimf(riesgo_diabetes.universe, [0, 20, 40])
# riesgo_diabetes['moderado'] = fuzz.trimf(riesgo_diabetes.universe, [30, 50, 70])
# riesgo_diabetes['alto'] = fuzz.trimf(riesgo_diabetes.universe, [60, 80, 100])

# # Reglas difusas
# reglas = [
#     ctrl.Rule(glucosa['normal'] & imc['bajo'], riesgo_diabetes['bajo']),
#     ctrl.Rule(glucosa['normal'] & imc['normal'], riesgo_diabetes['bajo']),
#     ctrl.Rule(glucosa['normal'] & imc['alto'], riesgo_diabetes['moderado']),
#     ctrl.Rule(glucosa['prediabetes'] & imc['bajo'], riesgo_diabetes['moderado']),
#     ctrl.Rule(glucosa['prediabetes'] & imc['normal'], riesgo_diabetes['alto']),
#     ctrl.Rule(glucosa['prediabetes'] & imc['alto'], riesgo_diabetes['alto']),
#     ctrl.Rule(glucosa['diabetes'] & imc['bajo'], riesgo_diabetes['alto']),
#     ctrl.Rule(glucosa['diabetes'] & imc['normal'], riesgo_diabetes['alto']),
#     ctrl.Rule(glucosa['diabetes'] & imc['alto'], riesgo_diabetes['alto'])
# ]

# sistema_ctrl = ctrl.ControlSystem(reglas)
# sistema = ctrl.ControlSystemSimulation(sistema_ctrl)
