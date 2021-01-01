// General functions for storing user settings and preferences in session storage
// The appSettings JSON object can be used to store and retrieve custom settings
// The JSON object is saved in session storage
// setAppSetting, getAppSetting, and deleteAppSetting operate on the JSON object
// The JSON object is structured as in these examples:
// appSettings = {categoryA: {parameter1: value2, parameter2:value2, ... }, categoryB:{parameter:value},...}
// appSettings =  {"pageTabs":{"Admin":"SetupTab","About":"InfoTab"},"userSettings":{"UserName":"My Name"}}


function setAppSetting(category, parameter, value) {
    var appSettings_JSON, appSettings, myJSON;
    // First, see if there are saved settings stored in the session
    // If there are saved settings, update them with the new setting
    appSettings_JSON = sessionStorage.getItem("appSettings");
    if (appSettings_JSON) {
        if (appSettings_JSON != "") {
            // Convert the saved settings into a JSON
            appSettings = JSON.parse(appSettings_JSON);
            // Initialize new category for settings if it doesn't exist
            if (!appSettings[category]) {
                appSettings[category] = {}
            }
        }
        // Else, initialize appSettings if it doesn't exist
    } else {
        appSettings = {}
        appSettings[category] = {}
    }
    // Save the current value into the appSettings object
    appSettings[category][parameter] = value;
    // Convert the JSON object to a string
    myJSON = JSON.stringify(appSettings);
    // console.log('myJSON =' + myJSON);
    // Save the JSON object to the session variable
    sessionStorage.setItem("appSettings", myJSON);
}

function getAppSetting(category, parameter) {
    var appSettings_JSON, appSettings;
    appSettings_JSON = sessionStorage.getItem("appSettings");
    if (appSettings_JSON) {
        if (appSettings_JSON != "") {
            // Convert the saved settings into a JSON
            appSettings = JSON.parse(appSettings_JSON);
            if (appSettings[category]) {
                if (appSettings[category][parameter]) {
                    return appSettings[category][parameter];
                }
            }
        }
    }
    return null
}

function deleteAppSetting(category, parameter) {
    var appSettings_JSON, appSettings, size, myJSON;
    appSettings_JSON = sessionStorage.getItem("appSettings");
    if (appSettings_JSON) {
        if (appSettings_JSON != "") {
            // Convert the saved settings into a JSON
            appSettings = JSON.parse(appSettings_JSON);
            if (appSettings[category]) {
                if (appSettings[category][parameter]) {
                    // Delete the parameter if it exists
                    delete appSettings[category][parameter];
                    // Delete the category if there are no other parameters
                    size = Object.keys(appSettings[category]).length;
                    if (size == 0) {
                        delete appSettings[category];
                    }
                    // Delete appSettings if there are no other categories
                    size = Object.keys(appSettings).length;
                    if (size == 0) {
                        sessionStorage.removeItem("appSettings", myJSON);
                        // Save the updated appSettings object
                    } else {
                        // Convert the JSON object to a string
                        myJSON = JSON.stringify(appSettings);
                        // Save the JSON object to the session variable
                        sessionStorage.setItem("appSettings", myJSON);
                    }
                }
            }
        }
    }
}

// Tabs for pages
// Based on example here: https://www.w3schools.com/w3css/w3css_tabulators.asp
// Requires HTML elements defined as in these examples:
// 
// <div class="w3-bar w3-blue">
// <button id='button_UserInfoTab' class="w3-bar-item w3-button tablink w3-black" onclick="openTab(event, 'UserInfoTab', 'Admin')">User Info</button>
// <button id='button_SetUpTab' class="w3-bar-item w3-button tablink" onclick="openTab(event, 'SetUpTab', 'Admin')">App Setup</button></div>
// 
// <div class="infoTab" id="UserInfoTab">
// <div class="infoTab" id="SetUpTab" style="display:none">
// 
// <script type="text/javascript" src="{{ url_for('static', filename="js/appSettings.js") }}"></script>
// <!-- Reload page to last loaded tab -->
// <script type='text/javascript'>
//    document.addEventListener("DOMContentLoaded", function (event) {
//        const pageName = 'Admin';
//        const default_tab = 'UserInfoTab';
//        loadSavedTabOrDefaultTab(pageName, default_tab)
//    });
// </script>

function openTab(evt, infoTabName, pageName) {
    // Update the appSetting session variable with the current tab selection
    setAppSetting('pageTabs', pageName, infoTabName)

    // Hide the non-selected tabs and display the selected tab
    var i, x, tablinks;

    x = document.getElementsByClassName("infoTab");
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" w3-black", "");
    }
    document.getElementById(infoTabName).style.display = "block";
    evt.currentTarget.className += " w3-black";
}

function loadSavedTabOrDefaultTab(pageName, default_tab) {
    // Check appSettings for saved tab setting
    // If savedTab exists, open the saved tab
    // Else, open the default tab
    var savedTab = getAppSetting('pageTabs', pageName);
    if (savedTab) {
        document.getElementById(`button_${savedTab}`).click();
    } else {
        document.getElementById(`button_${default_tab}`).click();
    }
}

