// Inicializar el mapa
const map = L.map('map-container').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Datos de los planes turísticos
const plans = [
  {
    title: 'Plan 1: Aventura en la Selva',
    description: 'Explora la selva amazónica y descubre sus maravillas naturales.',
    duration: '5 días',
    price: '$1,500',
    coordinates: [-3.7833, -73.0333]
  },
  {
    title: 'Plan 2: Relajación en la Costa',
    description: 'Disfruta de la playa y las actividades de ocio.',
    duration: '7 días',
    price: '$2,000',
    coordinates: [9.9333, -84.0833]
  },
  {
    title: 'Plan 3: Cultura en la Ciudad',
    description: 'Descubre la historia y la cultura de la ciudad.',
    duration: '3 días',
    price: '$800',
    coordinates: [19.4326, -99.1332]
  }
];

// Agregar marcadores al mapa
plans.forEach(plan => {
  const marker = L.marker(plan.coordinates).addTo(map);
  marker.on('click', () => {
    document.getElementById('plan-title').textContent = plan.title;
    document.getElementById('plan-description').textContent = plan.description;
    document.getElementById('plan-duration').textContent = plan.duration;
    document.getElementById('plan-price').textContent = plan.price;
  });
});