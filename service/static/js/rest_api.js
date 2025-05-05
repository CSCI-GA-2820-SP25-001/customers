$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_id").val(res.id);
        $("#customer_first_name").val(res.first_name);
        $("#customer_last_name").val(res.last_name);
        $("#customer_address").val(res.address);
        $("#customer_email").val(res.email);
        $("#customer_password").val(res.password);
        $("#customer_status").val(res.status);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_first_name").val("");
        $("#customer_last_name").val("");
        $("#customer_address").val("");
        $("#customer_email").val("");
        $("#customer_password").val("");
        $("#customer_status").val("active");  // for default
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Customer
    // ****************************************

    $("#create-btn").click(function () {

        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let email = $("#customer_email").val();
        let address = $("#customer_address").val();
        let password = $("#customer_password").val();
        let status = $("#customer_status").val();

        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "address": address,
            "password": password,
            "status": status
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/customers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Customer
    // ****************************************

    $("#update-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let email = $("#customer_email").val();
        let address = $("#customer_address").val();
        let password = $("#customer_password").val();
        let status = $("#customer_status").val();
        
        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "address": address,
            "password": password,
            "status": status
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/customers/${customer_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Customer
    // ****************************************

    $("#retrieve-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/customers/${customer_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Customer
    // ****************************************

    $("#delete-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/customers/${customer_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Customer has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // List all Customers
    // ****************************************

    $("#list-btn").click(function () {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: "/customers",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-1">First Name</th>'
            table += '<th class="col-md-1">Last Name</th>'
            table += '<th class="col-md-2">Email</th>'
            table += '<th class="col-md-2">Address</th>'
            table += '<th class="col-md-1">Password</th>'
            table += '<th class="col-md-1">Status</th>'
            table += '<th class="col-md-1">Created</th>'
            table += '<th class="col-md-1">Updated</th>'
            table += '</tr></thead><tbody>'
            let firstCustomer = "";
            for(let i = 0; i < res.length; i++) {
                let customer = res[i];
                table +=  `<tr id="row_${i}"><td>${customer.id}</td><td>${customer.first_name}</td><td>${customer.last_name}</td><td>${customer.email}</td><td>${customer.address}</td><td>${customer.password}</td><td>${customer.status}</td><td>${customer.creation_date || 'N/A'}</td><td>${customer.last_updated || 'N/A'}</td></tr>`;
                if (i == 0) {
                    firstCustomer = customer;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstCustomer != "") {
                update_form_data(firstCustomer)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#customer_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // Function to display search results
    function display_search_results(res) {
        $("#search_results").empty();
        let table = '<table class="table table-striped" cellpadding="10">'
        table += '<thead><tr>'
        table += '<th class="col-md-1">ID</th>'
        table += '<th class="col-md-1">First Name</th>'
        table += '<th class="col-md-1">Last Name</th>'
        table += '<th class="col-md-2">Email</th>'
        table += '<th class="col-md-2">Address</th>'
        table += '<th class="col-md-1">Password</th>'
        table += '<th class="col-md-1">Status</th>'
        table += '<th class="col-md-1">Created</th>'
        table += '<th class="col-md-1">Updated</th>'
        table += '</tr></thead><tbody>'
        let firstCustomer = "";
        for(let i = 0; i < res.length; i++) {
            let customer = res[i];
            table +=  `<tr id="row_${i}"><td>${customer.id}</td><td>${customer.first_name}</td><td>${customer.last_name}</td><td>${customer.email}</td><td>${customer.address}</td><td>${customer.password}</td><td>${customer.status}</td><td>${customer.creation_date || 'N/A'}</td><td>${customer.last_updated || 'N/A'}</td></tr>`;
            if (i == 0) {
                firstCustomer = customer;
            }
        }
        table += '</tbody></table>';
        $("#search_results").append(table);

        // copy the first result to the form
        if (firstCustomer != "") {
            update_form_data(firstCustomer)
        }

        flash_message("Success")
    }

    // ****************************************
    // Search for a Customer using form fields
    // ****************************************

    $("#search-btn").click(function () {
        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let email = $("#customer_email").val();
        let address = $("#customer_address").val();
        let password = $("#customer_password").val();
        let status = $("#customer_status").val();

        let queryParams = [];
        
        if (first_name) queryParams.push(`first_name=${encodeURIComponent(first_name)}`);
        if (last_name) queryParams.push(`last_name=${encodeURIComponent(last_name)}`);
        if (email) queryParams.push(`email=${encodeURIComponent(email)}`);
        if (address) queryParams.push(`address=${encodeURIComponent(address)}`);
        if (password) queryParams.push(`password=${encodeURIComponent(password)}`);
        if (status && status !== "active") queryParams.push(`status=${encodeURIComponent(status)}`);

        let queryString = queryParams.join('&');

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/customers?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            display_search_results(res);
        });

        ajax.fail(function(res){
            let errorMessage = "An error occurred during search.";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(errorMessage);
        });
    });

    // ****************************************
    // Search for a Customer using custom query
    // ****************************************

    $("#query-search-btn").click(function () {
        let searchQuery = $("#customer_search_query").val();
        let queryParams = [];
        
        // Check if search query is empty
        if (!searchQuery) {
            flash_message("Please enter a search query. Format: field=value (e.g., email=test, status=active)");
            return;
        }

        // Parse the search query
        try {
            // Split by commas, but not within quotes
            let queryParts = searchQuery.split(',').map(part => part.trim());
            
            for (let part of queryParts) {
                // Check if the part has the format field=value
                if (!part.includes('=')) {
                    throw new Error(`Invalid query format: "${part}". Expected format: field=value`);
                }
                
                let [field, value] = part.split('=').map(item => item.trim());
                
                // Validate field
                const validFields = ["first_name", "last_name", "email", "password", "address", "status"];
                if (!validFields.includes(field)) {
                    throw new Error(`Invalid field: "${field}". Valid fields are: ${validFields.join(', ')}`);
                }
                
                // Validate status value if field is status
                if (field === "status" && !["active", "suspended", "deleted"].includes(value)) {
                    throw new Error(`Invalid status value: "${value}". Valid status values are: active, suspended, deleted`);
                }
                
                queryParams.push(`${field}=${encodeURIComponent(value)}`);
            }
        } catch (error) {
            flash_message(`Error in search query: ${error.message}`);
            return;
        }

        let queryString = queryParams.join('&');
        
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/customers?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            display_search_results(res);
        });

        ajax.fail(function(res){
            let errorMessage = "An error occurred during search.";
            if (res.responseJSON && res.responseJSON.message) {
                errorMessage = res.responseJSON.message;
            }
            flash_message(errorMessage);
        });
    });

})
