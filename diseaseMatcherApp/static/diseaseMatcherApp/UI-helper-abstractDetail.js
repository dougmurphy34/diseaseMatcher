/**
 * Created by Doug on 8/20/2014.
 */

//NOT LOVING THIS SOLUTION - Textarea is a poor display object, interface is unappealing

$(document).ready(function() {

    inputBox = $('#userInput');
    resultsBox = $('#inputSoFar');

    /*just testing
    $('#userInput').blur(function () {
        $(this).css("background-color", "#337733");
    });
    */


    inputBox.focus();
    resultsBox.css('background-color', '#eeeeee');
    resultsBox.css('pointer-events', 'none');
    inputBox.keypress(movetext);
    //$('#userInput').click(move_text())

//End document.ready call
});

    function movetext(e) {
        //alert(e.keyCode);

        /**/
        if (e.keyCode == 45 || e.keyCode == 13) {
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




