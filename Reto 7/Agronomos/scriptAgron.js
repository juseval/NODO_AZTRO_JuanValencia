document.getElementById('calculadoraForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Obtener dimensiones del terreno
    const baseCorta = parseFloat(document.getElementById('baseCorta').value);
    const baseLarga = parseFloat(document.getElementById('baseLarga').value);
    const altura = parseFloat(document.getElementById('altura').value);
    const lado1 = parseFloat(document.getElementById('lado1').value);
    const lado2 = parseFloat(document.getElementById('lado2').value);

    // Calcular área del trapecio
    const area = ((baseCorta + baseLarga) / 2) * altura;

    // Calcular cantidad de pesticida necesario (1.5 litros por metro cuadrado)
    const pesticida = area * 1.5;

    // Calcular el perímetro para la cerca eléctrica
    const perimetro = baseCorta + baseLarga + lado1 + lado2;

    // Mostrar resultado
    document.getElementById('resultado').innerHTML = `
        <h3>Resultados:</h3>
        <p>Área del terreno: ${area.toFixed(2)} m²</p>
        <p>Pesticida necesario: ${pesticida.toFixed(2)} litros</p>
        <p>Longitud de cerca eléctrica necesaria: ${perimetro.toFixed(2)} metros</p>
    `;
});