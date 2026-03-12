// Form Data State
let formData = {
    sectionA: { country: '', companyName: '', plantLocation: '' },
    sectionB: { name: '', designation: '', contact: '', email: '' },
    sectionC: {
        products: [],
        fillPac: { units: '', oeeUnits: '', spouts: '', installationDate: '', services: [] },
        bucketElevator: {
            units: '',
            conditionMonitoringUnits: '',
            type: '',
            installationDate: '',
            workingEfficiently: '',
            beltSlippage: '',
            maintenanceCost: '',
            services: [],
            suggestions: ''
        }
    },
    sectionD_FillPac: {
        oeeAccurate: '',
        perfAccurate: '',
        qualAccurate: '',
        availAccurate: '',
        bagsMatch: '',
        dataFreq: '',
        bottlenecks: '',
        usefulMetric: '',
        missingFeatures: '',
        visualizations: '',
        faultInfo: '',
        bagInfo: '',
        comments: '',
        userFriendly: ''
    },
    sectionD_BucketElevator: {
        understanding: '',
        effectiveness: '',
        trainingSatisfaction: '',
        userFriendly: '',
        usageFreq: '',
        reducedBreakdowns: '',
        supportRating: '',
        suggestions: ''
    }
};

let isEmailVerified = false;
let currentPage = 0;
const totalPages = 7;

// Custom Dropdown Class
class CustomDropdown {
    constructor(elementId, options, placeholder, onChange, searchable = false) {
        this.container = document.getElementById(elementId);
        this.options = options;
        this.placeholder = placeholder;
        this.onChange = onChange;
        this.searchable = searchable;
        this.isOpen = false;
        this.selectedValue = '';
        this.filteredOptions = options;

        this.init();
    }

    init() {
        this.container.innerHTML = `
            <div class="dropdown-header">
                <span class="selected-text placeholder">${this.placeholder}</span>
                <span class="arrow">▼</span>
            </div>
            <div class="dropdown-list-container">
                ${this.searchable ? `
                    <div class="dropdown-search">
                        <input type="text" placeholder="Search...">
                    </div>
                ` : ''}
                <ul class="dropdown-list">
                    ${this.renderOptions(this.options)}
                </ul>
            </div>
        `;

        this.header = this.container.querySelector('.dropdown-header');
        this.listContainer = this.container.querySelector('.dropdown-list-container');
        this.list = this.container.querySelector('.dropdown-list');
        this.selectedText = this.container.querySelector('.selected-text');

        this.header.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });

        if (this.searchable) {
            this.searchInput = this.container.querySelector('.dropdown-search input');
            this.searchInput.addEventListener('click', (e) => e.stopPropagation());
            this.searchInput.addEventListener('input', (e) => this.filter(e.target.value));
        }

        document.addEventListener('click', () => this.close());
    }

    renderOptions(options) {
        if (options.length === 0) return '<li class="dropdown-no-results">No results found</li>';
        return options.map(opt => `
            <li class="dropdown-item ${opt === this.selectedValue ? 'selected' : ''}" data-value="${opt}">
                ${opt}
            </li>
        `).join('');
    }

    toggle() {
        this.isOpen ? this.close() : this.open();
    }

    open() {
        // Close other dropdowns
        document.querySelectorAll('.custom-dropdown').forEach(d => {
            if (d !== this.container) d.classList.remove('open');
        });

        this.isOpen = true;
        this.container.classList.add('open');
        if (this.searchable) {
            setTimeout(() => this.searchInput.focus(), 100);
        }
    }

    close() {
        this.isOpen = false;
        this.container.classList.remove('open');
    }

    filter(query) {
        this.filteredOptions = this.options.filter(opt =>
            opt.toLowerCase().includes(query.toLowerCase())
        );
        this.list.innerHTML = this.renderOptions(this.filteredOptions);
        this.attachItemListeners();
    }

    attachItemListeners() {
        this.list.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                this.select(item.dataset.value);
            });
        });
    }

    select(value) {
        this.selectedValue = value;
        this.selectedText.innerText = value;
        this.selectedText.classList.remove('placeholder');
        this.onChange(value);
        this.close();
        this.container.classList.remove('error');
    }

    setError(isError) {
        if (isError) this.container.classList.add('error');
        else this.container.classList.remove('error');
    }
}

// Initialize Dropdowns
const countries = ['India', 'Germany', 'USA', 'Japan', 'France', 'UK', 'China', 'Brazil'];
const designations = ['Manager', 'Engineer', 'Operator', 'Technician', 'Analyst', 'Director'];

let dropdowns = {};

window.onload = () => {
    dropdowns.country = new CustomDropdown('dropdown-country', countries, 'Select Country', (val) => {
        formData.sectionA.country = val;
    }, true);

    dropdowns.designation = new CustomDropdown('dropdown-designation', designations, 'Select Designation', (val) => {
        formData.sectionB.designation = val;
    });

    dropdowns.fpUnits = new CustomDropdown('dropdown-fpUnits', ['1', '2', '3', '4', '5+'], 'Select', (val) => {
        formData.sectionC.fillPac.units = val;
    });

    dropdowns.fpOeeUnits = new CustomDropdown('dropdown-fpOeeUnits', ['1', '2', '3', '4', '5+'], 'Select', (val) => {
        formData.sectionC.fillPac.oeeUnits = val;
    });

    dropdowns.fpSpouts = new CustomDropdown('dropdown-fpSpouts', ['8', '12', '16', '24'], 'Select', (val) => {
        formData.sectionC.fillPac.spouts = val;
    });

    dropdowns.beUnits = new CustomDropdown('dropdown-beUnits', ['1', '2', '3+'], 'Select', (val) => {
        formData.sectionC.bucketElevator.units = val;
    });

    dropdowns.beMonitoring = new CustomDropdown('dropdown-beMonitoring', ['1', '2', '3+'], 'Select', (val) => {
        formData.sectionC.bucketElevator.conditionMonitoringUnits = val;
    });

    Object.values(dropdowns).forEach(d => d.attachItemListeners());

    renderNavDots();
};

// Navigation Logic
function renderNavDots() {
    const navDots = document.getElementById('navDots');
    navDots.innerHTML = Array.from({ length: totalPages }).map((_, i) => {
        const isApplicable = isPageApplicable(i);
        return `
            <div class="dot ${currentPage === i ? 'active' : ''} ${i > currentPage || !isApplicable ? 'disabled' : ''}" 
                 onclick="handleDotClick(${i})"></div>
        `;
    }).join('');
}

function handleDotClick(index) {
    if (index <= currentPage && isPageApplicable(index)) {
        goToPage(index);
    }
}

function goToPage(index) {
    if (index === currentPage) return;

    // Remove active from current
    document.getElementById(`page${currentPage}`).classList.remove('active');

    currentPage = index;

    // Add active to new
    document.getElementById(`page${currentPage}`).classList.add('active');

    renderNavDots();
    updateButtonText();
}

function isPageApplicable(index) {
    if (index === 4) return formData.sectionC.products.includes('FillPac');
    if (index === 5) return formData.sectionC.products.includes('BucketElevator');
    return true;
}

function updateButtonText() {
    const nextBtn = document.querySelector(`#page${currentPage} .btn:not(.btn-secondary)`);
    if (!nextBtn || nextBtn.innerText === 'Start Feedback') return;

    let next = currentPage + 1;
    while (next < totalPages - 1 && !isPageApplicable(next)) {
        next++;
    }

    if (next === totalPages - 1) {
        nextBtn.innerText = 'Submit Feedback';
    } else {
        nextBtn.innerText = 'Next';
    }
}

function nextPage() {
    if (!validatePage()) return;

    let next = currentPage + 1;
    while (next < totalPages - 1 && !isPageApplicable(next)) {
        next++;
    }

    if (next === totalPages - 1) {
        submitForm();
    } else if (next < totalPages) {
        goToPage(next);
    }
}

function prevPage() {
    let prev = currentPage - 1;
    while (prev > 0 && !isPageApplicable(prev)) {
        prev--;
    }

    if (prev >= 0) {
        goToPage(prev);
    }
}

// Validation Logic
function validatePage() {
    clearErrors();
    let isValid = true;

    if (currentPage === 1) { // Section A
        if (!formData.sectionA.country) { dropdowns.country.setError(true); isValid = false; }
        const companyName = document.getElementById('companyName');
        if (!companyName.value) { companyName.classList.add('error'); isValid = false; }
        const plantLocation = document.getElementById('plantLocation');
        if (!plantLocation.value) { plantLocation.classList.add('error'); isValid = false; }

        formData.sectionA.companyName = companyName.value;
        formData.sectionA.plantLocation = plantLocation.value;

    } else if (currentPage === 2) { // Section B
        const name = document.getElementById('name');
        if (!name.value) { name.classList.add('error'); isValid = false; }

        if (!formData.sectionB.designation) {
            dropdowns.designation.setError(true);
            isValid = false;
        }

        const email = document.getElementById('email');
        if (!email.value) { email.classList.add('error'); isValid = false; }

        if (!isEmailVerified) {
            document.getElementById('otpStatus').innerText = 'Please verify your email to proceed';
            document.getElementById('otpStatus').className = 'otp-status error';
            isValid = false;
        }

        formData.sectionB.name = name.value;
        formData.sectionB.contact = document.getElementById('contact').value; // Optional
        formData.sectionB.email = email.value;

    } else if (currentPage === 3) { // Section C
        const products = Array.from(document.querySelectorAll('input[name="product"]:checked')).map(cb => cb.value);
        if (products.length === 0) {
            document.getElementById('product-selection').style.border = '1px solid var(--accent-color)';
            isValid = false;
        }
        formData.sectionC.products = products;

        if (products.includes('FillPac')) {
            if (!formData.sectionC.fillPac.units) { dropdowns.fpUnits.setError(true); isValid = false; }
            if (!formData.sectionC.fillPac.oeeUnits) { dropdowns.fpOeeUnits.setError(true); isValid = false; }
            if (!formData.sectionC.fillPac.spouts) { dropdowns.fpSpouts.setError(true); isValid = false; }
            const fpDate = document.getElementById('fpDate');
            if (!fpDate.value) { fpDate.classList.add('error'); isValid = false; }
            formData.sectionC.fillPac.installationDate = fpDate.value;
            formData.sectionC.fillPac.services = Array.from(document.querySelectorAll('#fpServices input:checked')).map(cb => cb.value);
        }

        if (products.includes('BucketElevator')) {
            if (!formData.sectionC.bucketElevator.units) { dropdowns.beUnits.setError(true); isValid = false; }
            if (!formData.sectionC.bucketElevator.conditionMonitoringUnits) { dropdowns.beMonitoring.setError(true); isValid = false; }
            const beType = document.getElementById('beType');
            if (!beType.value) { beType.classList.add('error'); isValid = false; }
            const beDate = document.getElementById('beDate');
            if (!beDate.value) { beDate.classList.add('error'); isValid = false; }
            const beEfficient = document.getElementById('beEfficient');
            if (!beEfficient.value) { beEfficient.classList.add('error'); isValid = false; }
            const beSlippage = document.getElementById('beSlippage');
            if (!beSlippage.value) { beSlippage.classList.add('error'); isValid = false; }
            const beCost = document.getElementById('beCost');
            if (!beCost.value) { beCost.classList.add('error'); isValid = false; }

            formData.sectionC.bucketElevator.type = beType.value;
            formData.sectionC.bucketElevator.installationDate = beDate.value;
            formData.sectionC.bucketElevator.workingEfficiently = beEfficient.value;
            formData.sectionC.bucketElevator.beltSlippage = beSlippage.value;
            formData.sectionC.bucketElevator.maintenanceCost = beCost.value;
            formData.sectionC.bucketElevator.services = Array.from(document.querySelectorAll('#beServices input:checked')).map(cb => cb.value);
            
            // beSuggestions does not exist on Page 3 HTML, moving it to Page 6 if needed 
            // but for now removing the null reference that breaks navigation.
        }
    } else if (currentPage === 4) { // Section D - FillPac Feedback
        const radioFields = [
            { name: 'fp_oee_accurate', key: 'oeeAccurate' },
            { name: 'fp_perf_accurate', key: 'perfAccurate' },
            { name: 'fp_qual_accurate', key: 'qualAccurate' },
            { name: 'fp_avail_accurate', key: 'availAccurate' },
            { name: 'fp_bags_match', key: 'bagsMatch' },
            { name: 'fp_data_freq', key: 'dataFreq' },
            { name: 'fp_bottlenecks', key: 'bottlenecks' },
            { name: 'fp_useful_metric', key: 'usefulMetric' },
            { name: 'fp_missing_features', key: 'missingFeatures' },
            { name: 'fp_fault_info', key: 'faultInfo' },
            { name: 'fp_bag_info', key: 'bagInfo' },
            { name: 'fp_user_friendly', key: 'userFriendly' }
        ];

        radioFields.forEach(field => {
            const selected = document.querySelector(`input[name="${field.name}"]:checked`);
            if (!selected) {
                const firstInput = document.querySelector(`input[name="${field.name}"]`);
                if (firstInput) firstInput.closest('.input-group').classList.add('error');
                isValid = false;
            } else {
                formData.sectionD_FillPac[field.key] = selected.value;
            }
        });

        formData.sectionD_FillPac.visualizations = document.getElementById('fpVisualizations').value;
        formData.sectionD_FillPac.comments = document.getElementById('fpComments').value;

    } else if (currentPage === 5) { // Section D - Bucket Elevator Feedback
        const beRadioFields = [
            { name: 'be_understanding', key: 'understanding' },
            { name: 'be_effectiveness', key: 'effectiveness' },
            { name: 'be_training_satisfaction', key: 'trainingSatisfaction' },
            { name: 'be_user_friendly', key: 'userFriendly' },
            { name: 'be_usage_freq', key: 'usageFreq' },
            { name: 'be_reduced_breakdowns', key: 'reducedBreakdowns' },
            { name: 'be_support_rating', key: 'supportRating' }
        ];

        beRadioFields.forEach(field => {
            const selected = document.querySelector(`input[name="${field.name}"]:checked`);
            if (!selected) {
                const firstInput = document.querySelector(`input[name="${field.name}"]`);
                if (firstInput) firstInput.closest('.input-group').classList.add('error');
                isValid = false;
            } else {
                formData.sectionD_BucketElevator[field.key] = selected.value;
            }
        });

        formData.sectionD_BucketElevator.suggestions = document.getElementById('beSuggestionsCM').value;
    }

    return isValid;
}

function clearErrors() {
    document.querySelectorAll('.error').forEach(el => el.classList.remove('error'));
    document.querySelectorAll('.custom-dropdown').forEach(d => d.classList.remove('error'));
    document.getElementById('product-selection').style.border = 'none';
    if (document.getElementById('otpStatus')) {
        document.getElementById('otpStatus').innerText = '';
        document.getElementById('otpStatus').className = 'otp-status';
    }
}

// ── OTP Logic ──────────────────────────────────────────────────────────────
async function send_otp_request(email) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout

    try {
        const response = await fetch('/api/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return { ok: response.ok, status: response.status, data: await response.json() };
    } catch (err) {
        clearTimeout(timeoutId);
        if (err.name === 'AbortError') {
            throw new Error('Request timed out. Please check your internet connection.');
        }
        throw err;
    }
}

async function sendOtp() {
    const email = document.getElementById('email').value;
    if (!email || !email.includes('@')) {
        alert('Please enter a valid email address');
        return;
    }

    const btn = document.getElementById('sendOtpBtn');
    const otpStatus = document.getElementById('otpStatus');
    
    btn.disabled = true;
    btn.innerText = 'Sending...';
    otpStatus.innerText = 'Attempting to send code...';
    otpStatus.className = 'otp-status';

    try {
        const result = await send_otp_request(email);
        
        if (result.ok) {
            document.getElementById('otpGroup').style.display = 'block';
            otpStatus.innerText = 'OTP sent successfully! Please check your inbox.';
            otpStatus.className = 'otp-status success';
            btn.innerText = 'Resend OTP';
        } else {
            const errorMsg = result.data.detail || 'Service unavailable';
            otpStatus.innerText = `Error: ${errorMsg}`;
            otpStatus.className = 'otp-status error';
            btn.innerText = 'Retry Sending';
            console.error('OTP Error:', result.data);
        }
    } catch (err) {
        console.error('OTP Fetch Failure:', err);
        otpStatus.innerText = `Network Error: ${err.message || 'Check connection'}`;
        otpStatus.className = 'otp-status error';
        btn.innerText = 'Send OTP';
    } finally {
        btn.disabled = false;
    }
}

async function verifyOtp() {
    const email = document.getElementById('email').value;
    const otp = document.getElementById('otpInput').value;
    if (otp.length !== 6) {
        alert('Please enter a 6-digit OTP');
        return;
    }

    const btn = document.getElementById('verifyOtpBtn');
    btn.disabled = true;
    btn.innerText = 'Verifying...';

    try {
        const response = await fetch('/api/verify-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp })
        });
        const data = await response.json();
        if (response.ok) {
            isEmailVerified = true;
            document.getElementById('otpGroup').innerHTML = `
                <div class="verified-badge">
                    <span>✅ Email Verified</span>
                </div>
            `;
            
            // Store JWT token for subsequent requests
            if (data.access_token) {
                localStorage.setItem('feedback_token', data.access_token);
            }
            
            document.getElementById('email').disabled = true;
            document.getElementById('sendOtpBtn').style.display = 'none';
            document.getElementById('otpStatus').innerText = 'Verification successful! Moving to next page...';
            document.getElementById('otpStatus').className = 'otp-status success';

            // Auto-advance after a brief delay
            setTimeout(() => {
                nextPage();
            }, 1000);
        } else {
            const errorMsg = data.detail || 'Invalid OTP. Please try again.';
            document.getElementById('otpStatus').innerText = errorMsg;
            document.getElementById('otpStatus').className = 'otp-status error';
        }
    } catch (err) {
        console.error('OTP Verification Error:', err);
        const statusEl = document.getElementById('otpStatus');
        if (statusEl) {
            statusEl.innerText = 'Network error or server is down. Please try again.';
            statusEl.className = 'otp-status error';
        }
        alert('Error connecting to verification service. Please check your connection.');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Verify';
    }
}

function resetEmailVerification() {
    isEmailVerified = false;
    document.getElementById('otpGroup').style.display = 'none';
    document.getElementById('otpStatus').innerText = '';
}

// Section C Logic
function toggleProductDetails() {
    const products = Array.from(document.querySelectorAll('input[name="product"]:checked')).map(cb => cb.value);
    formData.sectionC.products = products; // Update state immediately for logic
    document.getElementById('fillPacDetails').style.display = products.includes('FillPac') ? 'block' : 'none';
    document.getElementById('beDetails').style.display = products.includes('BucketElevator') ? 'block' : 'none';
    renderNavDots(); // Update dots as applicability changed
    updateButtonText(); // Update Next/Submit label based on selected products
}

// Submit Logic
async function submitForm() {
    try {
        const token = localStorage.getItem('feedback_token');
        const headers = { 'Content-Type': 'application/json' };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch('/api/submit-feedback', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
            alert('Your session has expired. Please verify your email again.');
            goToPage(2); // Go back to contact details page
            return;
        }

        if (data.status === 'success') {
            goToPage(6); // Success page
        }
    } catch (error) {
        console.error('Error submitting form:', error);
        alert('Failed to submit. Is the backend running?');
    }
}
