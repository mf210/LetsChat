
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
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
