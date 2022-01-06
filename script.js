function onSubmit() {
    output = "The following details have been submitted"
    output += "\nTitle: " + document.getElementById('ticket-title').value;
    output += "\nDescription: " + document.getElementById('ticket-description').value;
    output += "\nReported Date: " + document.getElementById('reported-date').value;
    output += "\nClosed Date: " + document.getElementById('closed-date').value;
    // ticketType = document.getElementById("ticket-type");
    output += "\nType: " + document.getElementById('ticket-type').value;
    output += "\nSeverity: " + document.getElementById('ticket-severity').value;
    output += "\nStatus: " + document.getElementById('ticket-status').value;
    document.getElementById('output-textarea').innerHTML = output;
}

document.getElementById('submit-button').addEventListener('click', onSubmit);
