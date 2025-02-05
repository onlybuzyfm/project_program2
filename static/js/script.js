document.getElementById("formulario").addEventListener("submit", function (event) {
    event.preventDefault(); // Evitar el envío tradicional del formulario

    // Obtener los valores del formulario
    const peso = document.getElementById("peso").value;
    const altura = document.getElementById("altura").value;
    const glucosa = document.getElementById("glucosa").value;

    // Validar que los datos estén completos
    if (peso && altura && glucosa) {
        // Crear el objeto de datos a enviar
        const datos = {
            peso: peso,
            altura: altura,
            glucosa: glucosa
        };

        // Enviar los datos al servidor usando Fetch API
        fetch("/calcular", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data); //Imprimir la respuesta en la consola para depuración
            // Mostrar el resultado del riesgo
            if (data.riesgo_diabetes !== undefined) {
                document.getElementById("resultado").innerHTML = `El riesgo de ser dignosticado con diabetes es: ${data.riesgo_diabetes}%`;
            } else {
                document.getElementById("resultado").innerHTML = `Error: ${data.error}`;
            }
        })
        .catch(error => {
            console.error(error);   //Ver el error en pantalla
            document.getElementById("resultado").innerHTML = `Error al calcular el riesgo. Intenta de nuevo.`;
        });
    } else {
        alert("Por favor, complete todos los campos.");
    }
});
