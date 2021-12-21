config = {
    locateFile: filename => `/dist/${filename}`
}

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

document.getElementById('new-ticket-submit-button').addEventListener('click', onSubmit);

initSqlJs(config).then(function (SQL) {
    //Create the database
    const db = new SQL.Database();
    // Run a query without reading the results
    db.run("CREATE TABLE test (col1, col2);");
    // Insert two rows: (1,111) and (2,222)
    db.run("INSERT INTO test VALUES (?,?), (?,?)", [1, 111, 2, 222]);

    // Prepare a statement
    const stmt = db.prepare("SELECT * FROM test WHERE col1 BETWEEN $start AND $end");
    stmt.getAsObject({ $start: 1, $end: 1 }); // {col1:1, col2:111}

    // Bind new values
    stmt.bind({ $start: 1, $end: 2 });
    while (stmt.step()) { //
        const row = stmt.getAsObject();
        console.log('Here is a row: ' + JSON.stringify(row));
    }
});