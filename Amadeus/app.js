const imagenes = ['./Imagenes/Carrusel1.jpg','./Imagenes/Carrusel2.jpg','./Imagenes/Carrusel3.jpg','./Imagenes/Carrusel4.jpg','./Imagenes/Carrusel5.jpg']

fondo = document.querySelectorAll('.imagenes');
let contador=0;

fondo.forEach(e => {
  e.style.backgroundImage=`Url(${imagenes[contador]})`;
  e.style.backgroundRepeat=`noRepeat`;
  e.style.backgroundSize=`cover`;
  e.style.backgroundPosition=`center`;
  contador++
});


const carouselItems = document.querySelectorAll('.carrusel .imagenes');

carouselItems.forEach(item => {
  item.addEventListener('mouseenter', () => {
    carouselItems.forEach(i => i.classList.remove('mostrar'));
    item.classList.add('mostrar');
  });

  item.addEventListener('mouseleave', () => {
    item.classList.remove('mostrar');
  });
});