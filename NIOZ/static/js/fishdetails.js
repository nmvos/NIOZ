document.addEventListener("DOMContentLoaded", function () {
	try {
		var button = document.getElementById("add-stomach-data");
		var tbody = document.getElementById("stomach-data-tbody");
		var table = document.getElementById("stomach-data-content");

		let count = stomachDataLength;
		button.addEventListener("click", function (e) {
			if (count == 0) { // if button gets clicked for the first time
				table.style.display = "block";
			}
			let tr = document.createElement('tr');
			let td1 = document.createElement('td');
			let input1 = document.createElement('input');
			input1.type = 'text';
			input1.id = `stomach_search_${count}`;
			input1.placeholder = 'Search species...';
			input1.autocomplete = 'off';
			td1.appendChild(input1);

			let td2 = document.createElement('td');
			let span = document.createElement('span');
			span.id = `stomach_display_${count}`;
			let input2 = document.createElement('input');
			input2.type = 'hidden';
			input2.id = `stomach_input_${count}`;
			input2.value = '';
			let searchResultsDiv = document.createElement('div');
			searchResultsDiv.id = `stomach_results_${count}`;
			searchResultsDiv.style.position = 'absolute';
			searchResultsDiv.style.background = 'white';
			searchResultsDiv.style.border = '1px solid #ddd';
			searchResultsDiv.style.display = 'none';
			td2.appendChild(span);
			td2.appendChild(input2);
			td2.appendChild(searchResultsDiv);

			let td3 = document.createElement('td');
			let input3 = document.createElement('input');
			input3.type = 'text';
			input3.id = `stomach_number_${count}`;
			input3.value = '';
			td3.appendChild(input3);

			let td4 = document.createElement('td');
			let input4 = document.createElement('input');
			input4.type = 'text';
			input4.id = `stomach_length_${count}`;
			input4.value = '';
			td4.appendChild(input4);

			let td5 = document.createElement('td');
			let button = document.createElement('button');
			button.textContent = 'X';
			button.classList.add('btn', 'btn-primary');
			button.addEventListener('click', function () {
				count--;
				tr.remove();
			})
			let deleteRecord = document.createElement('input');
			deleteRecord.type = 'hidden';
			deleteRecord.id = `stomach_delete_${count}`;
			let input5 = document.createElement('input');
			input5.type = 'hidden';
			input5.id = `stomach_id_${count}`;
			td5.appendChild(button);
			td5.appendChild(deleteRecord);
			td5.appendChild(input5);

			tr.appendChild(td1);
			tr.appendChild(td2);
			tr.appendChild(td3);
			tr.appendChild(td4);
			tr.appendChild(td5);

			tbody.appendChild(tr);
			count++;
		});


		// pre-submit stomachdata form handling
		document
			.getElementById("fishdetails-form")
			.addEventListener("submit", function (event) {
				if (count != 0) {
					['stomach_input', 'stomach_number', 'stomach_length','stomach_delete', 'stomach_id'].forEach(field => {
						document.querySelector(`input[name="${field}"]`).value =
							Array.from({ length: count }, (_, i) => document.querySelector(`input[id="${field}_${i}"]`).value).join(";");
					});
				}
			});
	} catch { }

	// Species Search
	function decodeHtml(html) {
		const textarea = document.createElement('textarea');
		textarea.innerHTML = html;
		return textarea.value;
	}

	function setupLiveSearch(inputElement, hiddenInputName, displayElementId, resultsDivId) {
		inputElement.addEventListener('input', function () {
			const query = this.value;
			if (query.length > 0) {  // Start search after 2 characters
				fetch(`/fyke/fishdetails/live-species-search/?q=${query}`)
					.then(response => response.json())
					.then(data => {
						const resultsDiv = document.getElementById(resultsDivId);
						resultsDiv.innerHTML = '';
						if (data.results.length) {
							resultsDiv.style.display = 'block';
							data.results.forEach(item => {
								const div = document.createElement("div");
								// Decode HTML entities before displaying
								const nlName = decodeHtml(item.nl_name);
								const latinName = decodeHtml(item.latin_name);
								const enName = decodeHtml(item.en_name);

								div.innerHTML = `${item.species_id} - ${nlName} - <i>${enName}</i> - (${latinName})`;
								div.style.cursor = 'pointer';
								div.onclick = function () {
									// Use species_id directly
									const speciesid = item.species_id;

									// Set the search input to the format: "species_id-speciesname"
									inputElement.value = ``;

									// Set the hidden input's value to the selected species_id
									document.querySelector(`input[name="${hiddenInputName}"], input[id="${hiddenInputName}"]`).value = speciesid;

									// Update the species display text dynamically
									document.getElementById(displayElementId).innerText = `${speciesid}-${nlName}`;

									resultsDiv.style.display = 'none';  // Hide the search results
								};
								resultsDiv.appendChild(div);
							});
						} else {
							resultsDiv.style.display = 'none';
						}
					});
			} else {
				document.getElementById(resultsDivId).style.display = 'none';
			}
		});

		// Hide the search results when clicking outside
		document.addEventListener('click', function (e) {
			try {
				const resultsDiv = document.getElementById(resultsDivId);
				if (!resultsDiv.contains(e.target) && e.target !== inputElement) {
					resultsDiv.style.display = 'none';
				}
			} catch {}
		});
	}

	try {
		// Apply live search to the speciesSearch input
		setupLiveSearch(document.getElementById('speciesSearch'), 'species', 'speciesDisplay', 'searchResults');

		// Apply live search to dynamically generated stomach_search inputs
		function activateStomachDataSearch() {
			const stomachSearchInputs = document.querySelectorAll('[id^="stomach_search_"]');
			stomachSearchInputs.forEach((input, index) => {
				setupLiveSearch(input, `stomach_input_${index}`, `stomach_display_${index}`, `stomach_results_${index}`);
			});
		}

		// execute the function when clicking the button
		document.getElementById('add-stomach-data').addEventListener('click', function () {
			activateStomachDataSearch();
		});

		// Check if stomach_data has data and execute the function directly
		if (stomachDataLength > 0) {
			activateStomachDataSearch();
		}
	} catch { }

	// Form validation
	document
		.getElementById('fishdetails-form')
		.addEventListener("submit", function (event) {
			// Get all input fields for validation
			var fields = document.querySelectorAll('input[type="text"]');
			var isValid = true; // Assume inputs are valid initially

			// Regular expression to allow both decimal separators (either . or ,)
			var numberRegex = /^[0-9]+([.,][0-9]+)?$/;

			// Hide the global error message initially
			var globalErrorMessage = document.getElementById("global-error-message");
			globalErrorMessage.style.display = "none";

			// Loop through all fields and validate
			fields.forEach(function (field) {
				var value = field.value.trim();

				if (value.toUpperCase() === "NA") {
					return; // Skip validation for these fields
				}

				// Check if the field is valid
				if (value !== "" && !numberRegex.test(value)) {
					// Invalid input: apply styles
					field.style.border = "1px red solid";
					field.style.backgroundColor = "pink";
					isValid = false;
				} else {
					// Valid input: reset styles
					field.style.border = "";
					field.style.backgroundColor = "";
				}
			});

			const stomachSearchInputs = document.querySelectorAll('[id^="stomach_search_"]');
			stomachSearchInputs.forEach((field, index) => {
				var hiddenInput = document.getElementById(`stomach_input_${index}`)
				
				if (hiddenInput.value == "") {
					field.style.border = "1px red solid";
					field.style.backgroundColor = "pink";
					isValid = false;
				} else {
					// Valid input: reset styles
					field.style.border = "";
					field.style.backgroundColor = "";
				}
			});

			// If any field is invalid, show the global error message
			if (!isValid) {
				event.preventDefault(); // Prevent form submission
				globalErrorMessage.style.display = "block"; // Show the global error message
			}
		});
});