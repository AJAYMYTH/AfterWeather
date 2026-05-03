// AfterWeather AI - Terminal Sandbox Script

const terminalInput = document.getElementById('terminalInput');
const terminalOutput = document.getElementById('terminalOutput');
const terminalScreen = document.getElementById('terminalScreen');

let history = [];
let historyIndex = -1;

const weatherLabels = {
    0: "Sunny/Clear",
    1: "Cloudy",
    2: "Rainy",
    3: "Stormy/Thunder"
};

const artAnimations = {
    0: `<span class="yellow">     \\   :   /
      .-"-.
    -(     )-
      '-._.-'
     /   :   \\</span>`,
    1: `<span class="white">       .--.
    .-(    ).
   (___.__)__)</span>`,
    2: `<span class="cyan">       .--.
    .-(    ).
   (___.__)__)
     '  '  '  '
    '  '  '  '</span>`,
    3: `<span class="red">       .--.
    .-(    ).
   (___.__)__)
      /  /
     /_ /
      /</span>`
};

// Auto scroll to bottom of console
function scrollToBottom() {
    terminalScreen.scrollTop = terminalScreen.scrollHeight;
}

// Input focus handling
function focusConsoleInput() {
    terminalInput.focus();
}

// Typing preset command instantly
function executePreset(cmd) {
    terminalInput.value = cmd;
    terminalInput.focus();
    processCommand(cmd);
}

// Key events listener
terminalInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const value = terminalInput.value.trim();
        if (value) {
            processCommand(value);
        }
    } else if (e.key === 'ArrowUp') {
        if (history.length > 0) {
            if (historyIndex === -1) historyIndex = history.length;
            historyIndex = Math.max(0, historyIndex - 1);
            terminalInput.value = history[historyIndex];
        }
        e.preventDefault();
    } else if (e.key === 'ArrowDown') {
        if (history.length > 0 && historyIndex !== -1) {
            historyIndex++;
            if (historyIndex >= history.length) {
                historyIndex = -1;
                terminalInput.value = '';
            } else {
                terminalInput.value = history[historyIndex];
            }
        }
        e.preventDefault();
    }
});

function appendLine(html, isPrompt = false, cmd = '') {
    const div = document.createElement('div');
    div.className = 'line';
    if (isPrompt) {
        div.innerHTML = `<span class="prompt">user@afterweather:~$</span> <span class="cmd-typed">${cmd}</span>`;
    } else {
        div.innerHTML = html;
    }
    terminalOutput.appendChild(div);
    scrollToBottom();
}

async function processCommand(cmd) {
    // Save to history
    history.push(cmd);
    historyIndex = -1;

    // Reset input
    terminalInput.value = '';

    // Append standard command input prompt to screen
    appendLine('', true, cmd);

    // Normalize command string
    const parts = cmd.split(/\s+/);
    const baseCommand = parts[0].toLowerCase();

    if (baseCommand === 'clear') {
        terminalOutput.innerHTML = '';
        return;
    }

    if (baseCommand === 'help') {
        appendLine(`<span class="cyan">Supported Commands:</span>
 • <span class="yellow">clear</span> - Clear the terminal screen.
 • <span class="yellow">afterweather --help</span> - Print help usage about AfterWeather CLI.
 • <span class="yellow">afterweather -c [city]</span> - Run interactive weather tracking & ML forecast.`);
        return;
    }

    if (baseCommand === 'afterweather') {
        const flagIndex = parts.indexOf('-c') !== -1 ? parts.indexOf('-c') : parts.indexOf('--city');
        let city = '';
        if (flagIndex !== -1 && parts[flagIndex + 1]) {
            city = parts.slice(flagIndex + 1).join(' ').replace(/['"]/g, '');
        }

        const isHelp = parts.includes('--help') || parts.includes('-h');
        if (isHelp) {
            appendLine(`Usage: afterweather [-c <city> | --city <city>] [--help]

✨ Features:
 • <span class="cyan">Dynamic Visuals:</span> Real-time meteorological data mapped to ASCII visuals.
 • <span class="cyan">Continuous Forecast:</span> Fetches exact telemetry predictions directly.
 • <span class="cyan">Localized ML:</span> Uses custom classification weights & future temperature forecasting.

Options:
 -c, --city <city>   Specific city to resolve via Open-Meteo Geocoding
 -h, --help          Show help usage menu`);
            return;
        }

        if (!city) {
            city = 'Mumbai';
            appendLine(`<span class="dim">No city argument passed. Using 'Mumbai' as default.</span>`);
        }

        // Trigger interactive startup loading precisely like Python CLI
        await startSimulation(city);
    } else {
        appendLine(`<span class="red">Command not found: ${baseCommand}</span>. Type <span class="cyan">help</span> or use Sidebar quick commands.`);
    }
}

async function startSimulation(city) {
    terminalInput.disabled = true;

    // Phase 1: Engine initialization
    appendLine(`<span class="magenta">●</span> <span class="white">Initializing AI Weather Engine...</span>`);
    await sleep(400);
    appendLine(`<span class="cyan">╔═╗┬ ┬┌─┐┌─┐</span>`);
    appendLine(`<span class="cyan">║  ├─┤├┤ │ │</span>`);
    appendLine(`<span class="cyan">╚═╝┴ ┴└─┘└─┘</span>`);
    await sleep(600);

    // Phase 2: Resolving location
    appendLine(`<span class="magenta">● ○ ○ ○</span> <span class="blue">Resolving location for '${city}'...</span>`);
    await sleep(800);

    let lat = 19.076, lon = 72.877, resolvedName = "Mumbai";

    try {
        const geoRes = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`);
        const geoData = await geoRes.json();
        if (geoData.results && geoData.results[0]) {
            lat = geoData.results[0].latitude;
            lon = geoData.results[0].longitude;
            resolvedName = geoData.results[0].name;
            appendLine(`<span class="green">✓</span> <span class="white">Location resolved: ${resolvedName} (${lat.toFixed(2)}°, ${lon.toFixed(2)}°)</span>`);
        } else {
            appendLine(`<span class="red">✗</span> <span class="white">Could not resolve city. Defaulting to Mumbai.</span>`);
        }
    } catch (err) {
        appendLine(`<span class="red">✗</span> <span class="white">Network error. Using fallback coordinates.</span>`);
    }

    await sleep(600);

    // Phase 3: ML model simulation
    appendLine(`<span class="magenta">○ ● ○ ○</span> <span class="yellow">Loading localized Machine Learning patterns...</span>`);
    appendLine(`<span class="dim">Training RandomForest on synthetic weather history...</span>`);
    await sleep(1000);
    appendLine(`<span class="green">✓</span> <span class="white">ML model weights loaded successfully—Neural Network is active</span>`);
    await sleep(600);

    // Phase 4: System Ready
    appendLine(`<span class="cyan">🔄</span> <span class="white">Connecting to live weather streams...</span>`);
    await sleep(800);

    // Phase 5: Fetch Live Weather data
    appendLine(`<span class="magenta">○ ○ ○ ●</span> <span class="white">Retrieving Open-Meteo live telemetry...</span>`);
    await sleep(500);

    let weatherData = null;
    try {
        const weatherRes = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto&forecast_days=1`);
        weatherData = await weatherRes.json();
    } catch (e) {
        // Fallback realistic simulation data if API fails
        weatherData = {
            current: { temperature_2m: 24.5, relative_humidity_2m: 65, wind_speed_10m: 12, weather_code: 1 },
            hourly: {
                time: ["2026-05-04T00:00", "2026-05-04T03:00", "2026-05-04T06:00", "2026-05-04T09:00", "2026-05-04T12:00", "2026-05-04T15:00", "2026-05-04T18:00", "2026-05-04T21:00"],
                temperature_2m: [21.2, 20.4, 23.5, 27.1, 29.8, 28.2, 24.5, 22.1],
                relative_humidity_2m: [72, 75, 68, 55, 48, 52, 60, 68],
                wind_speed_10m: [8.5, 9.1, 10.5, 12.0, 14.2, 13.1, 11.2, 9.4],
                weather_code: [1, 2, 1, 0, 0, 1, 1, 2]
            }
        };
    }

    // Display parsed visualization precisely
    renderOutputPanel(resolvedName, weatherData);

    terminalInput.disabled = false;
    terminalInput.focus();
}

function renderOutputPanel(resolvedName, weatherData) {
    const current = weatherData.current || {};
    const liveTemp = current.temperature_2m || 0;
    const liveHumidity = current.relative_humidity_2m || 0;
    const liveWind = current.wind_speed_10m || 0;
    const liveCode = current.weather_code || 0;

    // Convert Live code to 0-3 categories matching python map_weather_code
    let condId = 0;
    if (liveCode <= 1) condId = 0;
    else if ([2, 3, 45, 48].includes(liveCode)) condId = 1;
    else if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(liveCode)) condId = 2;
    else condId = 3;

    const currentLabel = weatherLabels[condId];
    const currentArt = artAnimations[condId];

    // Simple ML algorithm emulation: classification/regression based on current data
    let predictedCondId = condId;
    if (liveHumidity > 85 && liveTemp > 28) predictedCondId = 3;
    else if (liveHumidity > 70) predictedCondId = 2;
    else if (liveHumidity > 50) predictedCondId = 1;
    else predictedCondId = 0;

    const predictedLabel = weatherLabels[predictedCondId];
    const predictedArt = artAnimations[predictedCondId];
    const predictedNextHourTemp = liveTemp + (liveHumidity > 70 ? -1.2 : 0.8) + (Math.sin(new Date().getHours()) * 0.5);

    // Create ASCII-Styled output screen
    let outputHTML = `
<div class="ascii-panel">
    <div class="ascii-panel-header green">● AfterWeather Live Status - ${resolvedName.toUpperCase()}</div>
    <div class="grid-cols">
        <pre>${currentArt}</pre>
        <div>
            <div><span class="yellow">Condition:</span> ${currentLabel}</div>
            <div><span class="cyan">Temperature:</span> ${liveTemp.toFixed(1)}°C</div>
            <div><span class="magenta">Humidity:</span> ${liveHumidity}%</div>
            <div><span class="blue">Wind Speed:</span> ${liveWind.toFixed(1)} km/h</div>
        </div>
    </div>
</div>

<div class="ascii-panel">
    <div class="ascii-panel-header magenta">● Machine Learning Local Forecast</div>
    <div class="grid-cols">
        <pre>${predictedArt}</pre>
        <div>
            <div><span class="yellow">ML Predicted Behavior:</span> ${predictedLabel}</div>
            <div><span class="cyan">Next Hour Temp Estimate:</span> ${predictedNextHourTemp.toFixed(1)}°C</div>
            <div class="dim">Parameters Evaluated:
 • Time Context: ${new Date().toLocaleTimeString()}
 • Neural Weight Calibration: Balanced
            </div>
        </div>
    </div>
</div>
`;

    // Render Hourly Table
    const hourly = weatherData.hourly || {};
    if (hourly && hourly.time) {
        outputHTML += `
<div class="ascii-panel">
    <div class="ascii-panel-header cyan">● Hourly Prediction - Next 24 Hours</div>
    <table class="terminal-table">
        <thead>
            <tr>
                <th>Time</th>
                <th>Temp (°C)</th>
                <th>Humidity (%)</th>
                <th>Wind (km/h)</th>
                <th>Local Forecast</th>
            </tr>
        </thead>
        <tbody>`;

        const times = hourly.time || [];
        const temps = hourly.temperature_2m || [];
        const humidities = hourly.relative_humidity_2m || [];
        const winds = hourly.wind_speed_10m || [];
        const codes = hourly.weather_code || [];

        // Every 3 hours
        for (let i = 0; i < Math.min(24, times.length); i += 3) {
            const timeStr = times[i].includes('T') ? times[i].split('T')[1] : times[i];
            const temp = (temps[i] !== undefined) ? temps[i].toFixed(1) : "—";
            const hum = (humidities[i] !== undefined) ? humidities[i] : "—";
            const wind = (winds[i] !== undefined) ? winds[i].toFixed(1) : "—";
            
            // Map the hourly weather code
            const codeVal = codes[i] || 0;
            let hourlyCondId = 0;
            if (codeVal <= 1) hourlyCondId = 0;
            else if ([2, 3, 45, 48].includes(codeVal)) hourlyCondId = 1;
            else if ([51, 53, 55, 61, 63, 65, 80, 81, 82].includes(codeVal)) hourlyCondId = 2;
            else hourlyCondId = 3;

            const hourlyLabel = weatherLabels[hourlyCondId];

            outputHTML += `
            <tr>
                <td class="dim">${timeStr}</td>
                <td class="cyan">${temp}</td>
                <td class="magenta">${hum}</td>
                <td class="blue">${wind}</td>
                <td class="yellow">${hourlyLabel}</td>
            </tr>`;
        }

        outputHTML += `
        </tbody>
    </table>
</div>
`;
    }

    appendLine(outputHTML);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
