$(document).ready(function() {

    $('.myInput').each(function() {
        toggleFieldClass($(this));
    });
     // Check on input change for all inputs
     $('.myInput').on('input', function() {
        toggleFieldClass($(this));
    });

    function toggleFieldClass($input) {
        var inputVal = $input.val();
        if (inputVal === '') {
            $input.removeClass('fill-field').addClass('empty-field');
        } else {
            $input.removeClass('empty-field').addClass('fill-field');
        }
    }
});