document.addEventListener("DOMContentLoaded", () => {

    const dialogId = "error-modal"

    // Function to open the dialog with specific content
    function openDialog(content, status) {
        const dialog = document.getElementById(dialogId);
        document.getElementById('dialog-content').innerHTML = content;
        document.getElementById('dialog-status').innerHTML = status;
        dialog.showModal();  // Open the dialog
    }

    // Function to close the modal
    function closeDialog() {
        const dialog = document.getElementById(dialogId);
        dialog.close();  // Close the dialog
    }

    // document.querySelector("#error-modal button").addEventListener("click", closeDialog);

    // document.body.addEventListener('htmx:responseError', (evt) => {
    //     var xhr = evt.detail.xhr;
    //     if (xhr.status >= 400 && xhr.status < 600) {
    //         // Insert error response into modal
    //         openDialog(xhr.responseText || `An error occurred.`, `Status: ${xhr.status}`);
    //     }
    // });


});