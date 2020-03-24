function fight_reload(fight_id){
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("fight_" + fight_id.toString()).innerHTML = this.responseText
        }
    };
    xhr.open('GET', '/fight/' + fight_id.toString() + '/dropdown');
    xhr.send();
}

function fight_set_winner(fight_id, winner_id, points, subpoints){
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/fight/' + fight_id.toString() + '/set_winner', false);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("winner_id=" + winner_id.toString() +"&points=" + points.toString() + "&subpoints=" + subpoints.toString());
}

function group_competitor_list(group_id){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("competitor_list").innerHTML = this.responseText
        }
    };
    xhr.open('POST', '/group/' + group_id.toString());
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("action=list_competitors");
}

function group_remove_competitor(group_id, competitor_id){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {};
    xhr.open('POST', '/group/' + group_id.toString(), false);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("action=remove&competitor_id=" + competitor_id.toString());
}

function group_add_competitor(group_id, competitor_id){
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/group/' + group_id.toString(), false);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("action=add&competitor_id=" + competitor_id.toString());
}

function get_matching_competitors(search_text){
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/query', false);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("competitors_matching=" + search_text);

    return JSON.parse(xhr.responseText)
}