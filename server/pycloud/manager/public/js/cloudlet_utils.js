/////////////////////////////////////////////////////////////////////////////////////
// Creates a modal dialog to show wait state for a process (no actual progress though).
/////////////////////////////////////////////////////////////////////////////////////
function WaitDialog (headerText) {
    var pleaseWaitDiv = $('<div class="modal fade" id="pleaseWaitDialog" role="dialog" data-backdrop="static" data-keyboard="false"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h3>'+headerText+'...</h3></div><div class="modal-body"><div class="progress progress-striped active"><div class="progress-bar" role="progressbar" style="width: 100%;"></div></div></div></div></div></div>');
    return {
        show: function() {
            pleaseWaitDiv.modal();
        },
        hide: function () {
            pleaseWaitDiv.modal('hide');
        },
    };
}

/////////////////////////////////////////////////////////////////////////////////////
// Creates a notification to inform the user of an event.
/////////////////////////////////////////////////////////////////////////////////////
function Alert(level, message) {
    // Template for the alert message.
    var alertDiv = $('<div id="alert-div" style="position: fixed; top: 55px; display: block;"><div class="alert alert-dismissable fade in alert-'+level+'" id="alert-element"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button><div id="alert-text">'+message+'</div></div></div>');

    // Functions.
    return {
        show: function() {
            // Show the alert.
            $('#navbar-container').append(alertDiv);
            
            // Add timer to auto-close the alert after some time.
            alertElement = $('#alert-element');
            alertDiv.fadeIn(200, function () {
                setTimeout(function () {
                    alertElement.alert('close');
                    alertElement.parent().remove();
                }, 5000);
            });
        },
        hide: function () {
            alert('hiding');
        },
    };

}

