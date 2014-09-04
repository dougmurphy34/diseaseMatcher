/**
 * Created by Doug on 8/20/2014.
 * This file contains helper functions for the template diseaseMatcherApp/abstractDetail.html
 */

//TODO: NOT LOVING THIS SOLUTION - Textarea is a poor display object, interface is unappealing

$(document).ready(function() {

    inputBox = $('#userInput');
    resultsBox = $('#inputSoFar');
    secondsLeft = $('#secondsLeft');
    inputBox.focus();
    resultsBox.css('background-color', '#eeeeee');
    resultsBox.css('pointer-events', 'none');
    inputBox.keypress(movetext);
    secondsLeft.html(30);
    startCountdown(secondsLeft);

//End document.ready call
});

    function startCountdown(whatsLeft) {
        //vars in document.ready are not in scope here

        var doUpdate = function() {
            var count = parseInt(secondsLeft.html());
            if (count !== 0) {
                whatsLeft.html(count - 1)
            }
            else {
                $("#detailForm").submit()
            }
        };

        var timer = setInterval(doUpdate, 1000);

    }

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




