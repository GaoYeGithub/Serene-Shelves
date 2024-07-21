var toolType = 'line'; 
var widthSlider = document.querySelector('#widthSlider');
var colorInput = document.querySelector('#colorPicker');

var firebaseConfig = {
    apiKey: "AIzaSyCntsGwcx23zoQxFXgkxj76-8xgwGM8nJg",
    authDomain: "drawing-test-fc89d.firebaseapp.com",
    databaseURL: "https://drawing-test-fc89d-default-rtdb.firebaseio.com",
    projectId: "drawing-test-fc89d",
    storageBucket: "drawing-test-fc89d.appspot.com",
    messagingSenderId: "622905699981",
    appId: "1:622905699981:web:385b2f7d00185f7a25bcc4",
    measurementId: "G-V2NTMLZJW9"
};
firebase.initializeApp(firebaseConfig);

var pointsData = firebase.database().ref();
var points = [];

function setup() {
  setupCanvasAndControls();
  setupFirebaseListeners();
}

function setupCanvasAndControls() {
  var canvas = createCanvas(windowWidth, windowHeight);
  background(255);
  fill(0);

  canvas.mousePressed(drawPoint);
  canvas.mouseReleased(function () {
    pointsData.push({type: "release"});
  });
  canvas.mouseMoved(function () {
    if (mouseIsPressed) {
      drawPoint();
    }
  });

  $("#saveDrawing").on("click", saveDrawing);
  $("#clearDrawing").on("click", clearDrawing);
}

function setupFirebaseListeners() {
  pointsData.on("child_removed", function () {
    points = [];
  });
  pointsData.on("child_added", function (point) {
    points.push(point.val());
  });
}

function draw() {
  background(255);
  for (var i = 0; i < points.length; i++) {
    var point = points[i];
    fill(point.color || '#000000');
    if (i > 0 && point.type == "line" && points[i - 1].type == "line") {
      var previous = points[i - 1];
      stroke(point.color || '#000000');
      strokeWeight(point.width);
      line(point.x, point.y, previous.x, previous.y);
    }
  }
}

function drawPoint() {
  pointsData.push({
    type: toolType,
    x: mouseX,
    y: mouseY,
    color: colorInput.value,
    width: widthSlider.value
  });
}

function saveDrawing() {
  saveCanvas(window.prompt("Save as", "DeStress Drawing"));
}

function clearDrawing() {
  pointsData.remove();
  points = [];
}
