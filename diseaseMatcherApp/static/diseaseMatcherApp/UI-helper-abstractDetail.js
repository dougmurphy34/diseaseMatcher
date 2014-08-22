/**
 * Created by Doug on 8/20/2014.
 * This file contains helper functions for the template diseaseMatcherApp/abstractDetail.html
 */

//NOT LOVING THIS SOLUTION - Textarea is a poor display object, interface is unappealing

$(document).ready(function() {

    inputBox = $('#userInput');
    resultsBox = $('#inputSoFar');
    inputBox.focus();
    resultsBox.css('background-color', '#eeeeee');
    resultsBox.css('pointer-events', 'none');
    inputBox.keypress(movetext);

//End document.ready call
});

    function movetext(e) {
        //If user presses "Enter" - keyCode 13 - move the typed text to the textarea, then clear the input box

        if (e.keyCode == 13) {
            //For Testing: resultsBox.css('background-color', 'yellow');
            inputText = inputBox.val();
            textareaText = resultsBox.val();
            resultsBox.val(textareaText + inputText + "\n");
            inputBox.val('');
            return false;
        }



    }




