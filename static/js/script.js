document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const colorForm = document.getElementById('colorForm');
    const skinColorInput = document.getElementById('skinColor');
    const hairColorInput = document.getElementById('hairColor');
    const eyeColorInput = document.getElementById('eyeColor');
    const skinHexInput = document.getElementById('skinHex');
    const hairHexInput = document.getElementById('hairHex');
    const eyeHexInput = document.getElementById('eyeHex');
    const skinSwatch = document.getElementById('skinSwatch');
    const hairSwatch = document.getElementById('hairSwatch');
    const eyeSwatch = document.getElementById('eyeSwatch');
    const resultsSection = document.getElementById('resultsSection');
    const seasonName = document.getElementById('seasonName');
    const dominantTrait = document.getElementById('dominantTrait');
    const reasoning = document.getElementById('reasoning');
    const seasonBadge = document.getElementById('seasonBadge');

    // Color input event listeners
    skinColorInput.addEventListener('input', () => updateHexInput(skinColorInput, skinHexInput, skinSwatch));
    hairColorInput.addEventListener('input', () => updateHexInput(hairColorInput, hairHexInput, hairSwatch));
    eyeColorInput.addEventListener('input', () => updateHexInput(eyeColorInput, eyeHexInput, eyeSwatch));

    // Hex input event listeners
    skinHexInput.addEventListener('input', (e) => updateColorInput(e, skinHexInput, skinColorInput, skinSwatch));
    hairHexInput.addEventListener('input', (e) => updateColorInput(e, hairHexInput, hairColorInput, hairSwatch));
    eyeHexInput.addEventListener('input', (e) => updateColorInput(e, eyeHexInput, eyeColorInput, eyeSwatch));

    // Form submission
    colorForm.addEventListener('submit', handleFormSubmit);

    // Initialize swatches
    updateSwatches();

    // Function to update hex input when color picker changes
    function updateHexInput(colorInput, hexInput, swatch) {
        hexInput.value = colorInput.value.toUpperCase();
        updateSwatches();
    }

    // Function to update color input when hex value changes
    function updateColorInput(e, hexInput, colorInput, swatch) {
        const value = e.target.value;
        if (value.match(/^#[0-9A-Fa-f]{6}$/)) {
            colorInput.value = value.toUpperCase();
            updateSwatches();
        }
    }

    // Update all color swatches
    function updateSwatches() {
        skinSwatch.style.backgroundColor = skinColorInput.value;
        hairSwatch.style.backgroundColor = hairColorInput.value;
        eyeSwatch.style.backgroundColor = eyeColorInput.value;
    }

    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        // Show loading state
        resultsSection.style.display = 'block';
        seasonName.textContent = 'Analyzing...';
        dominantTrait.textContent = '';
        reasoning.textContent = '';
        seasonBadge.textContent = '';

        // Prepare request data
        const requestData = {
            skin: {
                match: {
                    hex: skinColorInput.value.toUpperCase()
                },
                analysis: {}
            },
            hair: {
                match: {
                    hex: hairColorInput.value.toUpperCase()
                },
                analysis: {}
            },
            eyes: {
                match: {
                    hex: eyeColorInput.value.toUpperCase()
                },
                analysis: {}
            }
        };

        try {
            // First, analyze each color
            const skinAnalysis = await analyzeColor(skinColorInput.value);
            const hairAnalysis = await analyzeColor(hairColorInput.value);
            const eyeAnalysis = await analyzeColor(eyeColorInput.value);

            // Add analysis to request data
            requestData.skin.analysis = skinAnalysis;
            requestData.hair.analysis = hairAnalysis;
            requestData.eyes.analysis = eyeAnalysis;

            // Send to season analysis endpoint
            const response = await fetch('/analyze-color-season', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            displayResults(result);
            
        } catch (error) {
            console.error('Error:', error);
            seasonName.textContent = 'Error';
            dominantTrait.textContent = 'Failed to analyze colors';
            reasoning.textContent = 'Please try again or check your connection.';
        }
    }

    // Analyze a single color
    async function analyzeColor(hex) {
        try {
            const response = await fetch(`/color?hex_code=${encodeURIComponent(hex)}`);
            if (!response.ok) {
                throw new Error(`Color analysis failed: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Color analysis error:', error);
            return {};
        }
    }

    // Display the analysis results
    function displayResults(data) {
        // Reset previous results
        seasonName.textContent = 'Analyzing...';
        dominantTrait.textContent = '';
        reasoning.textContent = '';
        seasonBadge.textContent = '';

        // If we got raw output from the model
        if (data.raw_output) {
            try {
                // First, try to extract JSON from the response
                const jsonMatch = data.raw_output.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    const parsed = JSON.parse(jsonMatch[0]);
                    updateSeasonDisplay(parsed);
                } else {
                    // If no JSON found, try to extract season name directly
                    const seasonMatch = data.raw_output.match(/"?season"?\s*[:=]\s*"?([^"\n}]+)"?/i);
                    if (seasonMatch && seasonMatch[1]) {
                        updateSeasonDisplay({
                            season: seasonMatch[1].trim(),
                            dominant_trait: 'Analyzed based on color characteristics',
                            reasoning: 'The analysis was successful, but some details might be missing.'
                        });
                    } else {
                        // If we can't extract anything, show the raw output
                        showError('Could not determine season', data.raw_output);
                    }
                }
            } catch (e) {
                console.error('Error parsing response:', e);
                showError('Error parsing results', 'Could not process the response from the server.');
            }
        } else if (data.season_analysis) {
            // If we got a structured response
            updateSeasonDisplay(data.season_analysis);
        } else if (data.error) {
            showError('Analysis Error', data.details || 'An unknown error occurred');
        } else {
            // Fallback for any other response format
            showError('Unexpected Response', JSON.stringify(data, null, 2));
        }
    }

    // Update the UI with season analysis results
    function updateSeasonDisplay(analysis) {
        seasonName.textContent = analysis.season || 'Unknown Season';
        dominantTrait.textContent = analysis.dominant_trait || '';
        reasoning.textContent = analysis.reasoning || '';
        
        // Create badge from season name (e.g., "Deep Winter" -> "DW")
        const badgeText = analysis.season 
            ? analysis.season.split(' ').map(word => word[0]).join('') 
            : '?';
        seasonBadge.textContent = badgeText;
        
        // Add a class based on season type for styling
        const seasonType = analysis.season ? analysis.season.split(' ')[0].toLowerCase() : 'unknown';
        seasonBadge.className = 'season-badge ' + seasonType;
    }
    
    // Show error message to the user
    function showError(title, message) {
        seasonName.textContent = title;
        reasoning.textContent = message;
        seasonBadge.textContent = '!';
        seasonBadge.className = 'season-badge error';
    }

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
});
