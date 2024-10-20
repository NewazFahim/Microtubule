// Get the active document
var doc = app.activeDocument;

// Initialize an array to hold the lengths of all paths
var pathLengths = [];

// Loop through all the path items in the document
for (var i = 0; i < doc.pathItems.length; i++) {
    var pathItem = doc.pathItems[i];
    var length = pathItem.length;
    pathLengths.push(length);
}

// Create the content for the text file
var fileContent = "Lengths of all paths:\n";
for (var k = 0; k < pathLengths.length; k++) {
    fileContent += "Path " + (k + 1) + ": " + pathLengths[k].toFixed(2) + " pixels\n";
}

// Save the content to a text file
var file = new File(Folder.desktop + "/path_lengths.txt");
file.encoding = "UTF-8";
file.open("w");
file.write(fileContent);
file.close();

alert("Path lengths saved to path_lengths.txt on your desktop.");
