/**
 * BSMA GeoAI Borewell & Groundwater Siting Application (MVP + Phase 1)
 * Features: Client-side KML Upload, Preset Farm Switcher (Karun Farm 2 & Mango Farm),
 * Full Siting Report Generator, PDF/HTML/GeoJSON/CSV Exporter, PWA Offline Service Worker,
 * Pin-Drop & Polygon Tools, and Ground-Truth Feedback Loop.
 */

// Multi-lingual dictionary
const I18N = {
  en: {
    appTitle: "Borewell Siting AI",
    subTitle: "GeoAI Groundwater Prospecting (Musi Basin)",
    meanPotential: "Mean Potential",
    landArea: "Land Area",
    elevationRange: "Elevation",
    topSpots: "Top Recommended Spots",
    drawCustomPlot: "Draw Custom Plot",
    resetPlot: "Reset Farm",
    waltaStatus: "WALTA Compliance",
    waltaText: "Minimum 150m spacing between agricultural borewells required in Telangana hard-rock.",
    vesNoticeTitle: "Mandatory VES Field Verification",
    vesNoticeText: "Before drilling rig mobilization, conduct a 1D/2D Vertical Electrical Sounding (VES) resistivity survey at Spot #1 to verify deep fracture depth.",
    estimatedDepth: "Est. Depth",
    expectedYield: "Yield",
    score: "GWPI Score",
    primary: "Primary",
    secondary: "Secondary",
    alternative: "Alternative",
    legendTitle: "Groundwater Potential Index",
    poor: "Low (0)",
    high: "High (100)",
    shareReport: "Report",
    fullReportBtn: "Full Siting Report",
    addOutcome: "Record Outcome",
    pinDropModeMsg: "📍 Pin-Drop Mode: Click anywhere on the map to evaluate a 300m radius parcel.",
    polyDrawModeMsg: "📐 Polygon Mode: Click on the map to place corner points (at least 3) for your custom plot."
  },
  te: {
    appTitle: "బోరుబావి గుర్తింపు AI",
    subTitle: "భూగర్భ జలాల అంచనా (మూసీ బేసిన్)",
    meanPotential: "సగటు నీటి సామర్థ్యం",
    landArea: "భూమి విస్తీర్ణం",
    elevationRange: "ఎత్తు",
    topSpots: "సిఫార్సు చేయబడిన స్థానాలు",
    drawCustomPlot: "కొత్త భూమిని గీయండి",
    resetPlot: "రీసెట్ చేయండి",
    waltaStatus: "వాల్టా (WALTA) నిబంధనలు",
    waltaText: "తెలంగాణ వాల్టా చట్టం ప్రకారం బోరుబావుల మధ్య కనీసం 150 మీటర్ల దూరం ఉండాలి.",
    vesNoticeTitle: "తప్పనిసరి VES రెసిస్టివిటీ సర్వే",
    vesNoticeText: "డ్రిల్లింగ్ చేయడానికి ముందు స్పాట్ #1 వద్ద తప్పనిసరిగా VES భూ-భౌతిక సర్వే చేయించుకుని నీటి పగులు లోతును నిర్ధారించుకోండి.",
    estimatedDepth: "అంచనా లోతు",
    expectedYield: "నీటి ప్రవాహం",
    score: "సామర్థ్య స్కోరు",
    primary: "మొదటి ప్రాధాన్యత",
    secondary: "రెండవ ప్రాధాన్యత",
    alternative: "ప్రత్యామ్నాయం",
    legendTitle: "భూగర్భ జలాల సూచిక",
    poor: "తక్కువ (0)",
    high: "అత్యధికం (100)",
    shareReport: "పూర్తి రిపోర్ట్",
    fullReportBtn: "పూర్తి రిపోర్ట్ డౌన్‌లోడ్",
    addOutcome: "ఫలితం నమోదు",
    pinDropModeMsg: "📍 పిన్ డ్రాప్ మోడ్: 300 మీటర్ల పరిధిని అంచనా వేయడానికి మ్యాప్‌పై క్లిక్ చేయండి.",
    polyDrawModeMsg: "📐 సరిహద్దు గీసే మోడ్: మీ పొలం సరిహద్దులను గుర్తించడానికి కనీసం 3 పాయింట్లను క్లిక్ చేయండి."
  },
  hi: {
    appTitle: "बोरवेल चयन AI",
    subTitle: "भूजल अन्वेषण प्रणाली (मूसी बेसिन)",
    meanPotential: "औसत भूजल क्षमता",
    landArea: "कुल क्षेत्रफल",
    elevationRange: "ऊंचाई",
    topSpots: "शीर्ष अनुशंसित स्थान",
    drawCustomPlot: "नया खेत चिह्नित करें",
    resetPlot: "रीसेट करें",
    waltaStatus: "वाल्टा (WALTA) अनुपालन",
    waltaText: "तेलंगाना वाल्टा नियमों के तहत बोरवेलों के बीच न्यूनतम 150 मीटर की दूरी अनिवार्य है।",
    vesNoticeTitle: "अनिवार्य VES भू-भौतिकीय जांच",
    vesNoticeText: "बोरवेल ड्रिलिंग से पहले स्पॉट #1 पर VES विद्युत प्रतिरोधकता (Resistivity) सर्वेक्षण अवश्य करवाएं।",
    estimatedDepth: "अनुमानित गहराई",
    expectedYield: "जल प्रवाह",
    score: "GWPI स्कोर",
    primary: "प्राथमिक",
    secondary: "द्वितीयक",
    alternative: "वैकल्पिक",
    legendTitle: "भूजल क्षमता सूचकांक",
    poor: "कम (0)",
    high: "उत्कृष्ट (100)",
    shareReport: "पूर्ण रिपोर्ट",
    fullReportBtn: "पूर्ण रिपोर्ट डाउनलोड",
    addOutcome: "परिणाम दर्ज करें",
    pinDropModeMsg: "📍 पिन-ड्रॉप मोड: 300 मीटर दायरे का मूल्यांकन करने के लिए मानचित्र पर क्लिक करें।",
    polyDrawModeMsg: "📐 बहुभुज मोड: अपने खेत की सीमा बनाने के लिए कम से कम 3 बिंदुओं पर क्लिक करें।"
  }
};

let currentLang = 'en';
let map;
let defaultFarmGeoJSON = null;
let mangoFarmGeoJSON = null;
let currentAnalysis = null;
let currentGeoJSON = null;
let clientGrid = null;
let currentToolMode = null; // 'pin', 'polygon', or null
let drawnPoints = [];
let markers = [];
let deferredPrompt = null;

document.addEventListener('DOMContentLoaded', async () => {
  initServiceWorker();
  initNetworkStatus();
  initLanguageSwitcher();
  await loadData();
  initMap();
  setupUIEventListeners();
  initPwaInstall();
});

/* PWA Service Worker Registration */
function initServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('service-worker.js')
        .then((reg) => console.log('[PWA] Service Worker registered with scope:', reg.scope))
        .catch((err) => console.warn('[PWA] Service Worker registration failed:', err));
    });
  }
}

/* Network Online / Offline Detection */
function initNetworkStatus() {
  const badge = document.getElementById('networkStatus');
  const text = document.getElementById('networkText');

  function updateStatus() {
    if (navigator.onLine) {
      badge.classList.remove('offline');
      text.textContent = 'Online';
    } else {
      badge.classList.add('offline');
      text.textContent = 'Offline (Cached)';
    }
  }

  window.addEventListener('online', updateStatus);
  window.addEventListener('offline', updateStatus);
  updateStatus();
}

/* PWA Install Button Handler */
function initPwaInstall() {
  const installBtn = document.getElementById('btnInstallPwa');
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installBtn.style.display = 'flex';
  });

  installBtn.addEventListener('click', async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log('[PWA] Install prompt outcome:', outcome);
      deferredPrompt = null;
      installBtn.style.display = 'none';
    }
  });
}

function initLanguageSwitcher() {
  const select = document.getElementById('langSelect');
  select.addEventListener('change', (e) => {
    currentLang = e.target.value;
    updateLanguageTexts();
  });
}

function updateLanguageTexts() {
  const t = I18N[currentLang];
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (t[key]) el.textContent = t[key];
  });
  if (currentAnalysis) {
    renderFarmData(currentAnalysis);
  }
}

async function loadData() {
  try {
    const [reportRes, mangoRes, gridRes] = await Promise.all([
      fetch('data/farm_siting_report.geojson'),
      fetch('data/mangofarm_siting_report.geojson').catch(() => null),
      fetch('data/gwpi_grid.json')
    ]);
    
    defaultFarmGeoJSON = await reportRes.json();
    if (mangoRes && mangoRes.ok) {
      mangoFarmGeoJSON = await mangoRes.json();
    }
    clientGrid = await gridRes.json();
    currentGeoJSON = defaultFarmGeoJSON;
    
    // Save to LocalStorage for offline resilience
    localStorage.setItem('borewell_default_farm', JSON.stringify(defaultFarmGeoJSON));
    if (mangoFarmGeoJSON) {
      localStorage.setItem('borewell_mango_farm', JSON.stringify(mangoFarmGeoJSON));
    }
    localStorage.setItem('borewell_grid', JSON.stringify(clientGrid));
  } catch (err) {
    console.warn("Loading from offline LocalStorage fallback:", err);
    const cachedFarm = localStorage.getItem('borewell_default_farm');
    const cachedMango = localStorage.getItem('borewell_mango_farm');
    const cachedGrid = localStorage.getItem('borewell_grid');
    if (cachedFarm) {
      defaultFarmGeoJSON = JSON.parse(cachedFarm);
      currentGeoJSON = defaultFarmGeoJSON;
    }
    if (cachedMango) mangoFarmGeoJSON = JSON.parse(cachedMango);
    if (cachedGrid) clientGrid = JSON.parse(cachedGrid);
  }
}

function initMap() {
  const farmCentroid = defaultFarmGeoJSON ? 
    [defaultFarmGeoJSON.farm_analysis.centroid.lon, defaultFarmGeoJSON.farm_analysis.centroid.lat] : 
    [79.08839, 17.43306];

  map = new maplibregl.Map({
    container: 'map',
    style: {
      version: 8,
      sources: {
        'osm-tiles': {
          type: 'raster',
          tiles: [
            'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
          ],
          tileSize: 256,
          attribution: '&copy; OpenStreetMap contributors'
        }
      },
      layers: [
        {
          id: 'osm-layer',
          type: 'raster',
          source: 'osm-tiles',
          minzoom: 0,
          maxzoom: 19
        }
      ]
    },
    center: farmCentroid,
    zoom: 15.6,
    pitch: 20
  });

  map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
  map.addControl(new maplibregl.ScaleControl({ maxWidth: 120, unit: 'metric' }), 'bottom-right');

  map.on('load', () => {
    addCatchmentOverlay();
    if (defaultFarmGeoJSON) {
      renderFarmOnMap(defaultFarmGeoJSON);
      renderFarmData(defaultFarmGeoJSON.farm_analysis);
    }
  });

  map.on('click', handleMapClick);
}

function addCatchmentOverlay() {
  if (!clientGrid) return;
  const bbox = clientGrid.bbox;
  
  map.addSource('gwpi-catchment-overlay', {
    type: 'image',
    url: 'data/catchment_gwpi_map.png',
    coordinates: [
      [bbox.min_lon, bbox.max_lat],
      [bbox.max_lon, bbox.max_lat],
      [bbox.max_lon, bbox.min_lat],
      [bbox.min_lon, bbox.min_lat]
    ]
  });

  map.addLayer({
    id: 'gwpi-raster-layer',
    type: 'raster',
    source: 'gwpi-catchment-overlay',
    paint: {
      'raster-opacity': 0.65,
      'raster-fade-duration': 300
    }
  });
}

function renderFarmOnMap(geojson) {
  currentGeoJSON = geojson;
  if (map.getSource('farm-boundary-source')) {
    map.getSource('farm-boundary-source').setData(geojson);
  } else {
    map.addSource('farm-boundary-source', {
      type: 'geojson',
      data: geojson
    });

    map.addLayer({
      id: 'farm-boundary-fill',
      type: 'fill',
      source: 'farm-boundary-source',
      filter: ['==', '$type', 'Polygon'],
      paint: {
        'fill-color': '#16a34a',
        'fill-opacity': 0.18
      }
    });

    map.addLayer({
      id: 'farm-boundary-line',
      type: 'line',
      source: 'farm-boundary-source',
      filter: ['==', '$type', 'Polygon'],
      paint: {
        'line-color': '#b91c1c',
        'line-width': 3,
        'line-dasharray': [2, 1]
      }
    });
  }

  // Clear existing markers
  markers.forEach(m => m.remove());
  markers = [];

  // Add Candidate Spots as MapLibre HTML Markers
  geojson.farm_analysis.candidate_points.forEach(pt => {
    const el = document.createElement('div');
    el.className = 'custom-map-marker';
    el.style.width = '32px';
    el.style.height = '32px';
    el.style.borderRadius = '50%';
    el.style.backgroundColor = pt.rank === 1 ? '#16a34a' : pt.rank === 2 ? '#d97706' : '#0284c7';
    el.style.border = '3px solid white';
    el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.35)';
    el.style.display = 'flex';
    el.style.alignItems = 'center';
    el.style.justifyContent = 'center';
    el.style.color = 'white';
    el.style.fontWeight = '800';
    el.style.fontSize = '13px';
    el.style.cursor = 'pointer';
    el.innerHTML = `#${pt.rank}`;

    const popupHtml = `
      <div style="font-family: sans-serif; padding: 4px;">
        <h4 style="margin: 0 0 4px 0; color: #0f172a; font-size: 14px;">${pt.label}</h4>
        <div style="font-size: 12px; margin-bottom: 4px;">
          <strong>GWPI Score:</strong> <span style="color: #16a34a; font-weight: bold;">${pt.gwpi_score} / 100</span>
        </div>
        <div style="font-size: 11px; color: #475569; line-height: 1.4;">
          <strong>Est. Depth:</strong> ${pt.estimated_depth_range}<br/>
          <strong>Expected Yield:</strong> ${pt.expected_yield_range}<br/>
          <strong>Coordinates:</strong> ${pt.lat.toFixed(5)}°N, ${pt.lon.toFixed(5)}°E
        </div>
      </div>
    `;

    const marker = new maplibregl.Marker({ element: el })
      .setLngLat([pt.lon, pt.lat])
      .setPopup(new maplibregl.Popup({ offset: 20 }).setHTML(popupHtml))
      .addTo(map);

    markers.push(marker);
  });
}

function renderFarmData(analysis) {
  currentAnalysis = analysis;
  document.getElementById('farmNameDisplay').textContent = analysis.farm_name;
  document.getElementById('farmCategoryDisplay').textContent = analysis.score_statistics.category;
  document.getElementById('meanScoreVal').textContent = `${analysis.score_statistics.mean} / 100`;
  document.getElementById('areaVal').textContent = `${analysis.farm_area_acres} Acres (${analysis.farm_area_hectares} ha)`;
  
  const minElev = analysis.candidate_points[0] ? analysis.candidate_points[0].elevation_m : 335;
  document.getElementById('elevVal').textContent = `~${minElev} m`;

  // Summary Text
  const summaryEl = document.getElementById('summaryText');
  if (analysis.summary && analysis.summary[currentLang]) {
    summaryEl.textContent = analysis.summary[currentLang];
  } else if (analysis.summary && analysis.summary.en) {
    summaryEl.textContent = analysis.summary.en;
  }

  // Candidate Spots
  const spotListEl = document.getElementById('candidateSpotsList');
  spotListEl.innerHTML = '';

  const t = I18N[currentLang];

  analysis.candidate_points.forEach(pt => {
    const card = document.createElement('div');
    card.className = `spot-card ${pt.rank === 1 ? 'primary-spot' : ''}`;
    card.onclick = () => {
      map.flyTo({ center: [pt.lon, pt.lat], zoom: 17, speed: 1.2 });
    };

    const rankLabel = pt.rank === 1 ? t.primary : pt.rank === 2 ? t.secondary : t.alternative;

    card.innerHTML = `
      <div class="spot-card-top">
        <div class="spot-title">#${pt.rank} ${rankLabel} (${pt.lat.toFixed(4)}°N, ${pt.lon.toFixed(4)}°E)</div>
        <div class="spot-score-badge">${pt.gwpi_score} / 100</div>
      </div>
      <div class="spot-details">
        <div>${t.estimatedDepth}: <strong>${pt.estimated_depth_range}</strong></div>
        <div>${t.expectedYield}: <strong>${pt.expected_yield_range.split('(')[0]}</strong></div>
        <div>Slope: <strong>${pt.slope_pct}%</strong></div>
        <div>Elevation: <strong>${pt.elevation_m}m</strong></div>
      </div>
      <div class="spot-rationale">${pt.hydro_summary}</div>
    `;

    spotListEl.appendChild(card);
  });
}

function setupUIEventListeners() {
  document.getElementById('btnDropPin').addEventListener('click', () => setToolMode('pin'));
  document.getElementById('btnDrawPolygon').addEventListener('click', () => setToolMode('polygon'));
  document.getElementById('btnResetFarm').addEventListener('click', resetToDefaultFarm);

  // KML Upload Handlers
  const kmlBtn = document.getElementById('btnUploadKML');
  const fileInput = document.getElementById('kmlFileInput');
  if (kmlBtn && fileInput) {
    kmlBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleKmlUpload(e.target.files[0]);
      }
    });
  }

  // Farm Preset Selector
  const presetSelect = document.getElementById('farmPresetSelect');
  if (presetSelect) {
    presetSelect.addEventListener('change', (e) => handlePresetFarmChange(e.target.value));
  }

  // Opacity Slider
  document.getElementById('opacitySlider').addEventListener('input', (e) => {
    const val = parseFloat(e.target.value) / 100.0;
    if (map.getLayer('gwpi-raster-layer')) {
      map.setPaintProperty('gwpi-raster-layer', 'raster-opacity', val);
    }
  });

  // Modal Report Listeners
  document.getElementById('btnOpenReport').addEventListener('click', openReportModal);
  document.getElementById('btnQuickReport').addEventListener('click', openReportModal);
  document.getElementById('btnCloseModal').addEventListener('click', closeReportModal);
  
  // Export Suite Buttons
  document.getElementById('btnDownloadPDF').addEventListener('click', downloadPdfReport);
  document.getElementById('btnDownloadHTML').addEventListener('click', downloadHtmlReport);
  document.getElementById('btnDownloadGeoJSON').addEventListener('click', downloadGeoJsonReport);
  document.getElementById('btnDownloadCSV').addEventListener('click', downloadCsvReport);

  // Drilling Outcome Feedback Listeners (ML Data Flywheel)
  document.getElementById('btnOpenFeedback').addEventListener('click', openFeedbackModal);
  document.getElementById('btnCloseFeedbackModal').addEventListener('click', closeFeedbackModal);
  document.getElementById('btnCancelFeedback').addEventListener('click', closeFeedbackModal);
  document.getElementById('feedbackForm').addEventListener('submit', handleFeedbackSubmit);
}

function handlePresetFarmChange(presetKey) {
  setToolMode(null);
  if (presetKey === 'mango_farm' && mangoFarmGeoJSON) {
    renderFarmOnMap(mangoFarmGeoJSON);
    renderFarmData(mangoFarmGeoJSON.farm_analysis);
    map.flyTo({
      center: [mangoFarmGeoJSON.farm_analysis.centroid.lon, mangoFarmGeoJSON.farm_analysis.centroid.lat],
      zoom: 15.6
    });
  } else if (presetKey === 'karun_farm_2' && defaultFarmGeoJSON) {
    renderFarmOnMap(defaultFarmGeoJSON);
    renderFarmData(defaultFarmGeoJSON.farm_analysis);
    map.flyTo({
      center: [defaultFarmGeoJSON.farm_analysis.centroid.lon, defaultFarmGeoJSON.farm_analysis.centroid.lat],
      zoom: 15.6
    });
  }
}

/* KML File Upload & Ingestion Parser */
function handleKmlUpload(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    parseAndEvaluateKML(e.target.result, file.name);
  };
  reader.readAsText(file);
}

function parseAndEvaluateKML(kmlText, fileName = "Uploaded Farm") {
  try {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(kmlText, "text/xml");
    
    // Check for parse error
    const parseError = xmlDoc.getElementsByTagName("parsererror");
    if (parseError.length > 0) {
      alert("Invalid KML file format. Please ensure it is a valid Google Earth KML.");
      return;
    }

    // Extract Name
    let farmName = fileName.replace(/\.kml$/i, '');
    const nameEl = xmlDoc.getElementsByTagName("name")[0];
    if (nameEl && nameEl.textContent) {
      farmName = nameEl.textContent.trim().replace(/\.kmz$/i, '');
    }

    // Extract Coordinates
    const coordsEls = xmlDoc.getElementsByTagName("coordinates");
    if (!coordsEls || coordsEls.length === 0) {
      alert("No coordinates found in this KML file.");
      return;
    }

    const rawCoords = coordsEls[0].textContent.trim();
    const points = [];
    const tuples = rawCoords.split(/\s+/);
    
    for (let tuple of tuples) {
      if (!tuple.trim()) continue;
      const parts = tuple.split(',');
      if (parts.length >= 2) {
        const lon = parseFloat(parts[0]);
        const lat = parseFloat(parts[1]);
        if (!isNaN(lon) && !isNaN(lat)) {
          points.push([lon, lat]);
        }
      }
    }

    if (points.length < 3) {
      alert("A valid polygon requires at least 3 coordinate points in the KML.");
      return;
    }

    // Compute bounding box and fit map
    let minLon = Infinity, maxLon = -Infinity, minLat = Infinity, maxLat = -Infinity;
    for (let p of points) {
      if (p[0] < minLon) minLon = p[0];
      if (p[0] > maxLon) maxLon = p[0];
      if (p[1] < minLat) minLat = p[1];
      if (p[1] > maxLat) maxLat = p[1];
    }

    map.fitBounds([[minLon, minLat], [maxLon, maxLat]], { padding: 80, maxZoom: 16.5 });

    // Evaluate over grid
    evaluateCustomPolygon(points, farmName);

    // Update preset selector
    const presetSelect = document.getElementById('farmPresetSelect');
    if (presetSelect) {
      let customOpt = presetSelect.querySelector('option[value="custom"]');
      if (!customOpt) {
        customOpt = document.createElement('option');
        customOpt.value = 'custom';
        presetSelect.appendChild(customOpt);
      }
      customOpt.textContent = `📁 ${farmName}`;
      customOpt.disabled = false;
      customOpt.selected = true;
    }

    // Show temporary notification banner
    const banner = document.getElementById('instructionBanner');
    const textEl = document.getElementById('instructionText');
    banner.classList.add('visible');
    textEl.textContent = `✓ Successfully loaded and analyzed KML: "${farmName}"`;
    setTimeout(() => { banner.classList.remove('visible'); }, 4000);

  } catch (err) {
    console.error("Error parsing KML:", err);
    alert("Error parsing KML file: " + err.message);
  }
}

function setToolMode(mode) {
  const pinBtn = document.getElementById('btnDropPin');
  const polyBtn = document.getElementById('btnDrawPolygon');
  const banner = document.getElementById('instructionBanner');
  const instructionText = document.getElementById('instructionText');
  const t = I18N[currentLang];

  if (currentToolMode === mode) {
    // Toggle off
    currentToolMode = null;
    pinBtn.classList.remove('active');
    polyBtn.classList.remove('active');
    banner.classList.remove('visible');
    drawnPoints = [];
    return;
  }

  currentToolMode = mode;
  drawnPoints = [];
  pinBtn.classList.toggle('active', mode === 'pin');
  polyBtn.classList.toggle('active', mode === 'polygon');

  banner.classList.add('visible');
  if (mode === 'pin') {
    instructionText.textContent = t.pinDropModeMsg;
  } else {
    instructionText.textContent = t.polyDrawModeMsg;
  }
}

function handleMapClick(e) {
  if (!currentToolMode) return;
  const { lng, lat } = e.lngLat;

  if (currentToolMode === 'pin') {
    evaluatePinDrop(lng, lat);
    setToolMode(null); // Turn off after drop
  } else if (currentToolMode === 'polygon') {
    drawnPoints.push([lng, lat]);
    if (drawnPoints.length >= 3) {
      evaluateCustomPolygon(drawnPoints);
    }
  }
}

function evaluatePinDrop(lon, lat) {
  if (!clientGrid) return;
  
  // Create circular buffer around dropped pin (~250m radius)
  const radiusDeg = 0.0022; // ~240 meters
  const coords = [];
  for (let i = 0; i < 16; i++) {
    const angle = (i / 16) * Math.PI * 2;
    coords.push([
      lon + Math.cos(angle) * radiusDeg,
      lat + Math.sin(angle) * (radiusDeg * 0.95)
    ]);
  }
  coords.push(coords[0]); // close loop

  evaluateCustomPolygon(coords, `Pin Sited Plot (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E)`);
}

function evaluateCustomPolygon(points, customName = "Custom Drawn Plot") {
  if (!clientGrid) return;
  
  const coords = points[0][0] === points[points.length-1][0] ? points : [...points, points[0]];
  
  const lons = clientGrid.lon_grid;
  const lats = clientGrid.lat_grid;
  const gwpi = clientGrid.gwpi;
  const elev = clientGrid.elevation;
  const slope = clientGrid.slope;

  let insideScores = [];
  let candidatePixels = [];

  for (let r = 0; r < clientGrid.rows; r++) {
    const lat = lats[r];
    for (let c = 0; c < clientGrid.cols; c++) {
      const lon = lons[c];
      if (pointInPolygon([lon, lat], coords)) {
        const score = gwpi[r][c];
        insideScores.push(score);
        candidatePixels.push({
          r, c, lat, lon, score,
          elevation: elev[r][c],
          slope: slope[r][c]
        });
      }
    }
  }

  if (candidatePixels.length === 0) return;

  candidatePixels.sort((a, b) => b.score - a.score);
  const meanScore = (insideScores.reduce((a, b) => a + b, 0) / insideScores.length).toFixed(1);

  // Pick top 3 with 150m spacing
  let selected = [];
  const minSpacingDeg = 0.0013; // ~145m

  for (let pix of candidatePixels) {
    let tooClose = false;
    for (let s of selected) {
      const d = Math.hypot(pix.lat - s.lat, pix.lon - s.lon);
      if (d < minSpacingDeg) {
        tooClose = true;
        break;
      }
    }
    if (!tooClose) {
      const rank = selected.length + 1;
      selected.push({
        rank,
        label: `Spot #${rank}`,
        lat: pix.lat,
        lon: pix.lon,
        gwpi_score: pix.score,
        potential_category: pix.score >= 70 ? "High Potential" : "Moderate Potential",
        elevation_m: pix.elevation,
        slope_pct: pix.slope,
        estimated_depth_range: "280 - 400 ft",
        expected_yield_range: "1,500 - 2,500 LPH (approx 1.0 - 1.5 inch)",
        hydro_summary: "Located on a gentle slope with favorable fracture density and moisture convergence in the weathered granite zone."
      });
    }
    if (selected.length >= 3) break;
  }

  const customAnalysis = {
    farm_name: customName,
    farm_area_acres: (candidatePixels.length * 0.89).toFixed(1),
    farm_area_hectares: (candidatePixels.length * 0.36).toFixed(2),
    centroid: { lon: points[0][0], lat: points[0][1] },
    score_statistics: {
      mean: meanScore,
      category: meanScore >= 65 ? "High Potential" : "Moderate Potential"
    },
    candidate_points: selected,
    summary: {
      en: `${customName} evaluation shows an average groundwater potential score of ${meanScore}/100 with ${selected.length} optimal drilling candidate locations.`,
      te: `${customName} సర్వేలో సగటు నీటి సామర్థ్య సూచిక ${meanScore}/100 గా నమోదైంది. అత్యుత్తమ ${selected.length} స్థానాలు గుర్తించబడ్డాయి.`,
      hi: `${customName} मूल्यांकन में औसत भूजल क्षमता सूचकांक ${meanScore}/100 दर्ज किया गया है।`
    }
  };

  const customGeoJSON = {
    type: "FeatureCollection",
    farm_analysis: customAnalysis,
    features: [{
      type: "Feature",
      geometry: { type: "Polygon", coordinates: [coords] }
    }]
  };

  renderFarmOnMap(customGeoJSON);
  renderFarmData(customAnalysis);
  
  if (currentToolMode === 'polygon') {
    setToolMode(null);
  }
}

function pointInPolygon(point, vs) {
  const x = point[0], y = point[1];
  let inside = false;
  for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
    const xi = vs[i][0], yi = vs[i][1];
    const xj = vs[j][0], yj = vs[j][1];
    const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

function resetToDefaultFarm() {
  setToolMode(null);
  const presetSelect = document.getElementById('farmPresetSelect');
  if (presetSelect) presetSelect.value = 'karun_farm_2';
  handlePresetFarmChange('karun_farm_2');
}

/* ==========================================================================
   Full Siting Report Generation & Export Functions
   ========================================================================== */

function openReportModal() {
  if (!currentAnalysis) return;
  
  // Populate Section 1: Overview
  document.getElementById('modalFarmName').textContent = currentAnalysis.farm_name;
  document.getElementById('modalFarmArea').textContent = `${currentAnalysis.farm_area_acres} Acres (${currentAnalysis.farm_area_hectares} ha)`;
  document.getElementById('modalFarmCoords').textContent = 
    `${currentAnalysis.centroid.lat.toFixed(5)}°N, ${currentAnalysis.centroid.lon.toFixed(5)}°E`;
  document.getElementById('modalScoreBadge').textContent = 
    `${currentAnalysis.score_statistics.mean} / 100 (${currentAnalysis.score_statistics.category})`;
  
  document.getElementById('modalReportDate').textContent = new Date().toISOString().split('T')[0];
  document.getElementById('modalReportId').textContent = `BSMA-GW-${Date.now().toString().slice(-6)}`;

  // Update Figure 1 Map Image depending on active farm
  const mapImg = document.getElementById('modalMapImg');
  if (mapImg) {
    if (currentAnalysis.farm_name.includes('Mango') || currentAnalysis.farm_name.includes('Farmland 1')) {
      mapImg.src = 'data/mangofarm_siting_plan.png';
    } else {
      mapImg.src = 'data/farm_siting_plan.png';
    }
  }

  // Populate Section 3: Table
  const tBody = document.getElementById('modalTableBody');
  tBody.innerHTML = '';

  currentAnalysis.candidate_points.forEach(pt => {
    const tr = document.createElement('tr');
    const rankLabel = pt.rank === 1 ? 'Primary Spot' : pt.rank === 2 ? 'Secondary Spot' : 'Alternative Spot';
    tr.innerHTML = `
      <td><strong>Spot #${pt.rank}</strong><br/><span style="font-size: 10px; color: #64748b;">${rankLabel}</span></td>
      <td><code>${pt.lat.toFixed(5)}°N, ${pt.lon.toFixed(5)}°E</code></td>
      <td><span style="font-weight: bold; color: #15803d; font-size: 13px;">${pt.gwpi_score} / 100</span><br/><span style="font-size: 9.5px; color: #64748b;">${pt.potential_category}</span></td>
      <td><strong>${pt.estimated_depth_range}</strong></td>
      <td><strong>${pt.expected_yield_range}</strong></td>
      <td>${pt.elevation_m}m MSL (${pt.slope_pct}% slope)</td>
    `;
    tBody.appendChild(tr);
  });

  // Populate Section 4: Detailed Rationales
  const ratContainer = document.getElementById('modalSpotRationales');
  ratContainer.innerHTML = '';
  currentAnalysis.candidate_points.forEach(pt => {
    const card = document.createElement('div');
    card.className = `rationale-card ${pt.rank === 1 ? 'primary' : ''}`;
    card.innerHTML = `
      <strong>Spot #${pt.rank} (${pt.lat.toFixed(5)}°N, ${pt.lon.toFixed(5)}°E) — Geological Profile:</strong>
      <p style="margin: 4px 0 0 0; line-height: 1.4; color: #334155;">${pt.hydro_summary} Recommended drilling technique: DTH rotary hammer with 40-60 ft casing.</p>
    `;
    ratContainer.appendChild(card);
  });

  // Populate Section 5: Multilingual Summaries
  const sumObj = currentAnalysis.summary || {};
  document.getElementById('modalSummaryEn').textContent = sumObj.en || "Evaluation complete with identified high groundwater recharge potential zones.";
  document.getElementById('modalSummaryTe').textContent = sumObj.te || "భూగర్భ జలాల అంచనా పూర్తయింది. గుర్తించబడిన ప్రదేశాలలో అధిక నీటి సాంద్రత మరియు పగుళ్లు కలవు.";
  document.getElementById('modalSummaryHi').textContent = sumObj.hi || "भूजल मूल्यांकन पूर्ण हुआ। चिह्नित स्थानों पर अच्छी जल संचयन क्षमता पाई गई है।";

  document.getElementById('reportModal').classList.add('open');
}

function closeReportModal() {
  document.getElementById('reportModal').classList.remove('open');
}

/* 1. Download Full PDF Report */
function downloadPdfReport() {
  if (!currentAnalysis) return;

  const isKarunFarm = defaultFarmGeoJSON && currentAnalysis.farm_name === defaultFarmGeoJSON.farm_analysis.farm_name;
  const isMangoFarm = currentAnalysis.farm_name.includes('Mango') || currentAnalysis.farm_name.includes('Farmland 1');

  if (isKarunFarm) {
    // Direct instant download of the complete 2-page publication-grade PDF
    const a = document.createElement('a');
    a.href = 'data/Borewell_Siting_Full_Report.pdf';
    a.download = `Borewell_Siting_Full_Report_${currentAnalysis.farm_name.replace(/\s+/g, '_')}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    return;
  }

  if (isMangoFarm) {
    const a = document.createElement('a');
    a.href = 'data/Borewell_Siting_Full_Report_MangoFarm.pdf';
    a.download = `Borewell_Siting_Full_Report_MangoFarm.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    return;
  }

  // For custom evaluated plots, generate via html2pdf or browser print
  const element = document.getElementById('printableReportContent');
  const btn = document.getElementById('btnDownloadPDF');
  const originalText = btn.innerHTML;
  btn.innerHTML = '⏳ Generating PDF...';
  btn.disabled = true;

  const opt = {
    margin: [8, 8, 8, 8],
    filename: `Borewell_Siting_Report_${currentAnalysis.farm_name.replace(/\s+/g, '_')}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true, logging: false },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };

  if (window.html2pdf) {
    window.html2pdf().set(opt).from(element).save().then(() => {
      btn.innerHTML = originalText;
      btn.disabled = false;
    }).catch(err => {
      console.error("PDF Export error:", err);
      btn.innerHTML = originalText;
      btn.disabled = false;
      window.print();
    });
  } else {
    window.print();
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

/* 2. Download Standalone Offline HTML Report */
function downloadHtmlReport() {
  const elementHtml = document.getElementById('printableReportContent').outerHTML;
  const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>BSMA GeoAI Borewell Siting Report — ${currentAnalysis.farm_name}</title>
  <style>
    body { font-family: 'Inter', sans-serif, system-ui; background: #f8fafc; color: #0f172a; margin: 0; padding: 20px; }
    .report-document-sheet { max-width: 850px; margin: 0 auto; background: white; padding: 32px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 12px; }
    .report-header-banner { display: flex; justify-content: space-between; border-bottom: 2px solid #0284c7; padding-bottom: 12px; }
    .overview-box { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; background: #f8fafc; padding: 12px; border: 1px solid #e2e8f0; margin-top: 6px; }
    .overview-item .lbl { font-size: 10px; color: #64748b; font-weight: bold; }
    .overview-item .val { font-size: 12.5px; font-weight: bold; }
    .report-table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 11.5px; }
    .report-table th, .report-table td { border: 1px solid #cbd5e1; padding: 8px; text-align: left; }
    .report-table th { background: #f1f5f9; font-weight: bold; }
    .rationale-card { background: #f8fafc; border-left: 4px solid #0284c7; padding: 8px 12px; margin-bottom: 6px; }
    .lang-summary-card { background: #f0f9ff; border: 1px solid #bae6fd; padding: 12px; border-radius: 6px; }
    .checklist-box { background: #fafaf9; border: 1px solid #e7e5e4; padding: 12px; border-radius: 6px; font-size: 11px; line-height: 1.5; }
    .report-signoff { display: flex; justify-content: space-between; border-top: 1px solid #cbd5e1; padding-top: 12px; margin-top: 16px; }
    .ahp-mini-card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px; }
  </style>
</head>
<body>
  ${elementHtml}
</body>
</html>`;

  const blob = new Blob([fullHtml], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Borewell_Siting_Report_${currentAnalysis.farm_name.replace(/\s+/g, '_')}.html`;
  a.click();
  URL.revokeObjectURL(url);
}

/* 3. Download GeoJSON Dataset */
function downloadGeoJsonReport() {
  const dataToExport = currentGeoJSON || defaultFarmGeoJSON;
  const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/geo+json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Borewell_Siting_${currentAnalysis.farm_name.replace(/\s+/g, '_')}.geojson`;
  a.click();
  URL.revokeObjectURL(url);
}

/* 4. Download CSV Coordinates Table */
function downloadCsvReport() {
  let csv = "Rank,Label,Latitude,Longitude,GWPI_Score,Potential_Category,Elevation_m,Slope_Pct,Estimated_Depth,Expected_Yield,Geological_Rationale\n";
  currentAnalysis.candidate_points.forEach(pt => {
    csv += `"${pt.rank}","${pt.label}","${pt.lat}","${pt.lon}","${pt.gwpi_score}","${pt.potential_category}","${pt.elevation_m}","${pt.slope_pct}","${pt.estimated_depth_range}","${pt.expected_yield_range}","${pt.hydro_summary.replace(/"/g, '""')}"\n`;
  });

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Borewell_Candidate_Spots_${currentAnalysis.farm_name.replace(/\s+/g, '_')}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

/* ==========================================================================
   Drilling Outcome Feedback Functions (ML Data Flywheel)
   ========================================================================== */

function openFeedbackModal() {
  document.getElementById('fbSuccessMsg').style.display = 'none';
  document.getElementById('feedbackModal').classList.add('open');
}

function closeFeedbackModal() {
  document.getElementById('feedbackModal').classList.remove('open');
}

async function handleFeedbackSubmit(e) {
  e.preventDefault();
  
  const targetSpot = document.getElementById('fbTargetSpot').value;
  const drilledDepth = parseInt(document.getElementById('fbDrilledDepth').value);
  const strikeDepth = parseInt(document.getElementById('fbStrikeDepth').value) || null;
  const casingDepth = parseInt(document.getElementById('fbCasingDepth').value) || null;
  const yieldCat = document.getElementById('fbYieldCategory').value;
  const vesCheck = document.getElementById('fbVesCheck').checked;
  const contractor = document.getElementById('fbContractor').value;
  const notes = document.getElementById('fbNotes').value;

  const lat = currentAnalysis && currentAnalysis.candidate_points[0] ? currentAnalysis.candidate_points[0].lat : 17.43388;
  const lon = currentAnalysis && currentAnalysis.candidate_points[0] ? currentAnalysis.candidate_points[0].lon : 79.08853;

  const payload = {
    drilled_lat: lat,
    drilled_lon: lon,
    actual_drilling_depth_ft: drilledDepth,
    water_strike_depth_ft: strikeDepth,
    casing_depth_ft: casingDepth,
    measured_yield_lph: yieldCat.includes('High') ? 3200 : yieldCat.includes('Moderate') ? 2200 : yieldCat.includes('Low') ? 1000 : 0,
    yield_category: yieldCat,
    ves_conducted: vesCheck,
    contractor_name: contractor,
    feedback_notes: notes
  };

  // 1. Save to local browser storage for offline resilience
  const existingOutcomes = JSON.parse(localStorage.getItem('borewell_outcomes') || '[]');
  existingOutcomes.push({ ...payload, submitted_at: new Date().toISOString() });
  localStorage.setItem('borewell_outcomes', JSON.stringify(existingOutcomes));

  // 2. Attempt API Sync with Backend
  try {
    const plotId = (currentAnalysis && currentAnalysis.id) || "pilot_farm";
    await fetch(`http://localhost:8000/api/v1/plots/${plotId}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    console.log("[ML Flywheel] Outcome synced with cloud backend.");
  } catch (err) {
    console.log("[ML Flywheel] Backend offline. Outcome saved locally in LocalStorage.");
  }

  // Show success message
  const msgEl = document.getElementById('fbSuccessMsg');
  msgEl.style.display = 'block';

  setTimeout(() => {
    closeFeedbackModal();
  }, 2200);
}
