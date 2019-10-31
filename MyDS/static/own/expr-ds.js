
$(document).ready(function () {

    $('#add').click(function () {
        $('#select1 option:selected').remove().appendTo('#select2');
        sort("select2");
        saveInHd();
        optionsClick();
        return true;
    });

    $('#addall').click(function () {
        $('#select1 option:enabled').remove().appendTo('#select2');
        sort("select1");
        sort("select2");
        saveInHd();
        optionsClick();
        return true;
    });

    $('#remove').click(function () {
        $('#select2 option:selected').remove().appendTo('#select1');
        sort("select1");
        saveInHd();
        optionsClick();
        return true;
    });

    $('#removeall').click(function () {
        $('#select2 option:enabled').remove().appendTo('#select1');
        sort("select1");
        sort("select2");
        saveInHd();
        optionsClick();
        return true;
    });



    ProcessSelectHD();

});

function sort(sname) {
    $("#" + sname).append($("#" + sname + " option").remove().sort(function (a, b) {
        var at = $(a).val(), bt = $(b).val();
        return (at > bt) ? 1 : ((at < bt) ? -1 : 0);
    }));
    
}

function optionsClick()
{
    //$('option').mousedown(function (e) {
    //    var select = $(this).parent();
    //    var scroll = select.scrollTop;

    //    e.preventDefault();
    //    $(this).prop('selected', !$(this).prop('selected'));

    //    setTimeout(function () { select.scrollTop = scroll; }, 0);

    //    $(select).focus();

    //    return false;
    //});
}

function saveInHd() {
    var options = [];
    $('#select2 option:enabled').each(function () {
        options.push($(this).val());
    });
    $("#hdselect2").val(JSON.stringify(options));
}

function ProcessSelectHD() {
    val = $("#hdselect2").val();
    optionsClick();
    if (val && (val.length > 0)) {

        var options = JSON.parse(val);
        options.forEach(function (item) {
            $('#select1 option[value="' + item + '"]').remove().appendTo('#select2');
        });
        sort('select1');
        sort('select2');
    }
    
}