// "Spacing Modifier Letters", "Combining Diacritical Marks", "	Combining Diacritical Marks Supplement", "Combining Diacritical Marks for Symbols", "Combining Half Marks"
// With help of http://kourge.net/projects/regexp-unicode-block
var marksRegex = /[\u02B0-\u02FF\u0300-\u036F\u1DC0-\u1DFF\u20D0-\u20FF\uFE20-\uFE2F]/g;
var othersMap = [
	[/đ/g, "d"],
	[/Đ/g, "D"]
]
function unidecode(string) {
	var cleaned = nfd(string).replace(marksRegex, "");
	for (var i = 0; i < othersMap.length; i++) {
		cleaned = cleaned.replace(othersMap[i][0], othersMap[i][1]);
	}
	return nfc(cleaned);
}
