/**
 * Created by Doug on 8/20/2014.
 */

//NOT LOVING THIS SOLUTION
//TODO: Replace this approach with jquery, bootstrap, or angular.js

userInputTextbox = document.getElementById('userInput');
resultsTextarea = document.getElementById('inputSoFar');
form = document.getElementById('detailForm');

userInputTextbox.addEventListener('keypress', function(e) {

    var key = e.which || e.keyCode;
    if (key == 45) {
        resultsTextarea.text += userInputTextbox.text;
        userInputTextbox.text = "";
    }

});

//This is not working.  Also, deeply inelegant solution
form.addEventListener('keypress', function(e) {

    var key = e.which || e.keyCode;
    if (key == 13) {
        return false
    }

});