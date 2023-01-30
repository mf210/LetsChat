
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

function triggerHandleFriendRequest(url, accept){
    let data = new FormData();
    data.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    data.append('accept', accept);
    fetch(url, 
        {
            method: 'POST',
            body: data
        },
    )
    .then((response) => response.text())
    .then((data) => {
        location.reload();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function sendFriendRequest(url, receiver){
    let data = new FormData();
    data.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    data.append('receiver_id', receiver);
    fetch(url, {method: 'POST', body: data})
        .then((response) => response.text())
        .then((value) => {
            location.reload();
        })
        .catch((error) => {
            console.error(error);
        });
}

function cancelFriendRequest(url, pk){
    let data = new FormData();
    data.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    data.append('pk', pk);
    fetch(url, {method: 'POST', body: data})
        .then((response) => response.text())
        .then((value) => {
            location.reload();
        })
        .catch((error) => {
            console.error(error);
        });
}

function unfriend(url, pk){
    let data = new FormData();
    data.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    data.append('pk', pk);
    fetch(url, {method: 'POST', body: data})
    .then((response) => response.text())
    .then((value) => {
        location.reload();
    })
    .catch((error) => {
        console.error(error);
    });
}

function redirectUser(url){
    window.location.href = url;
}