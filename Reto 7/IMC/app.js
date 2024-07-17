document.getElementById('imcForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const peso = parseFloat(document.getElementById('peso').value);
    const altura = parseFloat(document.getElementById('altura').value);
    
    const imc = peso / (altura * altura);
    
    let estado = '';
    if (imc < 16) {
        estado = 'Delgadez severa';
    } else if (imc >= 16 && imc < 17) {
        estado = 'Delgadez moderada';
    } else if (imc >= 17 && imc < 18.5) {
        estado = 'Delgadez aceptable';
    } else if (imc >= 18.5 && imc < 25) {
        estado = 'Peso normal';
    } else if (imc >= 25 && imc < 30) {
        estado = 'Sobrepeso';
    } else if (imc >= 30 && imc < 35) {
        estado = 'Obesidad tipo I';
    } else if (imc >= 35 && imc < 40) {
        estado = 'Obesidad tipo II';
    } else if (imc >= 40 && imc < 50) {
        estado = 'Obesidad tipo III (obesidad mórbida)';
    } else {
        estado = 'Obesidad tipo IV o extrema';
    }
    
    document.getElementById('resultado').innerHTML = `
        Su IMC es: ${imc.toFixed(2)}<br>
        Estado: ${estado}
    `;
});