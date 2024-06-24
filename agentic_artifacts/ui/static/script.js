document.addEventListener('DOMContentLoaded', () => {
    const generateForm = document.getElementById('generate-form');
    const promptInput = document.getElementById('prompt');
    const resultDiv = document.getElementById('result');
    const loadingSpinner = document.getElementById('loading-spinner');

    generateForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = promptInput.value.trim();

        if (!prompt) {
            resultDiv.innerHTML = 'Please enter a prompt.';
            return;
        }

        resultDiv.innerHTML = '';
        loadingSpinner.style.display = 'block';

        try {
            const response = await fetch(`/generate?prompt=${encodeURIComponent(prompt)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            if (data.error) {
                resultDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
            } else if (data.preview_url) {
                resultDiv.innerHTML = `
                    <h3>Generated Sandbox:</h3>
                    <iframe id="sandbox-frame" src="${data.preview_url}" style="width:100%; height:500px; border:0; border-radius: 4px; overflow:hidden;"></iframe>
                    <p><a href="${data.preview_url}" target="_blank">Open in new tab</a></p>
                `;

                const iframe = document.getElementById('sandbox-frame');
                iframe.onload = () => {
                    const iframeWindow = iframe.contentWindow;
                    iframeWindow.onerror = (message, source, lineno, colno, error) => {
                        fetch('/report-error', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                errorMessage: error ? error.stack : message,
                                prompt
                            })
                        }).then(res => res.json())
                          .then(data => {
                              if (data.fixed_code) {
                                  // Display the fixed code or update the iframe
                                  resultDiv.innerHTML += `<pre>${data.fixed_code}</pre>`;
                              } else if (data.error) {
                                  resultDiv.innerHTML += `<div class="error">Error: ${data.error}</div>`;
                              }
                          });
                    };
                };
            } else {
                resultDiv.innerHTML = `<div class="error">Unexpected response from server</div>`;
            }
        } catch (error) {
            resultDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
        } finally {
            loadingSpinner.style.display = 'none';
        }
    });
});
