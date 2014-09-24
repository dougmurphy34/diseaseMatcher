/**
 * Created by Doug on 8/20/2014.
 * This file contains client-side logic for the template diseaseMatcherApp/abstractDetail.html
 */

//TODO: Fix "double fadeout" message problem

    // PLAN GOES LIKE THIS:
    // 1) DONE - regex comparison of entered text to title and abstract text.  Disallow (with message) if no match.
    // 2) DONE - Display answers in a list, in black.  -->probably time to change textarea to a table
    // 3) In request.context, pass a list of gold standard answers to javascript.
    // 4) Every 5ish seconds, add the top answer to "AI answers".  (This means max possible answers is LENGTH_OF_GAME_IN_SECONDS / 5)
    // 5) If an answer is entered by both user and AI, change its color to green.
    // 6) Update instructions - zero (?) points per you-only answer, 10 points for match-with-AI answer.
    // 7) Change models.py to reflect new scoring system.  Change user profiles to match new work history and ranking system.

LENGTH_OF_GAME_IN_SECONDS = 300;

var answerDict = {};//Format {"theTextTyped" : secondsInt}
var selectDict = {};//Format {"selectedText" : {"secondsInt": 8, "titleText": 1, "offset": 32}}
// data_for_js Format [{"pk":781,"model":"diseaseMatcherApp.goldstandardmatch","fields":{"match_offset":10,"abstract":100,"text_matched":"coronaryheartdisease","match_location":1,"match_length":22,"annotation_id":112634}}]

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
        //Leaves behind CRLF, which we need - that's why I didn't use jquery's .trim()//TODO: with table model (not textarea) maybe we can move to .trim()?
        //Also removes some punctuation, but leaves other (ie, so Asperger's is not converted to Aspergers and therefore not matched)

        //***These characters pose no problem: , . - / ; ' " ALSO () in pairs
        //***These break things: uneven parentheses

        //Trimming punctuation passes sanitized answers to be matched vs. actual text, so it won't find any matches.  This is usually fine.
        //TODO: On rejecting dangerous input pop up a fadeaway warning about avoiding punctuation. -- mouse matches only
        var no_paren_family = input_string.replace(/[(){}\[\]]+/g,"");
        //no_punctuation = no_paren_family.replace(/[\.\?!,]+/g,"");
        var no_leads = no_paren_family.replace(/^[ \t]+/, "");

        //no_double_spaces = no_trails.replace(/\s{2,}g/," ");
        return no_leads.replace(/[ \t]+\r?\n?$/, "");//Save variable declaration of no_trails

}

function test_for_gold_standard_text_match(passedText) {
    //TODO: similar function for mouse entry.

    for (i in data_for_js) {
        if (data_for_js.hasOwnProperty(i)) {
            if (data_for_js[i]["fields"]["text_matched"] == passedText) {
                alert('You matched a Gold Standard answer!');

            }
        }

    }
}

function test_for_matches(userEnteredText) {

    var thisRe = new RegExp(userEnteredText);
    var abstractString = abstractTitle.text() + abstractText.text();
    var result = abstractString.search(thisRe);

    if (result == -1) {
        feedback.fadeIn('fast');
        feedback.text('no Match').css('backgroundColor',"red").fadeOut(1500);
        return false
    }
    else { //Don't remove this - game needs as much positive feedback as it can get right now.  Maybe rename (because it's not a partner match).
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

function no_dupe(text_passed) {
    //checks text against both typed answers and mouse-selected answers
    //returns TRUE if the answer is NOT a duplicate of an existing answer
    return (typeof selectDict[text_passed] == 'undefined' && typeof answerDict[text_passed] == 'undefined')
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

        if (no_dupe(inputText)) {//prevent dupes, which would reset time entered to later time
            timeLeft = secondsLeft.html();
            //record answer and time to our associative array
            answerDict[inputText] = LENGTH_OF_GAME_IN_SECONDS - parseInt(timeLeft);

            //TODO: Use this better
            test_for_gold_standard_text_match(inputText);

            updateUI();

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
            //It's a zero-length selection, or it perfectly spans mid-title to mid-text. Either way, get out of here.
            return false
        }

    if (window.confirm('select the text ' + textSelection.toString() + '?')){

        if (textSelection.anchorOffset < textSelection.focusOffset) {
            //It's a forward-direction selection, so the anchor (mousedown) is the start and the focus (mouseup) is the end
            start = textSelection.anchorOffset;
            end = textSelection.focusOffset;
        }
        else {
            //It's a backwards selection
            start = textSelection.focusOffset;
            end = textSelection.anchorOffset;
        }

        var titleTextInt; //1 = title, 2 = abstract text
        var offset;

        if (textSelection.anchorNode.parentNode.nodeName == 'DIV') {
            //We are in the abstract text.  Otherwise, it would have returned 'H1'.
            //Boy, is this asking for trouble when we do refactoring.  And horribly tight coupling between view and controller.
            titleTextInt = 2;

            //Offset seems to start at 0 in title, and at 9 in text.  Why 9?
            offset = start - 9;
        }
        else {
            //We are in abstract title.
            titleTextInt = 1;
            offset = start;
        }

        //adjust offset for leading spaces
        len1 = textSelection.toString().length;
        len2 = textSelection.toString().replace(/^[ \t]+/, "").length;
        lendiff = len1-len2;
        offset += lendiff;


        var timeLeft = secondsLeft.html();

        //clean up result
        var cleanText = trim_evil_characters(textSelection.toString());

        if (no_dupe(cleanText)) {//prevent dupes, which would reset time entered to later time

            //record answer and time to our associative array
            selectDict[cleanText] = {"secondsInt": LENGTH_OF_GAME_IN_SECONDS - parseInt(timeLeft), "titleTextInt": titleTextInt, "offset": offset};

            updateUI();
        }
        else {
            dupe_message()
        }
    }


}

function updateUI() {
    //Give each item in answer column a span with ID = answer + answerText.toString().  Will be useful later for matching.
    var table = document.getElementById("answerBody");  //Why this doesn't work with the variable answerBody, I have no idea
    table.innerHTML = "";

    var both_dicts = $.extend({}, answerDict, selectDict);

    for (var key in both_dicts) {

        if (both_dicts.hasOwnProperty(key)) {
            var new_row = table.insertRow(-1);
            var new_answer_cell = new_row.insertCell(0);
            var new_delete_cell = new_row.insertCell(1);
            new_answer_cell.id = "answer" + key.toString();
            new_answer_cell.innerHTML = key;
            new_delete_cell.innerHTML = "<a href='#' onclick='deleteKey(\"" + key.toString() + "\")'>X</a>";
        }
    }


}

function deleteKey(aKey){
    //called when user clicks the "X" next to a previous answer
    //takes an answer (the text of it, which is the key in the dict) and removes it from "both" (really, either) dicts.
    //This works for answerDict OR for selectDict because the keys are the same, only the values are different
    //Then, redraws the table by calling updateUI()

    if (typeof answerDict[aKey] != 'undefined') {
        delete(answerDict[aKey]);
    }

    if (typeof selectDict[aKey] != 'undefined') {
        delete(selectDict[aKey]);
    }

    updateUI(answerDict);
}

$(document).ready(function() {

    feedback = $('#feedback');
    inputBox = $('#userInput');
    secondsLeft = $('#secondsLeft');
    abstractText = $('#abstractTextDiv');
    abstractTitle = $('#abstractTitleDiv');
    answerDisplay = $('#answerDisplay');

    inputBox.focus();
    inputBox.keypress(moveText);
    secondsLeft.html(LENGTH_OF_GAME_IN_SECONDS);
    startCountdown(secondsLeft);
    abstractTitle.mouseup(function() {addTextFromMouseUp(window.getSelection())});//TODO: Browser compatibility testing on window.getSelection()
    abstractText.mouseup(function() {addTextFromMouseUp(window.getSelection())});

    //prevent multiple submissions of the form
    //this was a problem with the auto-submit when processing the POST took > 1 second
    $("form").submit(function() {
        $("#userTypedMatches").val(JSON.stringify(answerDict));
        $("#userHighlightedMatches").val(JSON.stringify(selectDict));
        $(this).submit(function() {
            return false;
        });
        return true;
    });

//End document.ready call
});





