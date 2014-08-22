/**
 * Created by Doug on 8/20/2014.
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
        //alert(e.keyCode);

        /*TODO: prevent user from tabbing into textarea and editing it*/
        if (e.keyCode == 13) {
           // alert('I got in here');
            resultsBox.css('background-color', 'yellow');
            inputText = inputBox.val();
           // alert(inputText);
            textareaText = resultsBox.val();
            resultsBox.val(textareaText + inputText + "\n");
            inputBox.val('');
            return false;
        }


    }




