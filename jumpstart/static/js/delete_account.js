(function() {
  const deleteButton = document.querySelector('.delete button');
  deleteButton.addEventListener('click', function(event) {
    // prevent the default button behavior
    event.preventDefault();

    // show the modal dialog
    const modal = document.querySelector('#deleteModal');
    modal.style.display = 'block';

    // add event listener for confirm button in the modal dialog
    const confirmButton = modal.querySelector('.modal-footer .btn-danger');
    confirmButton.addEventListener('click', function() {
      // get the CSRF token
      const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

      // send the POST request to delete the account
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/delete-account/');
      xhr.setRequestHeader('X-CSRFToken', csrfToken);
      xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
          if (xhr.status === 200) {
            window.location.href = '/';
          } else {
            alert('An error occurred while deleting your account. Please try again later.');
          }
        }
      }
      xhr.send(JSON.stringify({}));

      // hide the modal dialog
      modal.style.display = 'none';
    });

    // add event listener for cancel button in the modal dialog
    const cancelButton = modal.querySelector('.modal-footer .btn-secondary');
    cancelButton.addEventListener('click', function() {
      // hide the modal dialog
      modal.style.display = 'none';
    });
  });
})();





