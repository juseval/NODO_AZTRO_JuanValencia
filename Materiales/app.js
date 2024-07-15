function agregarProdcuto() {

    const productoAgregado = document.getElementById('producto').value;
    if(productoAgregado !=''){
        const listaCompra = document.getElementById(lista-compra');
        const nuevoLi = document.createElement('li')
    
    
        nuevoLi.textContent = productoAgregado;
    listaCompra.appendChild(nuevoLi);
    listaCompra.setAttribute

    elementoInput.style.border = "none";

    }else{
        const elementoInput = document.getElementById('producto');
        elementoInput.setAttribute("placeholder","No pudes dejar vacio el input");
        elementoiInput.style.border = "1px solid red"

}

}