document.getElementById('tiempoNatacionForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Obtener los tiempos de las pruebas
    const tiempos = [];
    for (let i = 1; i <= 5; i++) {
        tiempos.push(parseFloat(document.getElementById(`tiempo${i}`).value));
    }

    // Calcular el promedio
    const promedio = tiempos.reduce((a, b) => a + b, 0) / tiempos.length;

    // Convertir el promedio a minutos y segundos
    const minutos = Math.floor(promedio / 60);
    const segundos = (promedio % 60).toFixed(2);

    // Mostrar resultado
    document.getElementById('resultado').innerHTML = `
        <h3>Resultado:</h3>
        <p>Promedio de tiempo: ${minutos} minutos y ${segundos} segundos</p>
        <p>(${promedio.toFixed(2)} segundos)</p>
    `;
});