/**
 * Created by Doug on 8/20/2014.
 * This file contains helper functions for the template diseaseMatcherApp/abstractDetail.html
 */

//TODO: NOT LOVING THIS SOLUTION - TextArea is a poor display object, interface is unappealing

LENGTH_OF_GAME_IN_SECONDS = 30;


var answerDict = {};

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

function trim_space_tab(input_string) {
        //Trims leading and trailing spaces and tabs
        //Leaves behind CRLF, which we need - that's why I didn't use jquery's .trim()

        noleads = input_string.replace(/^[ \t]+/, "");
        return noleads.replace(/[ \t]+\r?\n?$/, "")
}

function moveText(e) {
    //If user presses "Enter" - keyCode 13 - move the typed text to the textArea, then clear the input box

    if (e.keyCode == 13) {
        inputText = trim_space_tab(inputBox.val());
        textareaText = resultsBox.val();
        timeLeft = secondsLeft.html();

        //record answer and time to our associative array
        answerDict[inputText] = LENGTH_OF_GAME_IN_SECONDS - parseInt(timeLeft);

        //Update UI
        resultsBox.val(textareaText + inputText + "\n");
        inputBox.val('');

        //Prevent form submission - Enter should not submit the form in this app
        return false;
    }

}

function addTextFromMouseUp(textSelection) {

    timeLeft = secondsLeft.html();

    //clean up result
    cleanText = trim_space_tab(textSelection.toString());//Fails

    //record answer and time to our associative array
    answerDict[cleanText] = LENGTH_OF_GAME_IN_SECONDS - parseInt(timeLeft);

    //update UI
    textareaText = resultsBox.val();
    resultsBox.val(textareaText + cleanText + "\n");

}


$(document).ready(function() {

    inputBox = $('#userInput');
    resultsBox = $('#inputSoFar');
    secondsLeft = $('#secondsLeft');
    abstractText = $('#abstractTextDiv');

    inputBox.focus();
    resultsBox.css('background-color', '#eeeeee');
    resultsBox.css('pointer-events', 'none');
    inputBox.keypress(moveText);
    secondsLeft.html(LENGTH_OF_GAME_IN_SECONDS);
    startCountdown(secondsLeft);
    abstractText.mouseup(function() {addTextFromMouseUp(window.getSelection())});

    //prevent multiple submissions of the form
    //this was a problem with the auto-submit when processing the POST took > 1 second
    $("form").submit(function() {
        $("#userMatches").val(JSON.stringify(answerDict));
        $(this).submit(function() {
            return false;
        });
        return true;
    });

//End document.ready call
});





