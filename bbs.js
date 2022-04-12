function popup(url) {
	window.open(url, "notice", "width=550,height=410,scrollbars=1");
}
function regform() {
    if (document.getElementById("reg-tbl").style.display == "") {
		document.getElementById("reg-tbl").style.display = "none";
    } else {
		document.getElementById("reg-tbl").style.display = "";
    }
}
function add_form() {
    if (document.getElementById("reg-box").style.display == "") {
		document.getElementById("reg-box").style.display = "none";
    } else {
		document.getElementById("reg-box").style.display = "";
    }
}
function popup(url) {
	window.open(url, "popwin", "width=550,height=350,scrollbars=1");
}
