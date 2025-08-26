const form = document.getElementById("signupform");

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const response = await fetch("/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "username": username,
            "password": password
        })
    });
    if (!response.ok) {
        alert("response bad");
    }
    const result = await response.json();
    if (result.goto === "root") {
        alert(`Don't forget! Your username is ${username} and your password is ${password}!`);
        document.documentElement.innerHTML = result.code;
    } else {
        alert(result.error);
    }
});