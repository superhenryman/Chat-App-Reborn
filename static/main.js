const form = document.getElementById("startForm");
const button = document.getElementById("pickServerbutton");
const sidebar = document.getElementById("sidebar");
let serverchoice = 1;

button.addEventListener("click", () => {
    sidebar.style.display = "block";
});

document.getElementById("server1").addEventListener("click" , () => { serverchoice = 1; })
document.getElementById("server2").addEventListener("click" , () => { serverchoice = 2; })
document.getElementById("server3").addEventListener("click" , () => { serverchoice = 3; })
// i couldn't think of a better solution to this


form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username");
    const response = await fetch("/wheredoigo", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "username": username.value,
            "serverChoice": serverchoice,
            "password": document.getElementById("password").value
        })
    });
    if (!response.ok) {
        alert("response bad");
    }
    const json = await response.json();
    switch (json.goto) {
        case "signup":
            document.documentElement.innerHTML = json.code;
            break;
        case "chatroom":
            document.documentElement.innerHTML = json.code;
            break;
        default:
            break;
    }
});

// could be buggy
setInterval(() => {
    switch (serverchoice) {
        case 1:
            document.getElementById("server1").style.color = "red";
            document.getElementById("server2").style.color = "";
            document.getElementById("server3").style.color = "";
            document.getElementById("youselected").innerText = "You selected Server 1.";
            break;
        case 2:
            document.getElementById("server1").style.color = "";
            document.getElementById("server2").style.color = "red";
            document.getElementById("server3").style.color = "";
            document.getElementById("youselected").innerText = "You selected Server 2.";
            break;
        case 3:
            document.getElementById("server1").style.color = "";
            document.getElementById("server2").style.color = "";
            document.getElementById("server3").style.color = "red";
            document.getElementById("youselected").innerText = "You selected Server 3.";
            break;
        default:
            serverchoice = 0;
            break;
    }
}, 100);

