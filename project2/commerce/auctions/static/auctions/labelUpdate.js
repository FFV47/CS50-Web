/** @type {HTMLInputElement} */
const input = document.getElementById("id_image");
/** @type {HTMLLabelElement} */
const label = document.getElementById("label_image");

input.addEventListener("change", function (e) {
	const value = e.target.value.split("\\");
	label.textContent = value[value.length - 1];
});
