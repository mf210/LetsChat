
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

function triggerAcceptFriendRequest(friend_req_obj_id){
    console.log(`Accept... ${friend_req_obj_id}`);
    let data = new FormData();
    data.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    fetch(`/friendships/accept_friend_request/${friend_req_obj_id}/`, 
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

function triggerDeclineFriendRequest(friend_req_obj_id){
    console.log(`Decline... ${friend_req_obj_id}`);
}