// =========================================================
// 🌙 SIMPLE THEME SYSTEM
// =========================================================

function applySavedTheme() {
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme === "dark") {
    document.body.classList.add("dark");
  } else {
    document.body.classList.remove("dark");
  }
}

function toggleTheme() {
  const isDark = document.body.classList.toggle("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
}

applySavedTheme();


// =========================================================
// 🔐 SESSION HANDLING
// =========================================================

document.addEventListener("DOMContentLoaded", () => {

    if(!sessionStorage.getItem("session_initialized")){
        sessionStorage.clear();
        sessionStorage.setItem("session_initialized", "true");
    }

    const authModal = document.getElementById("authModal");
    const dashboard = document.getElementById("dashboard");
    const footer = document.getElementById("footer");

    const loginTab = document.getElementById("loginTab");
    const registerTab = document.getElementById("registerTab");
    const adminNav = document.getElementById("adminNav");

    const login_email = document.getElementById("login_email");
    const login_password = document.getElementById("login_password");
    const loginError = document.getElementById("loginError");

    const analyzeBtn = document.getElementById("analyzeBtn"); // ✅ FIX

    // ✅ FIX: add event listener HERE
    if (analyzeBtn){
        analyzeBtn.addEventListener("click", function(e) {
            analyze(e);
        }); 
    }

    // ENTER key login
    login_email.addEventListener("keypress", function(e) {
      if (e.key === "Enter") login();
    });
    
    login_password.addEventListener("keypress", function(e) {
      if (e.key === "Enter") login();
    });

    const reg_name = document.getElementById("reg_name");
    const reg_email = document.getElementById("reg_email");
    const reg_password = document.getElementById("reg_password");
    const reg_company = document.getElementById("reg_company");
    const reg_department = document.getElementById("reg_department");

    // ENTER key register
    [reg_name, reg_email, reg_password, reg_company, reg_department].forEach(field => {
      field.addEventListener("keypress", function(e){
        if(e.key === "Enter") register();
      });
    });

    const resume_file = document.getElementById("resume_file");
    const job_description = document.getElementById("job_description");
    const results = document.getElementById("results");
    const loading = document.getElementById("loading");

    const userList = document.getElementById("userList");
    const dataViewer = document.getElementById("dataViewer");
    const historyData = document.getElementById("historyData");


    // =========================================================
    // INITIAL LOAD
    // =========================================================

    const userId = sessionStorage.getItem("user_id");

    if (!userId) {

        authModal.style.display = "flex";
        dashboard.style.display = "none";

        if (footer) footer.style.display = "none";

    } else {

        authModal.style.display = "none";
        dashboard.style.display = "flex";

        showPage("analyze");

        if (footer) footer.style.display = "block";

        if (sessionStorage.getItem("role") === "admin") {
            adminNav.style.display = "block";
        }
    }


    // =========================================================
    // TAB SWITCH
    // =========================================================

    window.showTab = function(tab) {

        loginTab.style.display =
            tab === "login" ? "block" : "none";

        registerTab.style.display =
            tab === "register" ? "block" : "none";

        document.querySelectorAll(".tab")
            .forEach(t => t.classList.remove("active"));

        if (tab === "login")
            document.querySelectorAll(".tab")[0].classList.add("active");
        else
            document.querySelectorAll(".tab")[1].classList.add("active");
    };


    // =========================================================
    // REGISTER
    // =========================================================

    window.register = async function() {

        const fd = new FormData();

        fd.append("hr_name", reg_name.value);
        fd.append("email", reg_email.value);
        fd.append("password", reg_password.value);
        fd.append("company_name", reg_company.value);
        fd.append("department", reg_department.value);

        const res = await fetch(
            "http://127.0.0.1:8000/register",
            { method: "POST", body: fd });

        const data = await res.json();

        alert(data.message || data.error);
    };


    // =========================================================
    // LOGIN
    // =========================================================

    window.login = async function(event) {

        if (event) event.preventDefault();

        const email = login_email.value.trim();
        const password = login_password.value.trim();

        if (!email || !password) {
            loginError.innerText = "Email and password are required";
            return;
        }

        const fd = new FormData();
        fd.append("email", email);
        fd.append("password", password);

        try {

            const res = await fetch(
                "http://127.0.0.1:8000/login",
                { method: "POST", body: fd }
            );

            const data = await res.json();

            if (!res.ok || data.error) {
                loginError.innerText = data.error || "Login failed";
                return;
            }

            sessionStorage.setItem("token", data.access_token);
            sessionStorage.setItem("role", data.user.role);
            sessionStorage.setItem("user_id", data.user.id);

            authModal.style.display = "none";
            dashboard.style.display = "flex";

            if (footer) footer.style.display = "block";

            if (data.user.role === "admin")
                adminNav.style.display = "block";

        } catch (err) {

            loginError.innerText = "Server not reachable";
        }
    };


    // =========================================================
    // LOGOUT
    // =========================================================

    window.logout = function() {

        if (!confirm("Are you sure you want to Logout?")) return;

        sessionStorage.clear();

        dashboard.style.display = "none";
        authModal.style.display = "flex";

        if (footer) footer.style.display = "none";
    };

});

    window.showPage = function(page) {
        
        document.querySelectorAll(".page")
            .forEach(p => p.style.display = "none");

        const target = document.getElementById("page-" + page);

        if (target) target.style.display = "block";

        if (page === "history") loadHistory();

        if (page === "employees") loadEmployees();
    };


    // =========================================================
    // ANALYZE RESUMES
    // =========================================================

    async function analyze(event){

    if(event) event.preventDefault();

    const token = sessionStorage.getItem("token");

    if(!token){
        alert("Session Expired. Login again.");
        logout();
        return;
    }

    const fileInput = document.getElementById("resume_file");
    const jd = document.getElementById("job_description").value;
    const topK = document.getElementById("top_k").value;
    const loading = document.getElementById("loading");

    if(!fileInput.files.length){
        alert("Please upload resumes");
        return;
    }

    const formData = new FormData();

    formData.append("file", fileInput.files[0]);
    formData.append("job_description", jd);
    formData.append("top_k", topK);

    loading.style.display = "block";

    try{

        const token = sessionStorage.getItem("token");

        const res = await fetch("http://127.0.0.1:8000/analyze_batch",{
            method:"POST",
            headers:{
                "Authorization": "Bearer " + token
            },
            body:formData
        });

        const data = await res.json();

        loading.style.display="none";

        if(data.error){
            alert(data.error);
            return;
        }

        renderResults(data);

    }
    catch(err){

        loading.style.display="none";

        console.error("Analyze Error:", err);

        alert("Frontend error while rendering results. Check browser console.");
    }
}


    // =========================================================
    // RENDER RESULTS
    // =========================================================
    
    function renderResults(data) {
        
        let html = `
        <h2>Analysis Summary</h2>
        <p><b>Mode:</b> ${data.mode}</p>
        <p><b>Total Resumes:</b> ${data.total_resumes_processed}</p>
        `;
        
        html += "<h2>Top Candidates</h2>";
        
        (data.top_candidates || []).forEach((c, i) => {

            let scoreClass = "score-bad";
            
            if (c.ats_score >= 80) {
                scoreClass = "score-good";
            } else if (c.ats_score >= 60) {
                scoreClass = "score-medium";
            }
            
            const matched = Array.isArray(c.matched_skills)
            ? c.matched_skills.map(s => `<span class="badge-skill">${s}</span>`).join(" ")
            : "";
            
            const missing = Array.isArray(c.missing_skills)
            ? c.missing_skills.map(s => `<span class="badge-missing">${s}</span>`).join(" ")
            : "";
            
            const strengths = c.detailed_explanation?.strengths || [];
            const weaknesses = c.detailed_explanation?.weaknesses || [];
            
            const strengthHTML = strengths.length
            ? strengths.map(s => `<li>${s}</li>`).join("")
            : "<li>-</li>";
            
            const weaknessHTML = weaknesses.length
            ? weaknesses.map(w => `<li>${w}</li>`).join("")
            : "<li>-</li>";
            
            html += `
            <div class="user-card">
            
            <h3>Rank ${i + 1}: ${c.filename || "Unknown"}</h3>

            <button onclick="hireCandidate(${c.resume_id})">
            Hire Candidate
            </button>

            <p><b>Semantic Match:</b> ${c.semantic_match ?? "-"}</p>
            <p><b>Skill Match:</b> ${c.skill_match ?? "-"}</p>
            <p><b>Experience:</b> ${c.experience_years ?? "-"} years</p>

            <p><b>ATS Score:</b>
            <span class="${scoreClass}">
            ${c.ats_score ?? "-"}
            </span>
            </p>

            <p><b>Hiring Probability:</b> ${c.hiring_probability ?? "-"}</p>
            <p><b>Fairness Score:</b> ${c.fairness_adjusted_score ?? "-"}</p>
            <p><b>Confidence:</b> ${c.confidence ?? "-"}</p>
            <p><b>Decision:</b> ${c.decision ?? "-"}</p>

            <p><b>Matched Skills:</b> ${matched || "None"}</p>
            <p><b>Missing Skills:</b> ${missing || "None"}</p>

            <p><b>Overall Assessment:</b> ${c.explanation ?? "-"}</p>

            <p><b>Detailed Assessment:</b> ${c.detailed_explanation?.overall_assessment ?? "-"}</p>

            <p><b>Strengths:</b></p>
            <ul>${strengthHTML}</ul>

            <p><b>Weaknesses:</b></p>
            <ul>${weaknessHTML}</ul>

            <p><b>Recommendation:</b> ${c.detailed_explanation?.recommendation ?? "-"}</p>
            
            </div>
            `;
        });
        
        html += "<h2>All Candidates Ranking</h2>";
        
        (data.all_candidates_ranked || []).forEach((c, i) => {
            html += `
            <p>
            ${i + 1}. ${c.filename}
            — Score: ${c.fairness_adjusted_score}
            — Decision: <b>${c.decision}</b>
            </p>
            `;
        });
        
        const b = data.bias_report || {};
        
        html += `
        <h2>Bias Report</h2>
        <p>Mean Score: ${b.mean_score ?? "-"}</p>
        <p>Std Dev: ${b.std_dev ?? "-"}</p>
        <p>High Outliers: ${b.high_outliers ?? "-"}</p>
        <p>Low Outliers: ${b.low_outliers ?? "-"}</p>
        <p><b>Bias Detected:</b> ${b.bias_detected ?? "-"}</p>
        `;
        
        results.innerHTML = html;
    }

// =========================================================
// HISTORY DATA
// =========================================================

async function loadHistory(){

    const token = sessionStorage.getItem("token");
    
    const res = await fetch("http://127.0.0.1:8000/get_history",{
        method:"POST",
        headers:{
            "Authorization": "Bearer " + token
        }
    });

    const data = await res.json();

    const historyContainer = document.getElementById("historyData");

    historyContainer.innerHTML = "<h3>Previous Sessions</h3>";

    if(!data.history || data.history.length === 0){
        historyContainer.innerHTML += "<p>No history found.</p>";
        return;
    }

    data.history.forEach(h => {

        historyContainer.innerHTML += `
        <div class="user-card">

            <b>Session #${h.session_number}</b><br>
            HR: ${h.hr_name}<br>
            Company: ${h.company_name}<br>
            Resumes: ${h.total_resumes}<br>
            Status: ${h.status}<br>
            Completed: ${h.completed_at}

        </div>
        `;
    });

}

// =========================================================
// ADMIN FUNCTIONS
// =========================================================

window.loadUsers = async function(){

    const token = sessionStorage.getItem("token");
    
    const res = await fetch("http://127.0.0.1:8000/get_company_users",{
        method:"POST",
        headers:{
            "Authorization":"Bearer " + token
        }
    });

    const data = await res.json();

    const userList = document.getElementById("userList");

    if(data.error){
        userList.innerHTML = data.error;
        return;
    }

    userList.innerHTML = "<h3>Company Users</h3>";

    data.users.forEach(u=>{

    const currentUser = sessionStorage.getItem("user_id");

    let buttons = `
        <button onclick="changeRole('${u.email}')">Change Role</button>
        <button onclick="deleteUser('${u.email}')">Delete</button>
    `;

    // 🚫 Prevent admin from modifying themselves
    if(u.id == currentUser){
        buttons = "<small>You (Admin)</small>";
    }

    userList.innerHTML += `
    <div class="user-card">

        <b>${u.name}</b><br>
        ${u.email}<br>
        Department: ${u.department}<br>
        Role: ${u.role}<br>

        <div class="admin-actions">
            ${buttons}
        </div>

    </div>
    `;

});
};


window.viewStoredData = async function(){

    const token = sessionStorage.getItem("token");

    if(!token){
        alert("Session expired. Please login again.");
        logout();
        return;
    }
    
    const res = await fetch("http://127.0.0.1:8000/get_analysis_data",{
        method:"POST",
        headers:{
            "Authorization": "Bearer " + token
        }
    });

    const data = await res.json();

    const viewer = document.getElementById("dataViewer");

    viewer.innerHTML = "<h3>Stored Sessions</h3>";

    if(!data.sessions || data.sessions.length === 0){
        viewer.innerHTML = "<p>No analysis sessions found.</p>";
        return;
    }

    data.sessions.forEach(s=>{

    viewer.innerHTML += `
    <div class="user-card">

        <b>Session ${s.session_number}</b><br>
        Status: ${s.status}<br>
        Resumes: ${s.total_resumes}<br><br>

        <button onclick="viewSession(${s.session_id})">
            View Details
        </button>

    </div>
    `;
});

};


window.clearAnalysisData = async function(){

    if(!confirm("Clear all analysis data?")) return;

    const token = sessionStorage.getItem("token");
    
    const res = await fetch("http://127.0.0.1:8000/clear_analysis_data",{
        method:"POST",
        headers:{
            "Authorization":"Bearer " + token
        }
    });

    const data = await res.json();

    alert(data.message || data.error);

    // refresh stored sessions
    document.getElementById("dataViewer").innerHTML = "";
    document.getElementById("historyData").innerHTML = "";

    loadHistory();
}


async function deleteCompanyData(){

    const confirmText = prompt(
        "⚠️ This will permanently delete ALL company data.\n\nType DELETE to confirm."
    );

    if(confirmText !== "DELETE"){
        alert("Deletion cancelled.");
        return;
    }

    const userId = sessionStorage.getItem("user_id");

    const formData = new FormData();

    const token = sessionStorage.getItem("token");
    
    const res = await fetch(
        "http://127.0.0.1:8000/delete_company_data",
        {
            method:"POST",
            headers:{
                "Authorization":"Bearer " + token
            },
            body:formData
        }
    );

    const data = await res.json();

    alert(data.message || data.error);

    sessionStorage.clear();

    location.reload();

}

// =========================================================
// ADMIN USER MANAGEMENT
// =========================================================

async function changeRole(email){

    const role = prompt("Enter new role (admin/recruiter)");

    if(!role) return;

    const requesterId = sessionStorage.getItem("user_id");

    const fd = new FormData();
    fd.append("target_email", email);
    fd.append("new_role", role);

    const token = sessionStorage.getItem("token");
    
    const res = await fetch(
        "http://127.0.0.1:8000/change_role",
        {
            method:"POST",
            headers:{
                "Authorization":"Bearer " + token
            },
            body:fd
        });

    const data = await res.json();

    alert(data.message || data.error);

    loadUsers();
}


async function deleteUser(email){

    if(!confirm("Delete this user?")) return;

    const requesterId = sessionStorage.getItem("user_id");

    const fd = new FormData();
    fd.append("target_email", email);

    const token = sessionStorage.getItem("token");
    
    const res = await fetch(
        "http://127.0.0.1:8000/delete_user",
        {
            method:"POST",
            headers:{
                "Authorization":"Bearer " + token
            },
            body:fd
        });

    const data = await res.json();

    alert(data.message || data.error);

    loadUsers();
}

async function viewSession(sessionId){

    const fd = new FormData();

    const userId = sessionStorage.getItem("user_id");

    fd.append("session_id", sessionId);
    
    const token = sessionStorage.getItem("token");
    
    const res = await fetch(
        "http://127.0.0.1:8000/get_session_details",
        {
            method:"POST",
            headers:{
                "Authorization":"Bearer " + token
            },
            body:fd
        });

    const data = await res.json();

    const modal = document.getElementById("detailsModal");
    const content = document.getElementById("detailsContent");

    content.innerHTML = `
<div class="details-grid">

  <div>

    <div class="details-section">
      <h3>General</h3>

      <p><b>Session:</b> ${data.session_number}</p>

      <p>
        <b>Status:</b>
        <span class="badge">${data.status}</span>
      </p>

      <p><b>Total Resumes:</b> ${data.total_resumes}</p>
      <p><b>Completed:</b> ${data.completed_at}</p>
    </div>

    <div class="details-section">
      <h3>Job Description</h3>
      <p>${data.job_description || "Not provided"}</p>
    </div>

  </div>

  <div>

    <div class="details-section">
      <h3>Top Candidates</h3>

      ${
        data.top_candidates.map(c => `
          <div class="candidate-card">
            <b>${c.filename}</b><br>
            Score: ${Number(c.score).toFixed(2)}
          </div>
        `).join(" ")
      }

    </div>

    <div class="details-section">
      <h3>Uploaded Files</h3>

      <ul class="file-list">
        ${data.files.map(f => `<li>${f}</li>`).join("")}
      </ul>

    </div>

  </div>

</div>
`;

    modal.style.display = "flex";
}

function closeDetails(){
    document.getElementById("detailsModal").style.display = "none";
}

function toggleAdminPanel(){

    const panel = document.getElementById("dataViewer");

    if(panel.style.display === "block"){
        panel.style.display = "none";
    }else{
        panel.style.display = "block";
        viewStoredData(); // load only when opening
    }
}

window.toggleUserList = function(){

    const userList = document.getElementById("userList");

    // If already visible → hide it
    if(userList.style.display === "block"){
        userList.style.display = "none";
        return;
    }

    // If hidden → show + load users
    userList.style.display = "block";

    loadUsers();
};

async function addEmployee(){

    console.log("Add Employee clicked");  // ✅ DEBUG

    const name = document.getElementById("emp_name").value.trim();
    const email = document.getElementById("emp_email").value.trim();
    const role = document.getElementById("emp_role").value.trim();
    const dept = document.getElementById("emp_department").value.trim();
    const salary = document.getElementById("emp_salary").value.trim();

    const resume = document.getElementById("emp_resume").files[0];

    if(!name || !email || !role || !dept || !salary){
        alert("All fields are required");
        return;
    }

    const fd = new FormData();

    fd.append("name", name);
    fd.append("email", email);
    fd.append("role", role);
    fd.append("department", dept);
    fd.append("salary", salary);

    if(resume){
        fd.append("resume", resume);
    }

    const token = sessionStorage.getItem("token");

    console.log("Sending request...");  // ✅ DEBUG

    try {
        const res = await fetch("http://127.0.0.1:8000/add_employee",{
            method:"POST",
            headers:{ "Authorization": "Bearer " + token },
            body:fd
        });

        const data = await res.json();

        console.log("Response:", data);  // ✅ DEBUG

        if(data.error){
            alert(data.error);
            return;
        }
        
        alert("✅ Employee added successfully");
        
        // ✅ CLEAR ALL INPUTS
        
        document.getElementById("emp_name").value = "";
        document.getElementById("emp_email").value = "";
        document.getElementById("emp_role").value = "";
        document.getElementById("emp_department").value = "";
        document.getElementById("emp_salary").value = "";
        document.getElementById("emp_resume").value = "";  // ⭐ IMPORTANT

        loadEmployees();

    } catch(err){
        console.error("Error:", err);
        alert("Something went wrong");
    }
}

async function loadEmployees(){

    const token = sessionStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/get_employees",{
        method:"POST",
        headers:{ "Authorization": "Bearer " + token }
    });

    const data = await res.json();

    const container = document.getElementById("employeeList");

    if(data.error){
        container.innerHTML = data.error;
        return;
    }

    container.innerHTML = "";

    data.employees.forEach(e => {

        container.innerHTML += `
        <div class="user-card">
            <b>#${e.serial} ${e.name}</b><br>
            Role: ${e.role}<br>
            Dept: ${e.department}<br>
            Salary: ${e.salary}<br><br>

            <button onclick="viewEmployee(${e.id})">View</button>
        </div>
        `;
    });
}

async function viewEmployee(id){

    const fd = new FormData();
    fd.append("employee_id", id);

    const token = sessionStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/employee_details",{
        method:"POST",
        headers:{ "Authorization": "Bearer " + token },
        body:fd
    });

    const data = await res.json();

    const modal = document.getElementById("employeeModal");
    const content = document.getElementById("employeeContent");

    content.innerHTML = "";

    if(data.error){
        alert(data.error);
        return;
    }

    content.innerHTML = `
        
        <button onclick="addPerformance(${id})">Add Performance</button>
        <button onclick="updateSalary(${id})">Update Salary</button>

        <p><b>Name:</b> ${data.name}</p>
        <p><b>Email:</b> ${data.email}</p>
        <p><b>Role:</b> ${data.role}</p>
        <p><b>Department:</b> ${data.department}</p>
        <p><b>Salary:</b> ${data.salary}</p>

        <h3>Performance</h3>
        ${
            data.performance.length
            ? data.performance.map(p => `<p>⭐ ${p.rating} - ${p.feedback}</p>`).join("")
            : "<p>No performance data</p>"
        }

        <h3>Salary History</h3>
        ${
            data.salary_history.length
            ? data.salary_history.map(s => `
                <p>Salary: ₹${s.salary} | Bonus: ₹${s.bonus}</p>`).join("")
            : "<p>No salary history</p>"
        }

        <div class="resume-section">
        <h3>Resume</h3>

        <div style="display:flex; justify-content:center; gap:15px; margin-top:20px;">
        <button onclick="previewResume(${id})">Preview Resume</button>
        <button onclick="downloadResume(${id})">Download Resume</button>
        <button onclick="closeEmployeeModal()">Close</button>
        </div>
    `;

    modal.style.display = "flex";
}

async function addPerformance(id){

    let rating = prompt("Rating (1-5)");
    if (rating === null) return;
    
    rating = parseInt(rating);

    const feedback = prompt("Feedback");
    if(feedback === null || feedback.trim() === ""){
        alert("Feedback is required");
        return;
    }

    if (rating < 1 || rating > 5) {
        alert("Rating must be between 1 and 5");
        return;
    }
    
    if (feedback.length > 300) {
        alert("Feedback too long");
        return;
    }

    const fd = new FormData();
    fd.append("employee_id", id);
    fd.append("rating", rating);
    fd.append("feedback", feedback);

    const token = sessionStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/add_performance",{
        method:"POST",
        headers:{ "Authorization": "Bearer " + token },
        body:fd
    });

    const data = await res.json();

    alert(data.message || data.error);

    // refresh UI
    viewEmployee(id);
}

async function updateSalary(id){

    const salary = prompt("New Salary");
    if(salary === null || salary.trim() === ""){
        alert("Salary required");
        return;
    }

    const bonus = prompt("Bonus (optional)") || 0;

    const fd = new FormData();
    fd.append("employee_id", id);
    fd.append("salary", salary);
    fd.append("bonus", bonus);

    const token = sessionStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/update_salary",{
        method:"POST",
        headers:{ "Authorization": "Bearer " + token },
        body:fd
    });

    const data = await res.json();

    alert(data.message || data.error);

    viewEmployee(id);
}

function closeEmployeeModal(){
    document.getElementById("employeeModal").style.display = "none";
}

let selectedResumeId = null;

function hireCandidate(resume_id){

    selectedResumeId = resume_id;

    // 🔥 CLEAR OLD VALUES
    document.getElementById("hire_role").value = "";
    document.getElementById("hire_department").value = "";
    document.getElementById("hire_salary").value = "";

    document.getElementById("hireModal").style.display = "flex";
}

function closeHireModal(){
    document.getElementById("hireModal").style.display = "none";
}

async function confirmHire(){

    const role = document.getElementById("hire_role").value;
    const dept = document.getElementById("hire_department").value;
    const salary = document.getElementById("hire_salary").value;

    if(!role || !dept || !salary){
        alert("All fields required");
        return;
    }

    const fd = new FormData();
    fd.append("resume_id", selectedResumeId);
    fd.append("role", role);
    fd.append("department", dept);
    fd.append("salary", salary);

    const token = sessionStorage.getItem("token");

    const res = await fetch("http://127.0.0.1:8000/hire_candidate",{
        method:"POST",
        headers:{ "Authorization": "Bearer " + token },
        body:fd
    });

    const data = await res.json();

    alert("✅ Employee added successfully");
    
    // CLEAR FORM
    
    document.getElementById("emp_name").value = "";
    document.getElementById("emp_email").value = "";
    document.getElementById("emp_role").value = "";
    document.getElementById("emp_department").value = "";
    document.getElementById("emp_salary").value = "";

    closeHireModal();
    loadEmployees();
}

function downloadResume(employee_id){

    const token = sessionStorage.getItem("token");

    fetch(`http://127.0.0.1:8000/download_resume/${employee_id}`, {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => {
        if (!res.ok) throw new Error("Download failed");

        return res.blob().then(blob => ({
            blob: blob,
            headers: res.headers
        }));
    })
    .then(data => {
        const link = document.createElement("a");

        link.href = window.URL.createObjectURL(data.blob);
        
        const disposition = data.headers.get("Content-Disposition");
        
        let filename = "resume";
        
        if (disposition && disposition.includes("filename=")) {
            filename = disposition.split("filename=")[1].replace(/"/g, "");
        }
        
        link.download = filename;

        document.body.appendChild(link);
        link.click();
        link.remove();
    })
    
    .catch(err => {
        alert("Download failed");
        console.error(err);
    });
}

function previewResume(employee_id){

    const modal = document.getElementById("previewModal");
    const frame = document.getElementById("resumeFrame");

    // ✅ set URL
    frame.src = `http://127.0.0.1:8000/preview_resume/${employee_id}`;

    modal.style.display = "flex";
}

function closePreview(){
    const modal = document.getElementById("previewModal");
    const frame = document.getElementById("resumeFrame");

    frame.src = ""; // clear
    modal.style.display = "none";
}