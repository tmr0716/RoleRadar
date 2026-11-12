const API_BASE = "https://roleradar-7egx.onrender.com/api/v1";

document.addEventListener("DOMContentLoaded", () => {
    fetchApplications();
    fetchStats();

    const form = document.getElementById("app-form");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const payload = {
            company_name: document.getElementById("company").value,
            role_title: document.getElementById("role").value,
            job_url: document.getElementById("url").value || null,
            applied_date: document.getElementById("date").value
        };

        try {
            const res = await fetch(`${API_BASE}/applications`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                form.reset();
                fetchApplications();
                fetchStats();
            } else {
                const errData = await res.json();
                alert(`Error adding application: ${errData.error || 'Server error'}`);
            }
        } catch (err) {
            alert("Could not connect to the RoleRadar backend server.");
            console.error(err);
        }
    });
});

async function fetchApplications() {
    try {
        const res = await fetch(`${API_BASE}/applications`);
        if (!res.ok) return;
        const apps = await res.json();
        const list = document.getElementById("applications-list");
        list.innerHTML = "";

        if (apps.length === 0) {
            list.innerHTML = `<p style="color: #64748b; font-size: 0.95rem;">No applications tracked yet.</p>`;
            return;
        }

        apps.forEach(app => {
            const card = document.createElement("div");
            card.className = "app-card";
            card.innerHTML = `
                <div>
                    <h3>${app.company_name} — <small style="color: #64748b; font-weight: normal;">${app.role_title}</small></h3>
                    <p>Applied on: ${app.applied_date}</p>
                </div>
                <div style="display: flex; align-items: center;">
                    <span class="badge badge-${app.status}">${app.status}</span>
                    <select onchange="updateStatus(${app.application_id}, this.value)">
                        <option value="">Update Status...</option>
                        <option value="OA_RECEIVED">OA Received</option>
                        <option value="INTERVIEWING">Interviewing</option>
                        <option value="OFFER">Offer</option>
                        <option value="REJECTED">Rejected</option>
                    </select>
                </div>
            `;
            list.appendChild(card);
        });
    } catch (err) {
        console.error("Fetch applications error:", err);
    }
}

async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE}/analytics/stats`);
        if (!res.ok) return;
        const stats = await res.json();
        document.getElementById("stat-total").innerText = stats.total_applications || 0;
        document.getElementById("stat-interview").innerText = stats.interviewing || 0;
        document.getElementById("stat-offer").innerText = stats.offers || 0;
        document.getElementById("stat-rejected").innerText = stats.rejected || 0;
    } catch (err) {
        console.error("Fetch stats error:", err);
    }
}

async function updateStatus(id, newStatus) {
    if (!newStatus) return;
    try {
        const res = await fetch(`${API_BASE}/applications/${id}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus })
        });

        const data = await res.json();
        if (!res.ok) {
            alert(`Transition Warning: ${data.message || data.error}`);
        }
        fetchApplications();
        fetchStats();
    } catch (err) {
        console.error("Update status error:", err);
    }
}
