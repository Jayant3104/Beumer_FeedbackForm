import re

FILE_PATH = r"j:\Beumer_FeedbackForm\static\script.js"

with open(FILE_PATH, "r", encoding="utf-8") as f:
    js_code = f.read()

# 1. Update State
js_code = re.sub(
    r"sectionD_FillPac: \{[^}]+\},",
    "sectionD_FillPac: [],",
    js_code, flags=re.DOTALL
)

js_code = re.sub(
    r"sectionD_BucketElevator: \{[^}]+\}",
    "sectionD_BucketElevator: []",
    js_code, flags=re.DOTALL
)

# 2. Add pageFlow variables
js_code = js_code.replace(
    "let currentPage = 0;\nconst totalPages = 7;",
    "let pageFlow = ['page0', 'page1', 'page2', 'page3', 'pageSuccess'];\nlet currentPageIndex = 0;"
)

# 3. Remove Dropdown initialization for Units
js_code = re.sub(r"dropdowns\.fpUnits = new CustomDropdown.*?\}\);\n", "", js_code, flags=re.DOTALL)
js_code = re.sub(r"dropdowns\.beUnits = new CustomDropdown.*?\}\);\n", "", js_code, flags=re.DOTALL)

# 4. Update renderNavDots
js_code = re.sub(
    r"function renderNavDots\(\) \{.*?\}",
    """function renderNavDots() {
    const navDots = document.getElementById('navDots');
    navDots.innerHTML = pageFlow.map((pageId, i) => {
        return `
            <div class="dot ${currentPageIndex === i ? 'active' : ''} ${i > currentPageIndex ? 'disabled' : ''}" 
                 onclick="handleDotClick(${i})"></div>
        `;
    }).join('');
}""",
    js_code, count=1, flags=re.DOTALL
)

# 5. Update Navigation Logic
nav_funcs = """
function handleDotClick(index) {
    if (index <= currentPageIndex) {
        goToPage(index);
    }
}

function goToPage(index) {
    if (index === currentPageIndex) return;
    document.getElementById(pageFlow[currentPageIndex]).classList.remove('active');
    currentPageIndex = index;
    document.getElementById(pageFlow[currentPageIndex]).classList.add('active');
    renderNavDots();
    updateButtonText();
}

function updateButtonText() {
    const nextBtn = document.querySelector(`#${pageFlow[currentPageIndex]} .btn:not(.btn-secondary)`);
    if (!nextBtn || nextBtn.innerText === 'Start Feedback') return;

    if (currentPageIndex === pageFlow.length - 2) {
        nextBtn.innerText = 'Submit Feedback';
    } else {
        nextBtn.innerText = 'Next';
    }
}

function nextPage() {
    if (!validatePage()) return;
    if (currentPageIndex === 3) {
        setupDynamicPages();
    }
    if (currentPageIndex === pageFlow.length - 2) {
        submitForm();
    } else if (currentPageIndex < pageFlow.length - 1) {
        goToPage(currentPageIndex + 1);
    }
}

function prevPage() {
    if (currentPageIndex > 0) {
        goToPage(currentPageIndex - 1);
    }
}
"""
js_code = re.sub(
    r"function handleDotClick\(index\).*?function validatePage\(\)",
    nav_funcs + "\n// Validation Logic\function validatePage()",
    js_code, flags=re.DOTALL
)
js_code = js_code.replace("function validatePage()", "function validatePage()")

# 6. Update Validation Logic (replace the whole validatePage function)
validate_new = """function validatePage() {
    clearErrors();
    let isValid = true;

    if (currentPageIndex === 1) { // Section A
        if (!formData.sectionA.country) { dropdowns.country.setError(true); isValid = false; }
        const companyName = document.getElementById('companyName');
        if (!companyName.value) { companyName.classList.add('error'); isValid = false; }
        const plantLocation = document.getElementById('plantLocation');
        if (!plantLocation.value) { plantLocation.classList.add('error'); isValid = false; }

        formData.sectionA.companyName = companyName.value;
        formData.sectionA.plantLocation = plantLocation.value;

    } else if (currentPageIndex === 2) { // Section B
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

    } else if (currentPageIndex === 3) { // Section C
        const products = Array.from(document.querySelectorAll('input[name="product"]:checked')).map(cb => cb.value);
        if (products.length === 0) {
            document.getElementById('product-selection').style.border = '1px solid var(--accent-color)';
            isValid = false;
        }
        formData.sectionC.products = products;

        if (products.includes('FillPac')) {
            const fpUnitsInput = document.getElementById('fpUnits');
            if (!fpUnitsInput.value || fpUnitsInput.value < 1) { fpUnitsInput.classList.add('error'); isValid = false; }
            else { formData.sectionC.fillPac.units = parseInt(fpUnitsInput.value, 10); }

            if (!formData.sectionC.fillPac.oeeUnits) { dropdowns.fpOeeUnits.setError(true); isValid = false; }
            if (!formData.sectionC.fillPac.spouts) { dropdowns.fpSpouts.setError(true); isValid = false; }
            const fpDate = document.getElementById('fpDate');
            if (!fpDate.value) { fpDate.classList.add('error'); isValid = false; }
            formData.sectionC.fillPac.installationDate = fpDate.value;
            formData.sectionC.fillPac.services = Array.from(document.querySelectorAll('#fpServices input:checked')).map(cb => cb.value);
        }

        if (products.includes('BucketElevator')) {
            const beUnitsInput = document.getElementById('beUnits');
            if (!beUnitsInput.value || beUnitsInput.value < 1) { beUnitsInput.classList.add('error'); isValid = false; }
            else { formData.sectionC.bucketElevator.units = parseInt(beUnitsInput.value, 10); }

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
        }
    } else if (pageFlow[currentPageIndex].startsWith('page_fp_')) {
        const unitNum = parseInt(pageFlow[currentPageIndex].split('_')[2], 10);
        const radioFields = [
            { name: `fp_oee_accurate_${unitNum}`, key: 'oeeAccurate' },
            { name: `fp_perf_accurate_${unitNum}`, key: 'perfAccurate' },
            { name: `fp_qual_accurate_${unitNum}`, key: 'qualAccurate' },
            { name: `fp_avail_accurate_${unitNum}`, key: 'availAccurate' },
            { name: `fp_bags_match_${unitNum}`, key: 'bagsMatch' },
            { name: `fp_data_freq_${unitNum}`, key: 'dataFreq' },
            { name: `fp_bottlenecks_${unitNum}`, key: 'bottlenecks' },
            { name: `fp_useful_metric_${unitNum}`, key: 'usefulMetric' },
            { name: `fp_missing_features_${unitNum}`, key: 'missingFeatures' },
            { name: `fp_fault_info_${unitNum}`, key: 'faultInfo' },
            { name: `fp_bag_info_${unitNum}`, key: 'bagInfo' },
            { name: `fp_user_friendly_${unitNum}`, key: 'userFriendly' }
        ];

        radioFields.forEach(field => {
            const selected = document.querySelector(`input[name="${field.name}"]:checked`);
            if (!selected) {
                const firstInput = document.querySelector(`input[name="${field.name}"]`);
                if (firstInput) firstInput.closest('.input-group').classList.add('error');
                isValid = false;
            } else {
                formData.sectionD_FillPac[unitNum - 1][field.key] = selected.value;
            }
        });

        formData.sectionD_FillPac[unitNum - 1].visualizations = document.getElementById(`fpVisualizations_${unitNum}`).value;
        formData.sectionD_FillPac[unitNum - 1].comments = document.getElementById(`fpComments_${unitNum}`).value;

    } else if (pageFlow[currentPageIndex].startsWith('page_be_')) {
        const unitNum = parseInt(pageFlow[currentPageIndex].split('_')[2], 10);
        const beRadioFields = [
            { name: `be_understanding_${unitNum}`, key: 'understanding' },
            { name: `be_effectiveness_${unitNum}`, key: 'effectiveness' },
            { name: `be_training_satisfaction_${unitNum}`, key: 'trainingSatisfaction' },
            { name: `be_user_friendly_${unitNum}`, key: 'userFriendly' },
            { name: `be_usage_freq_${unitNum}`, key: 'usageFreq' },
            { name: `be_reduced_breakdowns_${unitNum}`, key: 'reducedBreakdowns' },
            { name: `be_support_rating_${unitNum}`, key: 'supportRating' }
        ];

        beRadioFields.forEach(field => {
            const selected = document.querySelector(`input[name="${field.name}"]:checked`);
            if (!selected) {
                const firstInput = document.querySelector(`input[name="${field.name}"]`);
                if (firstInput) firstInput.closest('.input-group').classList.add('error');
                isValid = false;
            } else {
                formData.sectionD_BucketElevator[unitNum - 1][field.key] = selected.value;
            }
        });

        formData.sectionD_BucketElevator[unitNum - 1].suggestions = document.getElementById(`beSuggestionsCM_${unitNum}`).value;
    }

    return isValid;
}
"""
js_code = re.sub(
    r"function validatePage\(\) \{.*?\}\n\nfunction clearErrors\(\)",
    validate_new + "\n\nfunction clearErrors()",
    js_code, flags=re.DOTALL
)

# 7. Inject the setupDynamicPages and template generators before toggleProductDetails
html_gen_funcs = """
function setupDynamicPages() {
    const container = document.getElementById('dynamicFeedbackPages');
    container.innerHTML = '';
    
    // reset flow
    pageFlow = ['page0', 'page1', 'page2', 'page3'];
    
    formData.sectionD_FillPac = [];
    if (formData.sectionC.products.includes('FillPac')) {
        const fpUnits = formData.sectionC.fillPac.units;
        for (let i = 1; i <= fpUnits; i++) {
            const pageId = `page_fp_${i}`;
            pageFlow.push(pageId);
            container.innerHTML += createFillPacFeedbackHTML(i, pageId);
            formData.sectionD_FillPac.push({});
        }
    }
    
    formData.sectionD_BucketElevator = [];
    if (formData.sectionC.products.includes('BucketElevator')) {
        const beUnits = formData.sectionC.bucketElevator.units;
        for (let i = 1; i <= beUnits; i++) {
            const pageId = `page_be_${i}`;
            pageFlow.push(pageId);
            container.innerHTML += createBucketElevatorFeedbackHTML(i, pageId);
            formData.sectionD_BucketElevator.push({});
        }
    }
    
    pageFlow.push('pageSuccess');
    renderNavDots();
}

function createFillPacFeedbackHTML(unitNum, pageId) {
    return `
        <div class="page" id="${pageId}">
            <div class="header">
                <h1>FillPac Feedback</h1>
                <p>Section D (Unit ${unitNum})</p>
            </div>

            <div class="feedback-grid">
                <div class="form-group">
                    <label>Is OEE data accurate?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_oee_accurate_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_oee_accurate_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Is Performance data accurate?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_perf_accurate_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_perf_accurate_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Is Quality data accurate?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_qual_accurate_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_qual_accurate_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Is Availability data accurate?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_avail_accurate_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_avail_accurate_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Do no. of bags match with Physical stock?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_bags_match_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_bags_match_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Frequency of data generation</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_data_freq_${unitNum}" value="Real-time"> Real-time</label>
                        <label><input type="radio" name="fp_data_freq_${unitNum}" value="Daily"> Daily</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Helps in identifying bottlenecks?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_bottlenecks_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_bottlenecks_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Is any other metric useful for you?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_useful_metric_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_useful_metric_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Missing features in dashboard?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_missing_features_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_missing_features_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Are fault information alerts useful?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_fault_info_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_fault_info_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Is Average bag weight info useful?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_bag_info_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_bag_info_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Is the dashboard user-friendly?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="fp_user_friendly_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="fp_user_friendly_${unitNum}" value="No"> No</label>
                    </div>
                </div>
            </div>

            <div class="form-group full-width">
                <label>Suggestion for better visualizations</label>
                <textarea id="fpVisualizations_${unitNum}" rows="3" placeholder="Tell us more..."></textarea>
            </div>
            <div class="form-group full-width">
                <label>Overall comments / suggestions</label>
                <textarea id="fpComments_${unitNum}" rows="3" placeholder="Any additional feedback..."></textarea>
            </div>

            <div class="btn-group">
                <button class="btn btn-secondary" type="button" onclick="prevPage()">Back</button>
                <button class="btn" type="button" onclick="nextPage()">Next</button>
            </div>
        </div>
    `;
}

function createBucketElevatorFeedbackHTML(unitNum, pageId) {
    return `
        <div class="page" id="${pageId}">
            <div class="header">
                <h1>Bucket Elevator Monitoring</h1>
                <p>Section D feedback (Unit ${unitNum})</p>
            </div>

            <div class="feedback-grid">
                <div class="form-group">
                    <label>Did you understand the displayed monitoring data?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="be_understanding_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="be_understanding_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Effectiveness for predictive maintenance?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="be_effectiveness_${unitNum}" value="High"> High</label>
                        <label><input type="radio" name="be_effectiveness_${unitNum}" value="Medium"> Medium</label>
                        <label><input type="radio" name="be_effectiveness_${unitNum}" value="Low"> Low</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Are you satisfied with the training provided?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="be_training_satisfaction_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="be_training_satisfaction_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Is the dashboard user-friendly?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="be_user_friendly_${unitNum}" value="Yes"> Yes</label>
                        <label><input type="radio" name="be_user_friendly_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Frequency of dashboard usage</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="be_usage_freq_${unitNum}" value="Daily"> Daily</label>
                        <label><input type="radio" name="be_usage_freq_${unitNum}" value="Weekly"> Weekly</label>
                        <label><input type="radio" name="be_usage_freq_${unitNum}" value="Rarely"> Rarely</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Did the system help reduce breakdowns?</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="be_reduced_breakdowns_${unitNum}" value="Significant"> Significant</label>
                        <label><input type="radio" name="be_reduced_breakdowns_${unitNum}" value="Slightly"> Slightly</label>
                        <label><input type="radio" name="be_reduced_breakdowns_${unitNum}" value="No"> No</label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Rating for technical support</label>
                    <div class="radio-group input-group">
                        <label><input type="radio" name="be_support_rating_${unitNum}" value="5"> ⭐⭐⭐⭐⭐</label>
                        <label><input type="radio" name="be_support_rating_${unitNum}" value="4"> ⭐⭐⭐⭐</label>
                        <label><input type="radio" name="be_support_rating_${unitNum}" value="3"> ⭐⭐⭐</label>
                    </div>
                </div>
            </div>

            <div class="form-group full-width">
                <label>Suggestions for improvements in Section D</label>
                <textarea id="beSuggestionsCM_${unitNum}" rows="3" placeholder="Tell us more..."></textarea>
            </div>

            <div class="btn-group">
                <button class="btn btn-secondary" type="button" onclick="prevPage()">Back</button>
                <button class="btn" type="button" onclick="nextPage()">Submit/Next</button>
            </div>
        </div>
    `;
}

// Section C Logic
"""

js_code = js_code.replace("// Section C Logic\n", html_gen_funcs)

# Update submitForm to use pageSuccess correctly, actually we just need to use indexOf('pageSuccess')
js_code = js_code.replace("goToPage(6);", "goToPage(pageFlow.indexOf('pageSuccess'));")

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(js_code)

print("success!")
