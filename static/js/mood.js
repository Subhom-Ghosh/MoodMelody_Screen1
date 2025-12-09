function analyzeMood() {
    let text = document.getElementById("textInput").value;

    // Show a loading text or disable button here if you want
    document.getElementById("result").innerHTML = "Analyzing...";

    fetch("/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: text }),
    })
    .then((response) => response.json())
    .then((data) => {
        document.getElementById("result").innerHTML = `<strong>Suggestion:</strong> ${data.suggestion}`;
        document.body.style.backgroundColor = data.color;
        document.getElementById("result").style.color = data.fontColor;
    })
    .catch((error) => {
        console.error("Error:", error);
        document.getElementById("result").innerHTML = "Error connecting to server.";
    });
}

document.getElementById("chat").addEventListener("click", function () {
    window.location.href = "/chat"; // Matches the Flask route
});

document.getElementById("song").addEventListener("click", function () {
    window.location.href = "/song"; // Matches the Flask route
});