document.addEventListener('DOMContentLoaded', function() {
	let addToMultiViewButton = document.getElementById('add_to_multiview');
	let removeFromMultiViewButton = document.getElementById('remove_from_multiview');
	let downloadButton = document.getElementById('download');
	let addToFavouritesButton = document.getElementById('add_to_favourites');
	let removeFromFavouritesButton = document.getElementById('remove_from_favourites');
	let reportButton = document.getElementById('report');
	let fileId = document.querySelector('h2').textContent.match(/\((\d+)\)/)[1]
	let reportPopup = document.querySelector('.report_popup');
	let reportPopupCloseButton = document.getElementById('cancel_report');
	let reportPopupSubmitButton = document.getElementById('send_report');
	let reportPopupReason = document.getElementById('message');
	let multiview_cookie = document.cookie.match(/multiview_list="([^"]*)"/)[1].split('\\073');
	let favourites_cookie = document.cookie.match(/favourites_list="([^"]*)"/)[1].split('\\073');
	function checkIfInMultiView() {
		if (multiview_cookie.includes(fileId)) {
			addToMultiViewButton.parentElement.style.display = 'none';
			removeFromMultiViewButton.parentElement.style.display = 'block';
		}
	}
	function checkIfInFavourites() {
		if (favourites_cookie.includes(fileId)) {
			addToFavouritesButton.parentElement.style.display = 'none';
			removeFromFavouritesButton.parentElement.style.display = 'block';
		}
	}
	checkIfInMultiView();
	checkIfInFavourites();
	downloadButton.addEventListener('click', function() {
		fetch('download_file', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				file_id: fileId
			})
		})
		.then(response => response.blob())
		.then(blob => {
			let downloadLink = document.createElement('a');
			blob.text().then(function(result) {
				let file_data = result;
				downloadLink.href = 'data:application/octet-stream;base64,' + file_data;
				if (document.querySelector('.is_selected')) {
					let liSelected = document.querySelector('.is_selected');
					downloadLink.download = liSelected.querySelector('a').textContent.match(/^(.*) \(/)[1];
				}
				else {
					downloadLink.download = document.querySelector('h2').textContent.match(/^(.*) \(/)[1];
				}
				downloadLink.click();
				downloadLink.remove();
			});
		});
	});
	addToMultiViewButton.addEventListener('click', function() {
		addToMultiViewButton.parentElement.style.display = 'none';
		removeFromMultiViewButton.parentElement.style.display = 'block';
		fetch('add_to_multiview', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				file_id: fileId
			})
		});
	});
	removeFromMultiViewButton.addEventListener('click', function() {
		addToMultiViewButton.parentElement.style.display = 'block';
		removeFromMultiViewButton.parentElement.style.display = 'none';
		fetch('remove_from_multiview', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				file_id: fileId
			})
		});
	});
	addToFavouritesButton.addEventListener('click', function() {
		addToFavouritesButton.parentElement.style.display = 'none';
		removeFromFavouritesButton.parentElement.style.display = 'block';
		fetch('add_to_favourites', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				file_id: fileId
			})
		});
	});
	removeFromFavouritesButton.addEventListener('click', function() {
		addToFavouritesButton.parentElement.style.display = 'block';
		removeFromFavouritesButton.parentElement.style.display = 'none';	
		fetch('remove_from_favourites', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				file_id: fileId
			})
		});
	});
	reportButton.addEventListener('click', function() {
		reportPopup.style.display = 'block';
	});
	reportPopupCloseButton.addEventListener('click', function() {
		reportPopup.style.display = 'none';
	});
	reportPopupSubmitButton.addEventListener('click', function() {
		let reportReason = reportPopupReason.value;
		if (reportReason.length > 0) {
			fetch('report', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					file_id: fileId,
					reason: reportReason
				})
			});
			reportPopup.style.display = 'none';
			alert('Le fichier a été signalé avec succès.');
		} else {
			alert('Veuillez entrer une raison pour le signalement.');
		}
	});
});
window.addEventListener('resize', function() {
	let fileObject = document.querySelector('.file_object');
	let fileObjectSize = 50;
	let fileObjectBottom = fileObject.getBoundingClientRect();
	let windowHeight = window.innerHeight;
	let windowWidth = window.innerWidth;
	let windowHeightMinus = null;
	if (windowWidth > 1000) {
		windowHeightMinus = 75
	} else if (windowWidth < 1000 && windowWidth > 535) {
		windowHeightMinus = 150
	} else {
		windowHeightMinus = 200
	}
	while (fileObjectBottom.bottom < windowHeight - windowHeightMinus) {
		fileObject.style.height = fileObjectSize + 'vh';
		fileObjectSize += 5;
		fileObjectBottom = fileObject.getBoundingClientRect();
	}
});
window.dispatchEvent(new Event('resize'));