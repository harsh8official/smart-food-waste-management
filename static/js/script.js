// Shared frontend behavior for forms, previews, and analytics.
document.addEventListener("DOMContentLoaded", () => {
    const roleSelect = document.getElementById("roleSelect");
    const ngoFields = document.querySelectorAll(".ngo-only");

    function toggleNgoFields() {
        if (!roleSelect) return;
        const isNgo = roleSelect.value === "ngo";
        ngoFields.forEach((field) => field.classList.toggle("d-none", !isNgo));
    }

    if (roleSelect) {
        roleSelect.addEventListener("change", toggleNgoFields);
        toggleNgoFields();
    }

    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", (event) => {
            const password = registerForm.querySelector("[name='password']").value;
            const confirm = registerForm.querySelector("[name='confirm_password']").value;
            if (password !== confirm) {
                event.preventDefault();
                alert("Passwords do not match.");
            }
        });
    }

    const chartCanvas = document.getElementById("categoryChart");
    if (chartCanvas && window.Chart) {
        const labels = JSON.parse(chartCanvas.dataset.labels || "[]");
        const values = JSON.parse(chartCanvas.dataset.values || "[]");
        new Chart(chartCanvas, {
            type: "doughnut",
            data: {
                labels,
                datasets: [{
                    label: "Donations",
                    data: values,
                    backgroundColor: ["#198754", "#f7b731", "#0d6efd", "#20c997", "#6f42c1", "#fd7e14"],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });
    }
});
