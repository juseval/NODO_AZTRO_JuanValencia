document.getElementById('calculadoraForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Obtener dimensiones de la pared en metros
    const paredAlto = parseFloat(document.getElementById('paredAlto').value);
    const paredAncho = parseFloat(document.getElementById('paredAncho').value);

    // Obtener dimensiones del ladrillo en centímetros y convertir a metros
    const ladrilloAlto = parseFloat(document.getElementById('ladrilloAlto').value) / 100;
    const ladrilloAncho = parseFloat(document.getElementById('ladrilloAncho').value) / 100;

    // Calcular área de la pared y del ladrillo
    const areaPared = paredAlto * paredAncho;
    const areaLadrillo = ladrilloAlto * ladrilloAncho;

    // Calcular número de ladrillos necesarios
    const numeroLadrillos = Math.ceil(areaPared / areaLadrillo);

    // Mostrar resultado
    document.getElementById('resultado').innerHTML = `
        <h3>Resultado:</h3>
        <p>Área de la pared: ${areaPared.toFixed(2)} m²</p>
        <p>Área de cada ladrillo: ${areaLadrillo.toFixed(4)} m²</p>
        <p>Número de ladrillos necesarios: ${numeroLadrillos}</p>
    `;
});