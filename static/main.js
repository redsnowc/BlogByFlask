const ul = document.querySelector("ul");

ul.addEventListener("mouseover", function (e) {
    if (e.target.tagName === "LI") {
        e.target.style.fontSize = "20px";
        e.target.style.color = "blue";
    }
});

ul.addEventListener("mouseout", function (e) {
    if (e.target.tagName === "LI") {
        e.target.style.fontSize = "unset";
        e.target.style.color = "unset";
    }
});

// for (let i = 0; i <= li_list.length; i++) {
//     console.log(li_list[i]);
// }