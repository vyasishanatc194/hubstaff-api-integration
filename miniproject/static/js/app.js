// Initialize Date picker 
$('#loading').hide();
$(function() {
    // Daterangepicker
    var start = moment().subtract(1, 'days');

    $("input[name=\"datesingle\"]").daterangepicker({
        singleDatePicker: true,
		showDropdowns: true,
        opens: "left",
        startDate: start,
    }, getEmployeeData);

    getEmployeeData(start);
});

// Fetch Employee data based on Date
function getEmployeeData(start) {
    $('#loading').show();
    // CSRF Token for API Request
    const token = Cookies.get('csrftoken');

    // If Table Already Exist then remove it.
    isTableExist = document.querySelector('#dynamic-table');
    if (isTableExist) {
        isTableExist.remove()
    }

    // If No Data Message is Available then Remove it.
    let noData = document.querySelector('#no-data');
    if (noData) {
        noData.remove()
    }

    // Request params data
    const data = {
        "date": start.format("YYYY-MM-DD"),
        "csrfmiddlewaretoken": token
    }
    // Ajax Call to fetch Employee Data
    $.ajax({
        type: "GET",
        url: "api/v1/hubstaff/users/",
        data: data,
        dataType: "json",
        success: async function(data){
            $('#loading').hide();
            if (data.length > 0){
                // Generate Table according to formatted matrix response
                generateTable(data[0].columns, data[0].rows);
                $("#OutputCSV").attr("disabled", false);
                $("#OutputCSV").css("cursor", "pointer");
            } else {
                // add no data message if data is not available
                var newNode = document.createElement('h3');
                newNode.innerHTML = "No Data available!"
                newNode.id = "no-data"
                var referenceNode = document.querySelector('#custom-table');
                referenceNode.appendChild(newNode);
                $("#OutputCSV").attr("disabled", true)
                $("#OutputCSV").css("cursor", "no-drop");
            }
        },
        failure: function(errMsg) {
            $('#loading').hide();
            console.log(errMsg);
        }
    });
}

// Create Dynamic table according to Employee Data Response
function generateTable(columns, rows) {
    
    // Create Table
    let table = document.createElement('table');
    table.setAttribute("class", "table table-bordered");
    table.setAttribute("id", "dynamic-table")
    // Add thead Data
    var thead = document.createElement('thead');;
    let trHead = document.createElement('tr');
    columns.forEach(function(column, cIndex){
        let th = document.createElement('th');
        th.innerHTML = column;
        trHead.appendChild(th);
    })
    thead.appendChild(trHead);
    table.appendChild(thead);

    // Add tbody Data - manage the cell as per matrix and remove duplicate
    var tbody = document.createElement('tbody');

    rows.forEach(function(row, rIndex){
        let tr = document.createElement('tr');
        row.forEach(function(item) {
            let td = document.createElement('td');
            td.innerHTML = item
            tr.appendChild(td)
        })
        tbody.appendChild(tr)
    });
    table.appendChild(tbody)

    document.getElementById("custom-table").appendChild(table)
}

// Add CSV Link on Button Click.
$("#OutputCSV").click(function(){
    window.open("http://127.0.0.1:8000/static/csv/output.csv", "_blank");
});
