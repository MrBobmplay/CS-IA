<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Fishing Weather App - Redesigned</title>

  <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"/>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap"/>
  <link href="https://api.mapbox.com/mapbox-gl-js/v2.12.0/mapbox-gl.css" rel="stylesheet"/>

  <style>
    :root{--dark:#1A535C;--medium:#4ECDC4;--light:#F7FFF7;--text:#333;--muted:#555;}
    *{margin:0;padding:0;box-sizing:border-box;font-family:'Quicksand',sans-serif;}
    body{background:var(--light);color:var(--text);display:flex;flex-direction:column;min-height:100vh;}
    header{background:var(--dark);color:#fff;padding:1rem;text-align:center;position:relative;}
    .app-title{font-size:1.8rem;font-weight:600;display:inline-flex;align-items:center;gap:0.4rem;}
    .app-subtitle{font-size:1rem;opacity:0.9;margin-top:0.3rem;}
    .container{width:90%;max-width:1200px;margin:1rem auto;flex:1;display:flex;flex-direction:column;gap:1rem;}
    .search-area{display:grid;grid-template-columns:1fr auto;gap:0.5rem;align-items:center;}
    .search-box{display:flex;}
    .search-box input{flex:1;padding:0.5rem;border:1px solid var(--medium);border-radius:4px 0 0 4px;outline:none;}
    .search-box button{background:var(--medium);color:#fff;border:none;padding:0.6rem 1rem;border-radius:0 4px 4px 0;cursor:pointer;display:inline-flex;align-items:center;gap:0.3rem;transition:background 0.2s;}
    .search-box button:hover,.refresh-btn:hover{background:var(--dark);}
    .refresh-btn{background:var(--medium);color:#fff;border:none;padding:0.6rem 1rem;border-radius:4px;cursor:pointer;display:inline-flex;align-items:center;gap:0.3rem;transition:background 0.2s;}
    .refresh-btn:disabled{opacity:0.5;cursor:not-allowed;}
    .location-display{display:flex;align-items:center;gap:0.3rem;font-size:1.1rem;font-weight:500;color:var(--muted);margin-left:0.2rem;}
    .main-content{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;flex-wrap:wrap;}
    #map{flex:1 1 0;min-width:480px;height:400px;border-radius:8px;overflow:hidden;}
    .weather-cards{display:grid;grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(3,1fr);gap:1rem;height:400px;flex:1 1 0;min-width:320px;}
    .card{background:var(--light);border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,0.1);padding:1rem;display:flex;flex-direction:column;justify-content:center;}
    .card-header{display:flex;align-items:center;gap:0.3rem;color:var(--medium);font-weight:600;margin-bottom:0.5rem;font-size:1.3rem;}
    .card p{margin:0;line-height:1.4;font-size:1.3rem;}
    .extra-sections{display:flex;flex-direction:column;gap:1rem;}
    .extra-section{background:var(--light);border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,0.1);padding:1rem;}
    .extra-section h3{color:var(--medium);margin-bottom:0.5rem;}
    footer{background:var(--dark);color:#fff;text-align:center;padding:0.5rem;}
    .forecast-controls{display:flex;align-items:center;gap:1rem;margin:0.5rem 0;}
    .forecast-select{padding:0.5rem;border:1px solid var(--medium);border-radius:4px;background:#fff;color:var(--text);cursor:pointer;outline:none;}
    .forecast-select:hover{border-color:var(--dark);}
    .auth-container{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);display:flex;justify-content:center;align-items:center;z-index:1000;}
    .auth-form{background:var(--light);padding:2rem;border-radius:8px;width:90%;max-width:400px;}
    .auth-form input{width:100%;padding:0.5rem;margin:0.5rem 0;border:1px solid var(--medium);border-radius:4px;}
    .auth-form button{width:100%;padding:0.5rem;margin:0.5rem 0;background:var(--medium);color:#fff;border:none;border-radius:4px;cursor:pointer;}
    .auth-form button:hover{background:var(--dark);}
    .logout-btn{position:absolute;right:1rem;top:50%;transform:translateY(-50%);background:var(--medium);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;display:inline-flex;align-items:center;gap:0.3rem;transition:background 0.2s;}
    .logout-btn:hover{background:var(--dark);outline:1px solid var(--medium);}
    .fish-log-form{display:flex;flex-direction:column;gap:0.5rem;padding:0.5rem;}
    .fish-input{padding:0.5rem;border:1px solid var(--medium);border-radius:4px;}
    .fish-log-btn{background:var(--medium);color:#fff;border:none;padding:0.5rem;border-radius:4px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:0.3rem;}
    .fish-log-btn:disabled{opacity:0.5;cursor:not-allowed;}
    .fish-log-btn:not(:disabled):hover{background:var(--dark);}
    #clickMapMsg{color:var(--muted);font-size:0.9rem;text-align:center;margin-top:0.5rem;}
  </style>
</head>
<body>

  <header>
    <div class="app-title"><span class="material-icons">phishing</span>Fishing Weather App</div>
    <div class="app-subtitle">Plan your fishing trips with real-time weather data</div>
    <button id="logoutBtn" class="logout-btn" style="display:none;"><span class="material-icons">logout</span> Logout</button>
  </header>

  <div id="authContainer" class="auth-container">
    <div class="auth-form">
      <h2>Login / Register</h2>
      <input type="email" id="authEmail" placeholder="Email"/>
      <input type="password" id="authPassword" placeholder="Password"/>
      <button id="loginBtn">Login</button>
      <button id="registerBtn">Register</button>
    </div>
  </div>

  <div class="container">
    <div class="search-area">
      <div class="search-box">
        <input id="locationInput" type="text" placeholder="Enter location..."/>
        <button id="searchBtn"><span class="material-icons">search</span> Search</button>
      </div>
      <button id="refreshBtn" class="refresh-btn" disabled title="Refresh Data"><span class="material-icons">refresh</span></button>
    </div>

    <div class="location-display"><span class="material-icons">location_on</span><span id="locationName">Location: (Not selected)</span></div>

    <div class="forecast-controls">
      <select id="dateSelect" class="forecast-select"><option value="">Select Date</option></select>
      <select id="timeSelect" class="forecast-select"><option value="">Select Hour</option></select>
    </div>

    <div class="main-content">
      <div id="map"></div>

      <div class="weather-cards">
        <div class="card"><div class="card-header"><span class="material-icons">water_drop</span> Currents</div><p id="currentsData"></p></div>
        <div class="card"><div class="card-header"><span class="material-icons">air</span> Wind</div><p id="windData"></p></div>
        <div class="card"><div class="card-header"><span class="material-icons">waves</span> Waves</div><p id="wavesData"></p></div>
        <div class="card"><div class="card-header"><span class="material-icons">device_thermostat</span> Water Temperature</div><p id="waterTempData"></p></div>
        <div class="card"><div class="card-header"><span class="material-icons">water</span> Tide Info</div><p id="tideInfoData"></p></div>
        <div class="card"><div class="card-header"><span class="material-icons">thunderstorm</span> Precipitation</div><p id="precipData"></p></div>
      </div>
    </div>

    <div class="extra-sections">
      <div class="extra-section">
        <h3>Log Your Catch</h3>
        <div class="fish-log-form">
          <input type="text" id="fishSpecies" placeholder="Fish Species" class="fish-input"/>
          <input type="number" id="fishWeight" placeholder="Weight (kg)" step="0.1" class="fish-input"/>
          <input type="datetime-local" id="catchDateTime" class="fish-input"/>
          <button id="logFishBtn" disabled class="fish-log-btn"><span class="material-icons">add_circle</span> Log Fish</button>
          <p id="clickMapMsg">Click on the map to set catch location</p>
        </div>
      </div>
      <div class="extra-section"><h3>Seasonal Fish</h3><p id="seasonalFishData">Suggestions for fish species in season at this location.</p></div>
      <div class="extra-section"><h3>Best Time of Day to Fish in <span id="locationName2">Location</span></h3><p id="bestTimeData">Recommendation of what time of day to go fishing.</p></div>
    </div>
  </div>

  <footer>© 2025 Fishing Weather App — All Rights Reserved</footer>

  <script src="https://api.mapbox.com/mapbox-gl-js/v2.12.0/mapbox-gl.js"></script>

  <script type="module">
    // Firebase
    import { initializeApp } from "https://www.gstatic.com/firebasejs/10.1.0/firebase-app.js";
    import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.1.0/firebase-analytics.js";
    import {
      getAuth,
      signInWithEmailAndPassword,
      createUserWithEmailAndPassword,
      onAuthStateChanged,
      signOut,
      setPersistence,
      browserLocalPersistence
    } from "https://www.gstatic.com/firebasejs/10.1.0/firebase-auth.js";
    import {
      getFirestore,
      collection,
      addDoc,
      onSnapshot,
      query,
      orderBy,
      enableIndexedDbPersistence,
      serverTimestamp,
      Timestamp
    } from "https://www.gstatic.com/firebasejs/10.1.0/firebase-firestore.js";

    const firebaseConfig = {
      apiKey: "AIzaSyBkDmQWdWHtn6P0-KIw_7sEA4mCMMEvs0k",
      authDomain: "fishing-app-ce0a9.firebaseapp.com",
      projectId: "fishing-app-ce0a9",
      storageBucket: "fishing-app-ce0a9.appspot.com",
      messagingSenderId: "506190773744",
      appId: "1:506190773744:web:02923ffe7d8c370ef77135",
      measurementId: "G-R32XX5FEHX"
    };

    let auth, db, catchesUnsub = null;

    try {
      const app = initializeApp(firebaseConfig);
      getAnalytics(app);

      auth = getAuth(app);

      // Auth persistence
      setPersistence(auth, browserLocalPersistence)
        .then(() => {
          console.log("[Auth] Local persistence set.");
        })
        .catch(err => {
          console.warn("[Auth] Could not set persistence, continuing with default:", err);
        });

      db = getFirestore(app);

      // Firestore offline cache
      enableIndexedDbPersistence(db).catch(err => {
        console.warn("[Firestore] Persistence not enabled (likely multiple tabs):", err?.message || err);
      });

      console.log("[Firebase] Initialized.");
    } catch (err) {
      console.error("Firebase init error", err);
      alert("Failed to initialise Firebase");
    }

    // Keys And Tokens
    const OPEN_CAGE_KEY   = "3a51e8e8b63240129a3dc0095f71cc32";
    const STORM_GLASS_KEY = "0958464a-1872-11f0-a3d7-0242ac130003-0958471c-1872-11f0-a3d7-0242ac130003";
    const MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoibXJib2JtcGxheSIsImEiOiJjbTlnY3N6a2MxdzNiMnNxMTFqZWc1YTFtIn0.90HuGQSp4dhb0MqmDEiqNw";
    mapboxgl.accessToken  = MAPBOX_ACCESS_TOKEN;

    // Seasonal Fish Helpers
    const fishData = {
      "Mediterranean Sea":{"Winter":["Cod","Hake"],"Spring":["European Seabass","Gilt-head Bream"],"Summer":["Tuna","Swordfish","Mahi Mahi"],"Autumn":["Bonito","Snapper"]},
      "Northwest Atlantic":{"Winter":["Cod","Haddock"],"Spring":["Pollock","Striped Bass"],"Summer":["Bluefish","Tuna","Mackerel"],"Autumn":["Flounder","Mackerel"]},
      "Gulf of Mexico":{"Winter":["Sheepshead","Black Drum"],"Spring":["Snapper","Spanish Mackerel"],"Summer":["Redfish","Grouper","Tuna"],"Autumn":["Speckled Trout","Flounder"]}
    };
    const detectRegion = (lat,lng)=>{
      if(lat>=30&&lat<=46&&lng>=-5&&lng<=36) return "Mediterranean Sea";
      if(lat>=30&&lat<=50&&lng>=-80&&lng<=-55) return "Northwest Atlantic";
      if(lat>=18&&lat<=31&&lng>=-98&&lng<=-80) return "Gulf of Mexico";
      return null;
    };
    const getSeason=()=>{
      const m=new Date().getMonth();
      return m>=2&&m<=4?"Spring":m>=5&&m<=7?"Summer":m>=8&&m<=10?"Autumn":"Winter";
    };
    const updateSeasonalFish=(lat,lng)=>{
      const region=detectRegion(lat,lng),season=getSeason();
      const list=region&&fishData[region]&&fishData[region][season];
      seasonalFishData.textContent=list?`For the ${region} in ${season}, you can find: ${list.join(", ")}.`:"No fish data available for your region.";
    };

    // Mapbox Init
    const map = new mapboxgl.Map({container:"map",style:"mapbox://styles/mapbox/streets-v11",center:[-80.1918,25.7617],zoom:9});
    let marker,lastLat=null,lastLng=null;

    // Marker State
    const liveMarkers = new Map();
    let isAuthenticated = false;
    let selectedFishLocation=null;

    const now=new Date(); now.setMinutes(now.getMinutes()-now.getTimezoneOffset());
    catchDateTime.value=now.toISOString().slice(0,16);

    // Geocoding
    const geocodeLocation = async place => {
      const url=`https://api.opencagedata.com/geocode/v1/json?q=${encodeURIComponent(place)}&key=${OPEN_CAGE_KEY}&limit=1`;
      try{
        const res=await fetch(url),data=await res.json();
        if(data.results?.length){
          const r=data.results[0];
          return {lat:r.geometry.lat,lng:r.geometry.lng,formattedName:r.formatted};
        }
      }catch(e){console.error(e);}
      return null;
    };

    // Weather Forecast
    async function getWeatherData(lat,lng,selectedDate=null,selectedHour=null){
      try{
        const params="waveHeight,waterTemperature,windSpeed,currentSpeed,precipitation";
        let url=`https://api.stormglass.io/v2/weather/point?lat=${lat}&lng=${lng}&params=${params}`;

        if(selectedDate && selectedHour){
          const startDT = new Date(`${selectedDate}T${selectedHour.padStart(2,"0")}:00:00Z`);
          const endDT   = new Date(startDT.getTime()+59*1000);
          const startUnix = Math.floor(startDT.getTime()/1000);
          const endUnix   = Math.floor(endDT .getTime()/1000);
          url += `&start=${startUnix}&end=${endUnix}`;
        }

        const resp = await fetch(url,{headers:{Authorization:STORM_GLASS_KEY}});
        if(!resp.ok){console.error("StormGlass error",resp.status,await resp.text());return;}
        const data = await resp.json();
        if(data.hours?.length){
          const h=data.hours[0];
          currentsData.textContent  = h.currentSpeed  ? `Current Speed: ${(h.currentSpeed.noaa  ||h.currentSpeed.meto  ||h.currentSpeed.sg ).toFixed(1)} m/s` : "Current Speed: N/A";
          windData.textContent      = h.windSpeed     ? `Wind Speed: ${(h.windSpeed.noaa     ||h.windSpeed.meto     ||h.windSpeed.sg    ).toFixed(1)} m/s` : "Wind Speed: N/A";
          wavesData.textContent     = h.waveHeight    ? `Wave Height: ${(h.waveHeight.noaa    ||h.waveHeight.meto    ||h.waveHeight.sg   ).toFixed(1)} m`   : "Wave Height: N/A";
          waterTempData.textContent = h.waterTemperature ? `Water Temp: ${(h.waterTemperature.noaa||h.waterTemperature.meto||h.waterTemperature.sg).toFixed(1)} °C` : "Water Temp: N/A";
          precipData.textContent    = h.precipitation ? `Precipitation: ${(h.precipitation.noaa||h.precipitation.meto||h.precipitation.sg).toFixed(1)} mm/hr`   : "Precipitation: N/A";
        }

        // Tide Extremes
        const tideResp = await fetch(`https://api.stormglass.io/v2/tide/extremes/point?lat=${lat}&lng=${lng}`,{headers:{Authorization:STORM_GLASS_KEY}});
        if(tideResp.ok){
          const tideData=await tideResp.json();
          if(tideData.data?.length){
            const t=tideData.data[0];
            const type=t.type.charAt(0).toUpperCase()+t.type.slice(1);
            const timeLocal=new Date(t.time).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});
            tideInfoData.textContent=`${type} Tide at ${timeLocal}`;
          }else{tideInfoData.textContent="No Tide Data";}
        }
      }catch(err){console.error(err);}
    }

    // Sunrise And Best Time
    const updateTimeOfDay = async (lat,lng)=>{
      try{
        const res=await fetch(`https://api.sunrise-sunset.org/json?lat=${lat}&lng=${lng}&date=today&formatted=0`);
        const data=await res.json();
        if(data.status==="OK"){
          const sr=new Date(data.results.sunrise).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});
          const no=new Date(data.results.solar_noon).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});
          bestTimeData.textContent=`Sunrise is at ${sr}, and solar noon around ${no}. Fish between sunrise and noon.`;
        }else{bestTimeData.textContent="Unable to retrieve sunrise/noon data.";}
      }catch(e){bestTimeData.textContent="Error fetching sunrise/noon data.";console.error(e);}
    };

    // Dropdown Population
    const populateDateSelect = ()=>{
      dateSelect.innerHTML='<option value="">Select Date</option>';
      const today=new Date();
      for(let i=0;i<7;i++){
        const d=new Date(today); d.setDate(today.getDate()+i);
        const value=d.toISOString().split("T")[0];
        const label=d.toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"});
        dateSelect.innerHTML+=`<option value="${value}">${label}</option>`;
      }
    };
    const populateTimeSelect = ()=>{
      timeSelect.innerHTML='<option value="">Select Hour</option>';
      for(let i=0;i<24;i++){
        const h=i.toString().padStart(2,"0");
        timeSelect.innerHTML+=`<option value="${h}">${h}:00</option>`;
      }
    };
    populateDateSelect(); populateTimeSelect();

    // UI Handlers
    searchBtn.addEventListener("click", async ()=>{
      const place=locationInput.value.trim();
      if(!place){alert("Please enter a location");return;}
      const res=await geocodeLocation(place);
      if(!res){alert("Unable to find coordinates");return;}

      locationName.textContent = `Location: ${res.formattedName}`;
      locationName2.textContent = res.formattedName;
      lastLat=res.lat; lastLng=res.lng;
      refreshBtn.disabled=false;

      await getWeatherData(lastLat,lastLng);
      await updateTimeOfDay(lastLat,lastLng);
      updateSeasonalFish(lastLat,lastLng);

      map.flyTo({center:[lastLng,lastLat],zoom:10});
      if(marker)marker.remove();
      marker=new mapboxgl.Marker().setLngLat([lastLng,lastLat]).addTo(map);
    });

    refreshBtn.addEventListener("click", async ()=>{
      if(lastLat===null||lastLng===null)return;
      const d=dateSelect.value, h=timeSelect.value;
      if(!d||!h){alert("Please select both date and hour");return;}
      await getWeatherData(lastLat,lastLng,d,h);
      await updateTimeOfDay(lastLat,lastLng);
      updateSeasonalFish(lastLat,lastLng);
    });

    // Map Click For Catch Location
    map.on("click",e=>{
      selectedFishLocation=e.lngLat;
      updateLogButtonEnabled();
      clickMapMsg.textContent="Location selected! You can now log your catch.";
    });

    // Marker Creation Helper
    const createFishMarker=(lng,lat,species,weight,dt)=>{
      const el=document.createElement("div");
      el.innerHTML='<span class="material-icons" style="color:var(--medium);font-size:2rem;">phishing</span>';
      const when = (dt && typeof dt === "object" && "toDate" in dt) ? dt.toDate() :
                   (typeof dt === "string" ? new Date(dt) : new Date(dt));
      return new mapboxgl.Marker(el).setLngLat([lng,lat]).setPopup(
        new mapboxgl.Popup({offset:25}).setHTML(
          `<h3>Catch Details</h3>
           <p><strong>Species:</strong> ${species}</p>
           <p><strong>Weight:</strong> ${Number(weight).toFixed(2)} kg</p>
           <p><strong>Date:</strong> ${when.toLocaleString()}</p>`
        )
      ).addTo(map);
    };

    // Log Button Enablement
    function updateLogButtonEnabled(){
      const species=fishSpecies.value.trim();
      const weight=fishWeight.value;
      const dt=catchDateTime.value;
      const ready = isAuthenticated && selectedFishLocation && species && weight && dt;
      logFishBtn.disabled = !ready;
    }
    fishSpecies.addEventListener("input", updateLogButtonEnabled);
    fishWeight.addEventListener("input", updateLogButtonEnabled);
    catchDateTime.addEventListener("input", updateLogButtonEnabled);

    // Firestore User Catches
    function detachCatchesListener(){
      if(catchesUnsub){ catchesUnsub(); catchesUnsub=null; }
    }
    function clearLiveMarkers(){
      for(const [,m] of liveMarkers.entries()){ m.remove(); }
      liveMarkers.clear();
    }

    function listenToUserCatches(user){
      detachCatchesListener();
      clearLiveMarkers();

      const colRef = collection(db, "users", user.uid, "catches");
      const q = query(colRef, orderBy("timestamp","desc"));

      console.log("[Catches] Attaching listener for", user.uid);

      catchesUnsub = onSnapshot(q, (snap)=>{
        console.log(`[Catches] Snapshot: ${snap.size} docs, changes: ${snap.docChanges().length}`);
        snap.docChanges().forEach(change=>{
          const docId = change.doc.id;
          const data = change.doc.data();

          if(change.type === "removed"){
            const m = liveMarkers.get(docId);
            if(m){ m.remove(); liveMarkers.delete(docId); }
            return;
          }

          const {location, species, weight, timestamp} = data;
          const lng = location?.lng, lat = location?.lat;
          if(typeof lng !== "number" || typeof lat !== "number") return;

          if(liveMarkers.has(docId)){
            const existing = liveMarkers.get(docId);
            existing.setLngLat([lng,lat]);
            const when = (timestamp && typeof timestamp === "object" && "toDate" in timestamp) ? timestamp.toDate() :
                         (typeof timestamp === "string" ? new Date(timestamp) : new Date(timestamp));
            existing.setPopup(new mapboxgl.Popup({offset:25}).setHTML(
              `<h3>Catch Details</h3>
               <p><strong>Species:</strong> ${species}</p>
               <p><strong>Weight:</strong> ${Number(weight).toFixed(2)} kg</p>
               <p><strong>Date:</strong> ${when.toLocaleString()}</p>`
            ));
          }else{
            const mk = createFishMarker(lng,lat,species,weight,timestamp);
            liveMarkers.set(docId, mk);
          }
        });
      }, (err)=>{
        console.error("Catches listener error:", err);
      });
    }

    async function addCatchForUser(user, {lng,lat,species,weight,dt}){
      const colRef = collection(db, "users", user.uid, "catches");
      await addDoc(colRef, {
        species: species,
        weight: Number(weight),
        timestamp: Timestamp.fromDate(new Date(dt)),
        location: { lng: Number(lng), lat: Number(lat) },
        createdAt: serverTimestamp()
      });
    }

    // Auth UI
    let initialAuthResolved = false;

    onAuthStateChanged(auth, user => {
      console.log("[Auth] State changed. user:", !!user);
      isAuthenticated = !!user;

      if (user) {
        document.getElementById("authContainer").style.display = "none";
        document.getElementById("logoutBtn").style.display = "inline-flex";
        listenToUserCatches(user);
      } else {
        document.getElementById("authContainer").style.display = "flex";
        document.getElementById("logoutBtn").style.display = "none";

        if (initialAuthResolved) {
          detachCatchesListener();
          clearLiveMarkers();
        }
      }

      initialAuthResolved = true;
      updateLogButtonEnabled();
    });

    document.getElementById("loginBtn").addEventListener("click", async () => {
      const email = authEmail.value.trim(), password = authPassword.value;
      if (!email || !password) { alert("Enter email & password"); return; }
      try {
        await signInWithEmailAndPassword(auth, email, password);
      } catch (e) { alert(e.message); }
    });

    document.getElementById("registerBtn").addEventListener("click", async () => {
      const email = authEmail.value.trim(), password = authPassword.value;
      if (!email || !password) { alert("Enter email & password"); return; }
      try {
        await createUserWithEmailAndPassword(auth, email, password);
      } catch (e) { alert(e.message); }
    });

    logoutBtn.addEventListener("click", () => signOut(auth).catch(e => alert(e.message)));

    // Fish Logger
    logFishBtn.addEventListener("click", async ()=>{
      const user = auth.currentUser;
      if(!user){ alert("Please login first."); return; }

      const species=fishSpecies.value.trim();
      const weight=fishWeight.value;
      const dt=catchDateTime.value;
      if(!species||!weight||!dt||!selectedFishLocation){
        alert("Fill all fields and pick a map location"); return;
      }

      try{
        await addCatchForUser(user, {
          lng: selectedFishLocation.lng,
          lat: selectedFishLocation.lat,
          species, weight, dt
        });

        fishSpecies.value="";
        fishWeight.value="";
        selectedFishLocation=null;
        logFishBtn.disabled=true;
        clickMapMsg.textContent="Catch saved! Click on the map to set the next catch location.";
      }catch(e){
        console.error(e);
        alert("Failed to save catch. Please try again.");
      }
    });

  </script>
</body>
</html>
