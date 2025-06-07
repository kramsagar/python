
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

