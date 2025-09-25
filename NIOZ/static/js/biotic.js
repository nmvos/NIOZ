document.addEventListener("DOMContentLoaded", function () {
	// button to toggle the 'bioticWeekTable' table
	document
		.getElementById("toggleTableBtn")
		.addEventListener("click", function (event) {
			event.preventDefault();
			var table = document.getElementById("bioticWeekTable");
			if (table.style.display === "none") {
				table.style.display = "table";
			} else {
				table.style.display = "none";
			}
		});

	// Buttons to toggle the 'toggleEntryTable' function
	document.getElementById("toggleEntryBtn").addEventListener("click", toggleEntryTable);
	document.getElementById("formCancel").addEventListener("click", toggleEntryTable);

	// Function to toggle the Form for entering new biotic data
	function toggleEntryTable(event) {
		event.preventDefault();
		var table = document.getElementById("bioticEntryTable");
		if (table.style.display === "none") {
			table.style.display = "table";
		} else if (record != '') {
			window.location.href = window.location.origin + window.location.pathname;
		} else {
			table.style.display = "none";
		}
	}

	// Collect button function
	document
		.getElementById("collect")
		.addEventListener("click", function (event) {
			event.preventDefault();
			var collectDisplay = document.getElementById("collectDisplay");
			var collectButton = document.getElementById("collect");
			var collectInput = document.querySelector('input[name="collectno"]');
			if (collectDisplay.style.display === "none") {
				collectDisplay.style.display = "block";
				collectButton.innerHTML = "uncollect";
				collectInput.value = nth_record;
			} else {
				collectDisplay.style.display = "none";
				collectButton.innerHTML = "collect";
				collectInput.value = "0";
			}
		});

	// Supress button
	document
		.getElementById("supress")
		.addEventListener("click", function (event) {
			event.preventDefault();
			// no function yet
		});

	// 'enter' key as submit fix
	document.querySelector('form').addEventListener('keypress', function (e) {
		if (e.key === 'Enter') {
			const submitBtn = this.querySelector('button[type="submit"]');
			if (submitBtn) {
				e.preventDefault(); // Prevent triggering other buttons
				submitBtn.click(); // Trigger form submission
			}
		}
	});

	function decodeHtml(html) {
		const textarea = document.createElement("textarea");
		textarea.innerHTML = html;
		return textarea.value;
	}
	// Search Script
	const speciesSearch = document.getElementById('speciesSearch')
	speciesSearch
		.addEventListener("input", function () {
			const query = this.value;
			if (query.length) {
				fetch(`/fyke/fishdetails/live-species-search/?q=${query}`)
					.then((response) => response.json())
					.then((data) => {
						const resultsDiv = document.getElementById("searchResults");
						resultsDiv.innerHTML = "";
						if (data.results.length) {
							resultsDiv.style.display = "block";
							data.results.forEach((item) => {
								const div = document.createElement("div");
								// Decode HTML entities before displaying
								const nlName = decodeHtml(item.nl_name);
								const latinName = decodeHtml(item.latin_name);
								const enName = decodeHtml(item.en_name);

								div.innerHTML = `${item.species_id} - ${nlName} - <i>${enName}</i> - (${latinName})`;
								div.onclick = function () {
									// Use species_id directly
									const speciesid = item.species_id; // Ensure this is set correctly

									// Set the search input to the format: "species_id-speciesname"
									speciesSearch.value = ``;
									speciesSearch.style.border = "";
									speciesSearch.style.backgroundColor = "";

									// Set the hidden input's value to the selected species_id
									document.querySelector('input[name="species"]').value =
										speciesid;

									// Update the species display text dynamically
									document.getElementById(
										"speciesDisplay"
									).innerText = `${speciesid}-${nlName}`;

									resultsDiv.style.display = "none"; // Hide the search results
								};
								resultsDiv.appendChild(div);
							});
						} else {
							resultsDiv.style.display = "none";
						}
					});
			} else {
				document.getElementById("searchResults").style.display = "none";
			}
		});

	// Hide the search results when clicking outside
	document.addEventListener("click", function (e) {
		const resultsDiv = document.getElementById("searchResults");
		if (!resultsDiv.contains(e.target) && e.target.id !== "speciesSearch") {
			resultsDiv.style.display = "none";
		}
	});


	// Form validation Script
	document
		.getElementById("biotic-form")
		.addEventListener("submit", function (event) {
			// Get all input fields for validation
			var fields = document.querySelectorAll('input[type="text"], input[name="species"]');
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

				// Check if the species field is empty
				if (field.name === "species" && value === "") {
					var searchField = document.querySelector('input[name="search"]');
					if (searchField) {
						searchField.style.border = "1px red solid";
						searchField.style.backgroundColor = "pink";
					}
					isValid = false;
					return;
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

			if (document.querySelector('input[name="species"]').value === "") {
				isValid = false;
			}

			// If any field is invalid, show the global error message
			if (!isValid) {
				event.preventDefault(); // Prevent form submission
				globalErrorMessage.style.display = "block"; // Show the global error message
			}
		});

	// fields with `NA` as preset value will be colored
	document.addEventListener('DOMContentLoaded', function () {
		const cells = document.querySelectorAll('.fyke-table:not(#bioticEntryTable) td');
		cells.forEach(function (cell) {
			// Check if the cell's text content is 'NA'
			if (cell.textContent.trim() === 'NA') {
				cell.style.backgroundColor = 'yellow';
			}
		});
	});
});