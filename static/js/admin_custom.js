document.addEventListener('DOMContentLoaded', function () {
    console.log(' JS Loaded from admin_custom.js');

    const batchSelect = document.querySelector('select[name="batch"]');
    const branchSelect = document.querySelector('select[name="branch"]');
    const yearSelect = document.querySelector('select[name="year"]');
    const semesterSelect = document.querySelector('select[name="semester"]');

    if (!batchSelect || !branchSelect || !yearSelect || !semesterSelect) {
        console.error('One or more dropdown elements not found!');
        return;
    }

    // Global function to update Year Dropdown
    window.updateYearDropdown = function () {
        const batchId = batchSelect.value;
        const branchId = branchSelect.value;

        if (!batchId || !branchId) {
            console.log('Batch or Branch not selected.');
            return;
        }

        console.log(` Fetching years for Batch: ${batchId}, Branch: ${branchId}`);

        fetch(`/api/get_filtered_years/?batch=${batchId}&branch=${branchId}`)
            .then(response => response.json())
            .then(data => {
                console.log('Year Data Received:', data);

                yearSelect.innerHTML = '<option value="">Select Year</option>';
                semesterSelect.innerHTML = '<option value="">Select Semester</option>';

                if (data.years.length === 0) {
                    console.warn(' No years found for selected Batch & Branch.');
                    return;
                }

                data.years.forEach(year => {
                    const option = document.createElement('option');
                    option.value = year.id;
                    option.textContent = year.name;
                    yearSelect.appendChild(option);
                });
            })
            .catch(error => console.error(' Error fetching years:', error));
    };

    //  Global function to update Semester Dropdown
    window.updateSemesterDropdown = function () {
        const yearId = yearSelect.value;

        if (!yearId) {
            console.log(' Year not selected.');
            return;
        }

        console.log(` Fetching semesters for Year: ${yearId}`);

        fetch(`/api/get_semesters/?year=${yearId}`)
            .then(response => response.json())
            .then(data => {
                console.log(' Semester Data Received:', data);

                semesterSelect.innerHTML = '<option value="">Select Semester</option>';

                if (data.semesters.length === 0) {
                    console.warn(' No semesters found for selected Year.');
                    return;
                }

                data.semesters.forEach(semester => {
                    const option = document.createElement('option');
                    option.value = semester.id;
                    option.textContent = semester.name;
                    semesterSelect.appendChild(option);
                });
            })
            .catch(error => console.error(' Error fetching semesters:', error));
    };

    // Attach event listeners
    batchSelect.addEventListener('change', window.updateYearDropdown);
    branchSelect.addEventListener('change', window.updateYearDropdown);
    yearSelect.addEventListener('change', window.updateSemesterDropdown);
});
