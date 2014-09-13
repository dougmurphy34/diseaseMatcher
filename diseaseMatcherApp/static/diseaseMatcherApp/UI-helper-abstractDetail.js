/**
 * Created by Doug on 8/20/2014.
 * This file contains helper functions for the template diseaseMatcherApp/abstractDetail.html
 */

//TODO: NOT LOVING THIS SOLUTION - TextArea is a poor display object, interface is unappealing

LENGTH_OF_GAME_IN_SECONDS = 3000;


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

function trim_evil_characters(input_string) {
        //Trims leading and trailing spaces and tabs
        //Leaves behind CRLF, which we need - that's why I didn't use jquery's .trim()
        //Also removes some punctuation  #TODO: Should remove ['"-]?  Advantage: Asperger's == Aspergers

    //TODO: Remove parens as well, these break stuff.  Maybe {}[]()
    //***These characters pose no problem: , . - / ; ()
    //***These break things: parentheses and commas when together?  Key error.  See if I can replicate with no back button.
    //***This string failed to match itself: "gene ( s ) other than BRCA1".  Parens and spaces together?  2 data points say yes.

        //TODO: OH NO!  If I do this, it won't find any matches!!!
        //TODO: Instead, reject the input and pop up a fadeaway warning about avoiding punctuation?
        //no_paren_family = input_string.replace(/[(){}\[\]]+/g,"");
        //no_punctuation = no_paren_family.replace(/[\.\?!,]+/g,"");
        no_leads = input_string.replace(/^[ \t]+/, "");
        no_trails = no_leads.replace(/[ \t]+\r?\n?$/, "");
        //no_double_spaces = no_trails.replace(/\s{2,}g/," ");


        return no_trails
}

function moveText(e) {
    //If user presses "Enter" - keyCode 13 - move the typed text to the textArea, then clear the input box

    if (e.keyCode == 13) {

        inputText = trim_evil_characters(inputBox.val());

        if (typeof answerDict[cleanText] == 'undefined') {//prevent dupes, which would reset time entered to later time
            textareaText = resultsBox.val();
            timeLeft = secondsLeft.html();
            //record answer and time to our associative array
            answerDict[inputText] = LENGTH_OF_GAME_IN_SECONDS - parseInt(timeLeft);

            //Update UI
            resultsBox.val(textareaText + inputText + "\n");

        }

        inputBox.val('');

        //Prevent form submission - Enter should not submit the form in this app
        return false;
    }

}

function addTextFromMouseUp(textSelection) {

    timeLeft = secondsLeft.html();

    //clean up result
    cleanText = trim_evil_characters(textSelection.toString());

    if (typeof answerDict[cleanText] == 'undefined') {//prevent dupes, which would reset time entered to later time

        //record answer and time to our associative array
        answerDict[cleanText] = LENGTH_OF_GAME_IN_SECONDS - parseInt(timeLeft);

        //update UI
        textareaText = resultsBox.val();
        resultsBox.val(textareaText + cleanText + "\n");
    }
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





