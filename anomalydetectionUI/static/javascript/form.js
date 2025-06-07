
document.getElementById('trainButton').addEventListener('click', function () {
    // Collect form data from the Train section
    const trainSection = document.getElementById('Train');
    const formData = {};

    // Collect all input, select, and textarea values
    trainSection.querySelectorAll('input, select, textarea').forEach(input => {
        if (input.type === 'checkbox') {
            if (!formData[input.name]) {
                formData[input.name] = [];
            }
            if (input.checked) {
                formData[input.name].push(input.value);
            }
        } else if (input.type === 'radio') {
            if (input.checked) {
                formData[input.name] = input.value;
            }
        } else {
            formData[input.id] = input.value;
        }
    });

    

    // Send the data to the Flask backend
    fetch('/train', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Handle success response
        if (data.success) {
            alert('Form submitted successfully!' + data.message);
        } else {
            alert('Form submission failed: ' + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while submitting the form.');
    });
});



document.getElementById('detectButton').addEventListener('click', function () {
    // Collect form data from the Train section
    const detectSection = document.getElementById('Detect');
    const formData = {};

    // Collect all input, select, and textarea values
    detectSection.querySelectorAll('input, select, textarea').forEach(input => {
        if (input.type === 'checkbox') {
            if (!formData[input.name]) {
                formData[input.name] = [];
            }
            if (input.checked) {
                formData[input.name].push(input.value);
            }
        } else if (input.type === 'radio') {
            if (input.checked) {
                formData[input.name] = input.value;
            }
        } else {
            formData[input.id] = input.value;
        }
    });

    

    fetch('/detect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Handle success response
        if (!data.success) {
            alert('Form submission failed: ' + data.message);
            return;
        }

        

        const timestamps = data.data.map(d => d.timestamp);
        const values = data.data.map(d => d.value);
        const lower = data.data.map(d => d.lower);
        const upper = data.data.map(d => d.upper);
        const anomalies = data.data.filter(d => d.anomaly === 1);

        const trace_main = {
            x: timestamps,
            y: values,
            mode: 'lines+markers',
            name: 'Metric'
        };

        const trace_confidence = {
            x: [...timestamps, ...timestamps.slice().reverse()],
            y: [...upper, ...lower.slice().reverse()],
            fill: 'toself',
            fillcolor: 'rgba(0,100,80,0.2)',
            line: { color: 'transparent' },
            showlegend: true,
            name: 'Confidence Interval'
        };

        const trace_anomalies = {
            x: anomalies.map(a => a.timestamp),
            y: anomalies.map(a => a.value),
            text: anomalies.map(a => {
                const predictedValue = a.predicted;  // Assuming the predicted value is part of the data
                const difference = (a.value - predictedValue).toFixed(2); // Calculate difference
                const significance = Math.abs(difference) > 5 ? "High Significance" : "Normal"; // Threshold for significance

                return `
                    Anomaly
                    Time: ${a.timestamp}
                    Value: ${a.value}
                    Predicted: ${predictedValue}
                    Difference: ${difference}
                    Significance: ${significance}
                `;
            }),
            mode: 'markers',
            marker: {
                color: 'red',
                size: 12,
                symbol: 'circle-open-dot',  // Change symbol for better visibility
                line: {
                    width: 2,
                    color: 'darkred'
                }
            },
            name: 'Anomalies',
            hoverinfo: 'text'
        };

        Plotly.newPlot('chart', [trace_confidence, trace_main, trace_anomalies], {
            title: "Anomaly Detection with Confidence Bounds",
            xaxis: { title: "Time" },
            yaxis: { title: "Metric Value" },
            autosize: true,
            margin: { l: 50, r: 50, t: 50, b: 50 }
        }, { responsive: true });
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred while submitting the form.');
    });
});


document.getElementById('detectAppId').addEventListener('focusout', async function () {
    const detectAppId = this.value.trim(); // Get the value of the detectAppId input field
    const modelDropdown = document.getElementById('modelID');
    modelDropdown.innerHTML = '<option value="">Select modelID</option>'; // Reset dropdown to default

    if (!detectAppId) {
        alert('Please enter a valid App ID.');
        return;
    }

    try {
        // Call the /models endpoint with the detectAppId as a query parameter
        const response = await fetch(`/models?detectAppId=${encodeURIComponent(detectAppId)}`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch models: ${response.statusText}`);
        }

        const data = await response.json();

        // Check if models are returned
        if (data.models && data.models.length > 0) {

            // Populate the dropdown with model names
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelDropdown.appendChild(option);
            });
        } else {
            alert('No models found for the given App ID.');
        }
    } catch (error) {
        console.error('Error fetching models:', error);
        alert('An error occurred while fetching models. Please try again.');
    }
});


document.getElementById('modelID').addEventListener('change', async function () {
    const select = this;
    const modelId = select.value;
    const appId =  document.getElementById('detectAppId').value.trim(); // Get the value of the detectAppId input field

    if (!appId || !modelId) return;

    try {
        const response = await fetch(`/get_model_data?appId=${encodeURIComponent(appId)}&modelId=${encodeURIComponent(modelId)}`);
        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        console.log("Fetched model data:", data);
        // Optionally: Update UI with fetched data
        document.getElementById("modelDataOutput").textContent = JSON.stringify(data, null, 2);

    } catch (err) {
        console.error("Error fetching model data:", err);
        alert("An error occurred while fetching model data.");
    }
});