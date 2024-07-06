let boton = document.querySelector('#reto');
let ul = document.querySelector('.reto5');

boton.addEventListener('click', function(e){
  if (ul.style.display==='') {
    ul.style.display='flex';
  }else if (ul.style.display==='flex') {
    ul.style.display='';
  }
})