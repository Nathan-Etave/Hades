document.addEventListener('DOMContentLoaded', function() {
	let removeNotificationButtons = document.getElementsByClassName('supprimer');
	Array.from(removeNotificationButtons).forEach(function(button) {
		button.addEventListener('click', function() {
			let fileId = button.parentElement.getElementsByClassName('file_id')[0].textContent;
			let notificationId = button.parentElement.getElementsByClassName('notification_id')[0].textContent;
			let dateId = button.parentElement.getElementsByClassName('date_id')[0].textContent;
			fetch('remove_from_notifications', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					id_file: fileId,
					id_notification: notificationId,
					id_date: dateId
				})
			})
			.then(response => {
				if (response.redirected) {
					window.location.href = response.url;
				}
			});
		});
	});
});