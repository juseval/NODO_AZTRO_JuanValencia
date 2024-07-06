// Función para calcular las propiedades de una figura geométrica
function calcularFigura(figura) {
    const inputValues = Array.from(document.querySelectorAll(`#${figura} input`));
    const outputElements = Array.from(document.querySelectorAll(`#${figura} .output-group span`));
    const explicacionElement = document.getElementById(`explicacion-${figura}`);
  
    // Obtener los valores de entrada y calcular las propiedades
    const values = inputValues.map(input => parseFloat(input.value));
    let area, perimetro, diagonal, explanation;
  
    if (values.every(isFinite)) {
      switch (figura) {
        case 'rectangulo':
          const [base, altura] = values;
          area = base * altura;
          perimetro = 2 * (base + altura);
          diagonal = Math.sqrt(base ** 2 + altura ** 2);
          explanation = `Área = base × altura = ${base} × ${altura} = ${area.toFixed(2)}`;
          explanation += ` Perímetro = 2 × (base + altura) = 2 × (${base} + ${altura}) = ${perimetro.toFixed(2)}\n`;
          explanation += ` Diagonal = √(base² + altura²) = √(${base}² + ${altura}²) = ${diagonal.toFixed(2)}`;
          break;
        case 'circulo':
          const [radio] = values;
          area = Math.PI * radio ** 2;
          perimetro = 2 * Math.PI * radio;
          explanation = `Área = π × radio² = π × ${radio}² = ${area.toFixed(2)}`;
          explanation += `\nPerímetro = 2 × π × radio = 2 × π × ${radio} = ${perimetro.toFixed(2)}`;
          break;
      }
    } else {
      area = perimetro = diagonal = 'Ingresa valores válidos';
      explanation = 'Por favor, ingresa valores válidos para calcular las propiedades.';
    }
  
    // Mostrar los resultados
    outputElements[0].textContent = area.toFixed(2);
    outputElements[1].textContent = perimetro.toFixed(2);
    if (diagonal !== undefined) {
      outputElements[2].textContent = diagonal.toFixed(2);
    }
    
    explicacionElement.textContent = explanation;
  }
  
  // Agregar eventos de clic a los botones de calcular
  document.querySelectorAll('button[id^="calcular"]').forEach(button => {
    button.addEventListener('click', () => calcularFigura(button.id.replace('calcular-', '')));
  });
  