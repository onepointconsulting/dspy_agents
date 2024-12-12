document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("question")?.addEventListener("keydown", (event) => {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevents the default behavior (e.g., adding a new line)
            console.log('Enter key pressed!');
            document.getElementById("card").innerHTML = ""
        }
    });
    
    function writeToQuestionArea(e) {
        e.preventDefault()
        const value = e.target.text ?? "No value"
        const questionField = document.getElementById("question")
        if(questionField) {
            questionField.value = value
        }
    }

    [...document.querySelectorAll(".questionLink")].forEach(el => {
        el.addEventListener("click", (e) => {
            writeToQuestionArea(e)
        })
    })
});

