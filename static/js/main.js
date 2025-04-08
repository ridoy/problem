const sortable = new Sortable(document.getElementById('sortableList'), {
	animation: 150
});
let generatedUrl;
function removeEmailInput() {
	if (document.getElementById("email-input")) {
		document.getElementById("email-input").remove();
	}
	if (document.getElementById("email-submit-button")) {
		document.getElementById("email-submit-button").remove();
	}
}
function removeGenerateButton() {
	if (document.getElementById("generate-button")) {
		document.getElementById("generate-button").remove();
	}
}
function generateMP3() {
	const verses = document.querySelectorAll(".draggable-item");
	const versesToInclude = [];
	verses.forEach(verse => {
		if (verse.querySelector('input[type="checkbox"]').checked) {
			versesToInclude.push(parseInt(verse.getAttribute("data-id")));
		}
	})
	if (versesToInclude.length === 0) {
		return;
	}
	const payload = { order: versesToInclude };
	const responseElement = document.getElementById('response');
	responseElement.innerText = "GENERATING...";
	removeEmailInput();
	removeGenerateButton();
	fetch('/stitch', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(payload)
	})
	.then(response => response.json())
	.then(data => {
		generatedUrl = data.generated_url;
		const emailInput = document.createElement('input');
		emailInput.setAttribute("id", "email-input");
		emailInput.placeholder = "ENTER EMAIL HERE";
		const emailSubmit = document.createElement('button');
		emailSubmit.id = "email-submit-button";
		emailSubmit.innerText = "SUBMIT";
		emailSubmit.onclick = sendEmail;
		responseElement.innerHTML = '';
		responseElement.appendChild(emailInput);
		responseElement.appendChild(emailSubmit);
	})
	.catch((error) => {
		console.error('Error:', error);
	});
}
function sendEmail() {
	const email = document.getElementById("email-input").value;
	if (email === "") {
		return;
	}
	const payload = {
		"email": email
	}
	const responseElement = document.getElementById('response');
	responseElement.innerHTML = 'JUST A SECOND...';
	fetch('/email', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(payload)
	})
	.then(response => response.json())
	.then(data => {
		const downloadLink = document.createElement('a');
		removeEmailInput();
		downloadLink.href = generatedUrl;
		downloadLink.innerText = "PLAY YOUR CUSTOMIZED MP3 HERE";
		downloadLink.setAttribute('target', '_blank');
		responseElement.innerHTML = '';
		responseElement.appendChild(downloadLink);
	})
	.catch((error) => {
		console.error('Error:', error);
	}); 
}
