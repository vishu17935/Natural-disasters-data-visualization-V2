(function() {
    function initializeGlobe() {
        function waitForGlobeContainer() {
    let attempts = 0;
    const maxAttempts = 100; // 10 seconds max
    
    const interval = setInterval(() => {
        const container = document.getElementById("globe-container");
        attempts++;
        
        if (container && typeof Globe !== "undefined") {
            clearInterval(interval);
            initGlobe(container);
        } else if (attempts >= maxAttempts) {
            clearInterval(interval);
            console.error("❌ Globe container not found after 10 seconds");
        }
    }, 100);
}

function initGlobe(container) {
  const world = Globe()(container)
    .globeImageUrl('https://raw.githubusercontent.com/vasturiano/three-globe/master/example/img/earth-night.jpg')
    .atmosphereColor('white')
    .atmosphereAltitude(0.15);

  world.camera().position.z = 280;

  const cities = [
    // 🌍 Equatorial Cities
  
{ lat: 1.3521, lng: 103.8198, size: 0.15, color: 'gold' },        // Singapore
{ lat: 1.4927, lng: 103.7414, size: 0.15, color: 'orange' },      // Johor Bahru, Malaysia
{ lat: 1.0456, lng: 104.0305, size: 0.15, color: 'yellow' },      // Batam, Indonesia

];

  world
    .pointsData(cities)
    .pointLat(d => d.lat)
    .pointLng(d => d.lng)
    .pointColor(d => d.color)
    .pointAltitude(d => d.size * 0.01)
    .pointRadius(d => d.size)
    .pointResolution(16);

  const controls = world.controls();
  controls.autoRotate = true;
  controls.autoRotateSpeed = 10;

  console.log("✅ Globe initialized.");
}
        (function injectGlobeLibraryAndInit() {
            const script = document.createElement('script');
  script.src = "https://unpkg.com/globe.gl@2.42.0/dist/globe.gl.min.js";
  script.onload = () => {
    if (document.readyState === 'loading') {
        document.addEventListener("DOMContentLoaded", waitForGlobeContainer);
    } else {
        waitForGlobeContainer();
    }
};
  script.onerror = () => {
  console.error("❌ Failed to load Globe.gl script.");
};
  document.head.appendChild(script);
        })();
    }


if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeGlobe);
    } else {
        initializeGlobe();
    }
})();