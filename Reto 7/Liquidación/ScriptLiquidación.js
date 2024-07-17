document.getElementById('liquidacionForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const diasTrabajados = parseInt(document.getElementById('diasTrabajados').value);
    const horasExtrasDiurnas = parseInt(document.getElementById('horasExtrasDiurnas').value);
    const horasExtrasNocturnas = parseInt(document.getElementById('horasExtrasNocturnas').value);
    const horasExtrasFestivos = parseInt(document.getElementById('horasExtrasFestivos').value);
    
    const valorDiaTrabajado = 43000;
    const valorHoraExtraDiurna = 6915;
    const valorHoraExtraNocturna = 9681;
    const valorHoraExtraFestivo = 11064;
    
    const salarioBruto = (diasTrabajados * valorDiaTrabajado) +
                         (horasExtrasDiurnas * valorHoraExtraDiurna) +
                         (horasExtrasNocturnas * valorHoraExtraNocturna) +
                         (horasExtrasFestivos * valorHoraExtraFestivo);
    
    const descuentoSalud = salarioBruto * 0.04;
    const descuentoPension = salarioBruto * 0.04;
    const descuentoAlimentacion = salarioBruto * 0.03;
    
    const totalDescuentos = descuentoSalud + descuentoPension + descuentoAlimentacion;
    const salarioNeto = salarioBruto - totalDescuentos;
    
    document.getElementById('resultado').innerHTML = `
        <h2>Resultado de la Liquidación</h2>
        <p>Salario Bruto: $${salarioBruto.toFixed(2)}</p>
        <p>Descuento Salud (4%): $${descuentoSalud.toFixed(2)}</p>
        <p>Descuento Pensión (4%): $${descuentoPension.toFixed(2)}</p>
        <p>Descuento Alimentación (3%): $${descuentoAlimentacion.toFixed(2)}</p>
        <p>Total Descuentos: $${totalDescuentos.toFixed(2)}</p>
        <p>Salario Neto: $${salarioNeto.toFixed(2)}</p>
    `;
});