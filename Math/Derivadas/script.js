// Asegúrate de haber incluido math.js en tu HTML antes de este script

// Función para inicializar la calculadora
function inicializarCalculadora() {
    const botones = [
        '7', '8', '9', '/', 'ln',
        '4', '5', '6', '*', 'log',
        '1', '2', '3', '-', 'pi',
        '0', '.', '^', '+', 'e',
        '(', ')', 'x', 'C', '∞',
        '1/x', 'sin', 'cos', 'tan', 'sqrt'
    ];

    const calculadora = document.getElementById('calculator');
    botones.forEach(boton => {
        const btnElement = document.createElement('button');
        btnElement.textContent = boton;
        btnElement.onclick = () => agregarAlInput(boton);
        calculadora.appendChild(btnElement);
    });
}

// Función para agregar símbolos al input
function agregarAlInput(simbolo) {
    const input = document.getElementById('function-input');
    if (simbolo === 'C') {
        input.value = '';
    } else if (simbolo === '1/x') {
        input.value += '1/';
    } else if (simbolo === 'pi') {
        input.value += 'pi';
    } else if (simbolo === '∞') {
        input.value += 'Infinity';
    } else if (['ln', 'log', 'sin', 'cos', 'tan', 'sqrt'].includes(simbolo)) {
        input.value += simbolo + '(';
    } else {
        input.value += simbolo;
    }
}

// Función principal para calcular la derivada
function calcularDerivada() {
    const funcionInput = document.getElementById('function-input').value;
    const resultadoDiv = document.getElementById('result');
    
    try {
        // Paso 1: Identificar la función
        resultadoDiv.innerHTML = `
            <h2>Derivada de ${funcionInput}</h2>
            <h3>Paso 1: Identificar la función</h3>
            <p>La función ingresada es: ${funcionInput}</p>
        `;

        // Paso 2: Simplificar la función (si es necesario)
        const funcionSimplificada = math.simplify(funcionInput);
        if (funcionSimplificada.toString() !== funcionInput) {
            resultadoDiv.innerHTML += `
                <h3>Paso 2: Simplificar la función</h3>
                <p>Función simplificada: ${funcionSimplificada.toString()}</p>
            `;
        }

        // Paso 3: Calcular la derivada
        const derivada = math.derivative(funcionInput, 'x');
        resultadoDiv.innerHTML += `
            <h3>Paso 3: Aplicar reglas de derivación</h3>
            <p>Utilizamos las reglas de derivación para calcular:</p>
            <p>d/dx(${funcionInput}) = ${derivada.toString()}</p>
        `;

        // Paso 4: Simplificar el resultado (si es posible)
        const derivadaSimplificada = math.simplify(derivada);
        if (derivadaSimplificada.toString() !== derivada.toString()) {
            resultadoDiv.innerHTML += `
                <h3>Paso 4: Simplificar el resultado</h3>
                <p>Derivada simplificada: ${derivadaSimplificada.toString()}</p>
            `;
        }

        // Resultado final
        resultadoDiv.innerHTML += `
            <h3>Resultado final</h3>
            <p>La derivada de ${funcionInput} es: ${derivadaSimplificada.toString()}</p>
        `;

    } catch (error) {
        resultadoDiv.innerHTML = `<p>Error: ${error.message}</p>`;
    }
}

// Inicializar la calculadora cuando se carga la página
window.onload = inicializarCalculadora;