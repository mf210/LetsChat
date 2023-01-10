// Vars
const notificationContainer = document.getElementById("id_general_notifications_container");


// WebSockets
const notificationSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/notification/'
);

notificationSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const msgType = data['type'];
    console.log(`new message: ${msgType}`);
};

notificationSocket.onopen = function(e) {
    console.log('notification socket is open now!');
};

notificationSocket.onclose = function(e) {
    console.error('notification socket closed.');
};

// Fetching Data
(function getGeneralNotifications(){
    const earliestNotif = notificationContainer.lastChild;
    const earliestNotifID = earliestNotif ? earliestNotif.id : null;
    const url = `/notifications/general/?earliest_notif_id=${earliestNotifID}`;
    fetch(url)
    .then((response) => response.json())
    .then((data) => {
        data.forEach(obj => appendGeneralNotification(obj, insertDown=false));
    })
    .catch((error) => {
        console.error('Error:', error);
    });
})()

/*
    The card that each notification sits in
*/
function createGeneralNotificationCard(){
    const card = document.createElement("div");
    card.classList.add("d-flex", "flex-column", "align-items-start", "general-card", "p-4");
    return card;
}

/*
    Append a general notification to the list.
*/
function appendGeneralNotification(notification, insertDown=true){
    switch(notification['content_type']) {
        case "friendships | friendship":
            card = createFriendshipElement(notification);
            notificationContainer.insertBefore(card, notificationContainer.childNodes[0]);
            break;

        default:
            console.error(`Unkonwn notification content type!`);
    }
}

function createFriendshipElement(notification){
    card = createGeneralNotificationCard();
    card.id = assignGeneralCardId(notification);
    card.addEventListener("click", function(){
        console.log(`${notification['notification_id']} notification clicked!`);
    })

    const div1 = document.createElement("div");
    div1.classList.add("d-flex", "flex-row", "align-items-start");
    div1.id = assignGeneralDiv1Id(notification);

    img = createGeneralProfileImageThumbnail(notification);
    div1.appendChild(img);

    span = document.createElement("span")
    span.classList.add("align-items-start", "pt-1", "m-auto");
    if(notification['verb'].length > 50){
        span.innerHTML = notification['verb'].slice(0, 50) + "...";
    }
    else{
        span.innerHTML = notification['verb'];
    }
    span.id = assignGeneralVerbId(notification);
    div1.appendChild(span);
    card.appendChild(div1);
    // card.appendChild(createGeneralTimestampElement(notification))
    return card;
}


/*
    Circular image icon that can be in a notification card
*/
function createGeneralProfileImageThumbnail(notification){
    const img = document.createElement("img");
    img.classList.add("notification-thumbnail-image", "img-fluid", "rounded-circle", "mr-2");
    img.src = notification['image_url'];
    img.id = assignGeneralImgId(notification);
    return img;
}

// /*
//     Timestamp at the bottom of each notification card
// */
// function createGeneralTimestampElement(notification){
//     const timestamp = document.createElement("p")
//     timestamp.classList.add("small", "pt-2", "timestamp-text")
//     timestamp.innerHTML = notification['timestamp']
//     timestamp.id = assignGeneralTimestampId(notification)
//     return timestamp
// }

//  Helpers for generating IDs 
function assignGeneralDiv1Id(notification){
    return "id_general_div1_" + notification['notification_id']
}

function assignGeneralImgId(notification){
    return "id_general_img_" + notification['notification_id']
}

function assignGeneralVerbId(notification){
    return "id_general_verb_" + notification['notification_id']
}

function assignGeneralDiv2Id(notification){
    return "id_general_div2_" + notification['notification_id']
}

function assignGeneralPosActionId(notification){
    return "id_general_pos_action_" + notification['notification_id']
}

function assignGeneralNegActionId(notification){
    return "id_general_neg_action_" + notification['notification_id']
}

function assignGeneralTimestampId(notification){
    return "id_timestamp_" + notification['notification_id']
}

function assignGeneralCardId(notification){
    return "id_general_notification_" + notification['notification_id']
}

