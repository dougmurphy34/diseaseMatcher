/**
 * Created by Doug on 8/20/2014.
 * This file contains client-side logic for the template diseaseMatcherApp/abstractDetail.html
 */

//TODO: TextArea is a poor display object, change to Table
//TODO: Fix "double fadeout" message problem

    // PLAN GOES LIKE THIS:
    // 1) DONE - regex comparison of entered text to title and abstract text.  Disallow (with message) if no match.
    // 2) Display answers in a list, in black.  -->probably time to change textarea to a table
    // 3) In request.context, pass a list of all past successful answers (ordered by frequency) to view.
    // 4) Every 5ish seconds, add the top answer to "AI answers".  (This means max possible answers is LENGTH_OF_GAME_IN_SECONDS / 5)
    // 5) If an answer is entered by both user and AI, change its color to green.
    // 6) Update instructions - zero (?) points per you-only answer, 10 points for match-with-AI answer.
    // 7) Change models.py to reflect new scoring system.  Change user profiles to match new work history and ranking system.
    // 8) Deal with the few/no answer yet problem: use capitalized words/phrases?  Most common words > 6 chars?

LENGTH_OF_GAME_IN_SECONDS = 300;

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
        //Also removes some punctuation, but leaves other (ie, so Asperger's is not converted to Aspergers and therefore not matched)

        //***These characters pose no problem: , . - / ; ' " ALSO () in pairs
        //***These break things: uneven parentheses

        //Trimming punctuation passes sanitized answers to be matched vs. actual text, so it won't find any matches.  This is usually fine.
        //TODO: Once client side matching is implemented, reject dangerous input and pop up a fadeaway warning about avoiding punctuation.
        var no_paren_family = input_string.replace(/[(){}\[\]]+/g,"");
        //no_punctuation = no_paren_family.replace(/[\.\?!,]+/g,"");
        var no_leads = no_paren_family.replace(/^[ \t]+/, "");

        //no_double_spaces = no_trails.replace(/\s{2,}g/," ");
        return no_leads.replace(/[ \t]+\r?\n?$/, "");//Save variable declaration of no_trails

}


function test_for_matches(userEnteredText) {

    var thisRe = new RegExp(userEnteredText);
    var abstractString = abstractText.text();
    var result = abstractString.search(thisRe);

    if (result == -1) {
        feedback.fadeIn('fast');
        feedback.text('no Match').css('backgroundColor',"red").fadeOut(1500);
        return false
    }
    else { //TODO: Probably remove this from final version, provides minimal value
        feedback.fadeIn('fast');
        feedback.text('Match!').css('backgroundColor',"green").fadeOut(1200);
        return true
    }
}

function test_for_too_long(answerString) {
    if (answerString.toString().length > 50) {
        feedback.fadeIn('fast');
        feedback.text('Answers should be 50 characters or less').css('backgroundColor','red').fadeOut(3000);
        return true
    }

    return false
}

function dupe_message() {
    feedback.fadeIn('fast');
    feedback.text('You already entered that one!').css('backgroundColor','red').fadeOut(3000);

}

function moveText(e) {
    //If user presses "Enter" - keyCode 13 - move the typed text to the textArea, then clear the input box

    if (e.keyCode == 13) {
        if (!test_for_matches(inputBox.val())) {
            //There's no match; don't take answer, and also reject form submission
            inputBox.val('');
            return false
        }

        var inputText = trim_evil_characters(inputBox.val());

        if (typeof answerDict[inputText] == 'undefined') {//prevent dupes, which would reset time entered to later time
            textareaText = resultsBox.val();
            timeLeft = secondsLeft.html();
            //record answer and time to our associative array
            answerDict[inputText] = LENGTH_OF_GAME_IN_SECONDS - parseInt(timeLeft);

            //Update UI
            resultsBox.val(textareaText + inputText + "\n");

        }
        else {
            dupe_message()
        }

        inputBox.val('');

        //Prevent form submission - Enter should not submit the form in this app
        return false;
    }

}

function addTextFromMouseUp(textSelection) {

    if (test_for_too_long(textSelection)) {
            //Too long, don't add.  This is common when a vertical mouse move grabs a whole extra row of text.
            //text_for_too_long function handles user error feedback
            return false
        }

    if (textSelection.anchorOffset == textSelection.focusOffset) {
            //It's a zero-length selection. Get out of here.
            return false
        }

    if (window.confirm('select the text ' + textSelection.toString() + '?')){
        if (textSelection.anchorOffset > textSelection.focusOffset) {
            //It's a forward-direction selection, so the anchor (mousedown) is the start and the focus (mouseup) is the end
            start = textSelection.anchorOffset;
            end = textSelection.focusOffset;
        }
        else {
            //It's a backwards selection
            start = textSelection.focusOffset;
            end = textSelection.anchorOffset;
        }




        if (textSelection.anchorNode.parentNode.nodeName == 'DIV') {
            //We are in the abstract text.  Otherwise, it would have returned 'H1'.
            //Boy, is this asking for trouble when we do refactoring.  And horribly tight coupling between view and controller.

            //Offset seems to start at 0 in title, and at 9 in text.  Why 9?

        }
        else {
            //We are in abstract title.
        }

        var timeLeft = secondsLeft.html();

        //clean up result
        var cleanText = trim_evil_characters(textSelection.toString());

        if (typeof answerDict[cleanText] == 'undefined') {//prevent dupes, which would reset time entered to later time

            //record answer and time to our associative array
            answerDict[cleanText] = LENGTH_OF_GAME_IN_SECONDS - parseInt(timeLeft);

            //update UI
            var textareaText = resultsBox.val();
            resultsBox.val(textareaText + cleanText + "\n");
        }
        else {
            dupe_message()
        }
    }


}


$(document).ready(function() {

    feedback = $('#feedback');
    inputBox = $('#userInput');
    resultsBox = $('#inputSoFar');
    secondsLeft = $('#secondsLeft');
    abstractText = $('#abstractTextDiv');
    abstractTitle = $('#abstractTitleDiv');

    inputBox.focus();
    resultsBox.css('background-color', '#eeeeee');
    resultsBox.css('pointer-events', 'none');
    inputBox.keypress(moveText);
    secondsLeft.html(LENGTH_OF_GAME_IN_SECONDS);
    startCountdown(secondsLeft);
    abstractTitle.mouseup(function() {addTextFromMouseUp(window.getSelection())});
    abstractText.mouseup(function() {addTextFromMouseUp(window.getSelection())});

    //prevent multiple submissions of the form
    //this was a problem with the auto-submit when processing the POST took > 1 second
    $("form").submit(function() {
        $("#userTypedMatches").val(JSON.stringify(answerDict));
        $(this).submit(function() {
            return false;
        });
        return true;
    });

//End document.ready call
});





