// searchFormToggle()
//
//  Switches visibility between the basic search form and the advanced search 
//  form.  

function searchFormToggle() {
    basic = document.getElementById("basicsearch")
    advanced = document.getElementById("advancedsearch")
    toggler = document.getElementById("searchFormToggler")
    bstyle = basic.getAttribute("style")
    if (bstyle == "") {
        basic.setAttribute("style", "display: none;")
        advanced.setAttribute("style", "")
        toggler.innerHTML = "Basic search"
    } else {
        basic.setAttribute("style", "")
        advanced.setAttribute("style", "display: none;")
        toggler.innerHTML = "Advanced search"
    }   
}

function validateMessage() {
    recipients = document.getElementById("recipientbox");
    searchrecips = document.getElementById("searchrecipients");
    if ((recipients && recipients.value == "(select contacts below)") && (searchrecips && searchrecips.value == "-9999")) {
        alert("You must select recipients.");
        return false;
    }
    subject = document.getElementById("id_subject");
    if (subject && !subject.value) {
        alert("You must enter a subject.")
        return false;
    }
    return true;
}

function copyEditorValue() {
    var a=dojo.byId('messageformelement');
    a.value=dijit.byId('id_message').getValue(false); 
}

function showPreview() {
    var form = document.forms[0];
    var b = dojo.byId("blackout");
    b.setAttribute("class", "blackout");
    var p = dojo.byId("preview");
    var newinput = document.createElement("input");
    newinput.setAttribute("type", "hidden");
    newinput.setAttribute("name", "Submit");
    newinput.setAttribute("value", "Send");
    form.appendChild(newinput);
    p.innerHTML = "<h2 style='margin-top: 5px;'>Preview</h2><hr><h3>Subject: "+ form.subject.value +"</h3>"+ 
                  form.message.value + 
                  "<br><br><span style='font-size: 10px;'>You received this email because of your previous relationship with our organization.  To unsubscribe, <a href='#'>click here</a>." + 
                  "<hr><br><input type='button' value='Cancel' onclick='hidePreview();'> <input type='button' value='Send this message' onclick='document.forms[0].submit();'>";
    dojo.place(p, "blackout", "before");
}

function hidePreview() {
    var b = dojo.byId("blackout");
    b.setAttribute("class", "");
    dojo.place("preview", "hideyhole", "first");
}




var idthing = 1;  // this is 1 because we start with one advanced search query.

function addAdvanced(e) { 
    buttons = document.getElementById("advbuttons");        //new rows go before this
    query = document.getElementById("querytmpl");             //query row template
    condition = document.getElementById("conditiontmpl");     //condition row template
    plusbuttoncontainer = document.getElementById("plusbuttoncontainer");   // the plus button.  only one ever exists.
    minusbuttoncontainer = document.getElementById("minusbuttoncontainertmpl");     // minus button template.  is copied and un-id-ed.

    nquery = dojo.clone(query);
    ncondition = dojo.clone(condition);
    nminus = dojo.clone(minusbuttoncontainer);

    ncondition.setAttribute("id", "condition"+idthing);
    idthing = idthing + 1;
    nquery.setAttribute("id", "query"+idthing);
    nminus.setAttribute("id", "");

    dojo.place(ncondition, buttons, "before"); 
    dojo.place(nquery, buttons, "before");
    dojo.place(nminus, plusbuttoncontainer, "before");
    dojo.place(plusbuttoncontainer, nquery, "last");

}

function removeAdvanced(node) {
    query = node.parentNode.parentNode;
    condition = query.nextSibling;
    while (condition != null && condition.nodeType != 1) {
        condition = condition.nextSibling;
    }
    daddy = condition.parentNode;
    daddy.removeChild(condition);
    daddy.removeChild(query);
}


function main() {
    // Advanced search form    
    plusbutton = document.getElementById("plusbutton");     //event owner for adding a row
    if (plusbutton != null) {
        dojo.connect(plusbutton, "onclick", "addAdvanced");
    }
}
