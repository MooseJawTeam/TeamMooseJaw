// Form handling functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Handle file uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const files = this.files;
            const maxSize = 5 * 1024 * 1024; // 5MB
            const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png'];

            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                if (file.size > maxSize) {
                    alert(`File ${file.name} is too large. Maximum size is 5MB.`);
                    this.value = '';
                    return;
                }
                if (!allowedTypes.includes(file.type)) {
                    alert(`File ${file.name} is not a valid type. Allowed types are PDF, JPEG, and PNG.`);
                    this.value = '';
                    return;
                }
            }
        });
    });

    // Handle signature pads
    const signaturePads = {};
    const signatureCanvases = document.querySelectorAll('.signature-pad canvas');
    signatureCanvases.forEach(canvas => {
        const pad = new SignaturePad(canvas);
        const fieldName = canvas.closest('.signature-pad').dataset.fieldName;
        signaturePads[fieldName] = pad;

        // Resize canvas
        function resizeCanvas() {
            const ratio = Math.max(window.devicePixelRatio || 1, 1);
            canvas.width = canvas.offsetWidth * ratio;
            canvas.height = canvas.offsetHeight * ratio;
            canvas.getContext('2d').scale(ratio, ratio);
            pad.clear();
        }

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
    });

    // Clear signature
    window.clearSignature = function(fieldName) {
        if (signaturePads[fieldName]) {
            signaturePads[fieldName].clear();
        }
    };

    // Save all signatures before form submission
    window.saveAllSignatures = function() {
        Object.keys(signaturePads).forEach(fieldName => {
            const pad = signaturePads[fieldName];
            if (!pad.isEmpty()) {
                const input = document.querySelector(`input[name="${fieldName}"]`);
                if (input) {
                    input.value = pad.toDataURL();
                }
            }
        });
    };
}); 