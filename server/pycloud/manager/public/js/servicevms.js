
/////////////////////////////////////////////////////////////////////////////////////
// Function to stop a Service VM through Ajax.
/////////////////////////////////////////////////////////////////////////////////////
function stopSVM(stopUrl)
{
    // Show progress bar.
    var dialog = WaitDialog("Stopping Service VM Instance");
    dialog.show();
    
    // Send the ajax request to start the service vm.
    $.ajax({
      url: stopUrl,
      dataType: 'json',
      success: function( resp ) {
        // Hide the progress bar and reload the page to show the changes.
        dialog.hide();
        window.top.location=window.top.location;
      },
      error: function( req, status, err ) {
        dialog.hide();
        console.log( 'something went wrong', status, err );
      }
    });
}    

/////////////////////////////////////////////////////////////////////////////////////
// Function to start a VNC window.
/////////////////////////////////////////////////////////////////////////////////////
function openVNC(vncUrl)
{
    // Send the ajax request to start the VNC window.
    $.ajax({
      url: vncUrl,
      dataType: 'json',
      success: function( resp ) {
        // Do nothing, as the VNC window should have opened by now.
        console.log( 'VNC window was opened successfully.');
      },
      error: function( req, status, err ) {
        console.log( 'Something went wrong', status, err );
      }
    });
}     