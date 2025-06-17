let updateIntervalRaw = null;
let updateIntervalFatigue = null;
let cobotTimer = null;

const toggleRawUpdates = document.getElementById("toggleUpdates");
const toggleFatigueState = document.getElementById("start_AD");
const toggleCobotState = document.getElementById("start_CEP");
const opState = document.getElementById("OP-State");
const cobotModeDisplay = document.getElementById("Cobot-Mode");

// Initialize status displays
opState.className = "status";
cobotModeDisplay.className = "status";

// Real-Time Sensor Data Toggle (now includes both EMG and HR/RR)
toggleRawUpdates.addEventListener("change", function () {
    if (this.checked) {
        updateIntervalRaw = setInterval(fetchSensorData, 1000); // Fetch all sensor data every second
    } else {
        clearInterval(updateIntervalRaw);
        updateIntervalRaw = null;
        // Clear all displays when turned off
        clearSensorDisplays();
    }
});

// Fatigue Detector Toggle
toggleFatigueState.addEventListener("change", function () {
    if (this.checked) {
        updateIntervalFatigue = setInterval(processEMGdata, 5000); // every 5 seconds
        processEMGdata(); // Immediate first update
    } else {
        clearInterval(updateIntervalFatigue);
        updateIntervalFatigue = null;
        opState.textContent = "---";
        opState.className = "status";
    }
});

// Cobot Mode Toggle
toggleCobotState.addEventListener("change", function () {
    if (this.checked) {
        startCobotMonitor();
        updateCobotMode(); // Immediate first update
    } else {
        stopCobotMonitor();
        cobotModeDisplay.textContent = "Manual";
        cobotModeDisplay.className = "status";
    }
});

/******************************************************************
 * Sensor Data Functions
 ******************************************************************/

// Clear all sensor displays
function clearSensorDisplays() {
    // Clear EMG displays
    for (let i = 1; i <= 6; i++) {
        document.getElementById(`emg${i}`).textContent = "---";
    }
    // Clear HR/RR displays
    document.getElementById("hrValue").textContent = "---";
    document.getElementById("rrValue").textContent = "---";
}

// Fetch all sensor data (EMG + HR/RR)
function fetchSensorData() {
    fetchEMGData();
    fetchHRData();
}

// Fetch and display raw EMG values
function fetchEMGData() {
    fetch('/get_emg_data')
        .then(response => {
            if (!response.ok) throw new Error("EMG data not available");
            return response.json();
        })
        .then(data => {
            const values = data.data;
            for (let i = 0; i < values.length; i++) {
                document.getElementById(`emg${i + 1}`).textContent = values[i];
            }
        })
        .catch(error => {
            console.error("Error fetching EMG data:", error);
            for (let i = 1; i <= 6; i++) {
                document.getElementById(`emg${i}`).textContent = "---";
            }
        });
}

// Fetch and display HR/RR values
// Fetch and display HR/RR values
function fetchHRData() {
    fetch('/get_hr_data')
        .then(response => {
            if (!response.ok) throw new Error("HR data not available");
            return response.json();
        })
        .then(data => {
            if (data.status === 'OK') {
                // Update HR display
                const hrDisplay = document.getElementById("hrValue");
                hrDisplay.textContent = data.hr_value;
                hrDisplay.className = "value";  // Add CSS class for styling
                
                // Update RR display
                const rrDisplay = document.getElementById("rrValue");
                rrDisplay.textContent = data.rr_value;
                rrDisplay.className = "value";  // Add CSS class for styling
            } else {
                throw new Error(data.error || "Unknown error");
            }
        })
        .catch(error => {
            console.error("Error fetching HR data:", error);
            document.getElementById("hrValue").textContent = "---";
            document.getElementById("rrValue").textContent = "---";
        });
}

// Fetch and process EMG fatigue state
function processEMGdata() {
    opState.textContent = "Processing...";
    opState.className = "processing";

    fetch("/processEMG")
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
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
        .catch(error => {
            console.error("Error processing EMG data:", error);
            opState.textContent = "Error";
            opState.className = "failed";
        });
}

/******************************************************************
 * Cobot Monitoring Functions
 ******************************************************************/
const COBOT_INTERVAL_MS = 1000; // Changed to 1 second for more responsive updates

function startCobotMonitor() {
    clearInterval(cobotTimer); // safety: kill any old timer
    cobotTimer = setInterval(updateCobotMode, COBOT_INTERVAL_MS);
}

function stopCobotMonitor() {
    clearInterval(cobotTimer);
    cobotTimer = null;
}

function updateCobotMode() {
    fetch('/send_robot_state')
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            if (!('robot_state' in data)) {
                setCobotStatus('---', false);
                return;
            }
            const newState = data.robot_state; // true = Normal, false = Fatigue
            setCobotStatus(newState ? 'Normal' : 'Fatigue', newState);
        })
        .catch(error => {
            console.error("Error updating cobot mode:", error);
            setCobotStatus('Error', false);
        });
}

function setCobotStatus(text, isNormal) {
    cobotModeDisplay.textContent = text;
    cobotModeDisplay.className = isNormal ? "ok" : "failed";
}

/******************************************************************
 * Initialization
 ******************************************************************/
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all displays
    clearSensorDisplays();
    opState.textContent = "---";
    cobotModeDisplay.textContent = "---";
});