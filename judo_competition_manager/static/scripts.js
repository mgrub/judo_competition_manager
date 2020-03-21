function fight_reload(fight_id){
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("fight_" + fight_id.toString()).innerHTML = this.responseText
        }
    };
    xhr.open('GET', '../fight/' + fight_id.toString() + '/dropdown');
    xhr.send();
}

function fight_set_winner(fight_id, winner_id, points, subpoints){
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '../fight/' + fight_id.toString() + '/set_winner');
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("winner_id=" + winner_id.toString() +"&points=" + points.toString() + "&subpoints=" + subpoints.toString());
}