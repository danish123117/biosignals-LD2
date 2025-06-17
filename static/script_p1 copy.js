let updateIntervalRaw = null;
let updateIntervalFatigue = null;
let cobotTimer = null;

const toggleRawUpdates = document.getElementById("toggleUpdates");
const toggleFatigueState = document.getElementById("start_AD");
const toggleCobotState = document.getElementById("start_CEP");
const opState = document.getElementById("OP-State");
const cobotModeDisplay = document.getElementById("Cobot-Mode");

// Real-Time EMG Data Toggle
toggleRawUpdates.addEventListener("change", function () {
    if (this.checked) {
        updateIntervalRaw = setInterval(fetchEMGData, 1000);
    } else {
        clearInterval(updateIntervalRaw);
        updateIntervalRaw = null;
    }
});

// Fatigue Detector Toggle
toggleFatigueState.addEventListener("change", function () {
    if (this.checked) {
        updateIntervalFatigue = setInterval(processEMGdata, 5000); // every 5 seconds
    } else {
        clearInterval(updateIntervalFatigue);
        updateIntervalFatigue = null;
    }
});

// Cobot Mode Toggle
toggleCobotState.addEventListener("change", function () {
    if (this.checked) {
        startCobotMonitor(); // Start polling
    } else {
        stopCobotMonitor(); // Stop polling
    }
});

// Fetch and process EMG fatigue state
function processEMGdata() {
    opState.textContent = "Processing...";
    opState.className = "processing";

    fetch("/processEMG")
        .then(response => response.json())
        .then(data => {
            if (data.status === "OK") {
                opState.textContent = "Normal";
                opState.className = "ok";
            } else if (data.status === "No data available") {
                opState.textContent = "No data";
                opState.className = "failed";
            } else {
                opState.textContent = "Failed";
                opState.className = "failed";
            }
        })
        .catch(() => {
            opState.textContent = "Error";
            opState.className = "failed";
        });
}

// Fetch and display raw EMG values
function fetchEMGData() {
    fetch('/get_emg_data')
        .then(response => response.json())
        .then(data => {
            const values = data.data;
            for (let i = 0; i < values.length; i++) {
                document.getElementById(`emg${i + 1}`).textContent = values[i];
            }
        })
        .catch(() => {
            for (let i = 1; i <= 6; i++) {
                document.getElementById(`emg${i}`).textContent = "---";
            }
        });
}

/******************************************************************
 * Cobot monitoring
 * – Starts when the “Cobot‑Mode” switch is ON
 * – Polls /send_robot_state immediately, then every 5 min
 * – Stops completely when the switch is turned OFF
 ******************************************************************/
const COBOT_INTERVAL_MS = 1000;   // 5 minutes
let currentCobotState = null;

function startCobotMonitor() {
    clearInterval(cobotTimer);             // safety: kill any old timer
    updateCobotMode();                     // immediate first check
    cobotTimer = setInterval(updateCobotMode, COBOT_INTERVAL_MS);
}

function stopCobotMonitor() {
    clearInterval(cobotTimer);
    cobotTimer = null;
}

// Poll /send_robot_state and update cobot mode UI
function updateCobotMode() {
    fetch('/send_robot_state')
        .then(res => res.json())
        .then(data => {
            if (!('robot_state' in data)) {
                setCobotStatus('---', false);
                return;
            }

            const newState = data.robot_state; // true = Normal, false = Fatigue
            setCobotStatus(newState ? 'Normal' : 'Fatigue', newState);
            currentCobotState = newState;
        })
        .catch(() => {
            setCobotStatus('Error', false);
        });
}

// Update the Cobot Mode display and switch
function setCobotStatus(text, isNormal) {
    cobotModeDisplay.textContent = text;
    toggleCobotState.checked = isNormal;
    toggleCobotState.disabled = !isNormal;
}
