document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("question")?.addEventListener("keydown", (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevents the default behavior (e.g., adding a new line)
            console.log('Enter key pressed!');
            document.getElementById("card").innerHTML = ""
        }
    });
});
