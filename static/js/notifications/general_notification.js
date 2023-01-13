// Vars
let canUserLoadGeneralNotifications = true;
const notificationContainer = document.getElementById("id_general_notifications_container");

// Get Cookie by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// WebSockets
const notificationSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/notification/'
);

notificationSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const msgType = data['type'];
    if (msgType === 'general_notification') {
        appendGeneralNotification(data['notification'], insertDown=false);
    }
};

notificationSocket.onopen = function(e) {
    console.log('notification socket is open now!');
};

notificationSocket.onclose = function(e) {
    console.error('notification socket closed.');
};

// Fetching Data
function getGeneralNotifications(){
    const earliestNotif = notificationContainer.lastChild;
    const earliestNotifID = earliestNotif ? earliestNotif.id.slice(24) : null;
    const url = `/notifications/general/?earliest_notif_id=${earliestNotifID}`;
    fetch(url)
    .then((response) => response.json())
    .then((data) => {
        data.forEach(obj => appendGeneralNotification(obj));
        canUserLoadGeneralNotifications = true;
    })
    .catch((error) => {
        console.error('Error:', error);
        canUserLoadGeneralNotifications = true;
    });
}
getGeneralNotifications();

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
            break;
        case "friendships | friend request":
            card = createFriendRequestElement(notification);
            break;

        default:
            console.error(`Unkonwn notification content_type!`);
            console.log(notification['content_type'])
    }
    if (insertDown) {
        notificationContainer.appendChild(card);
    } else {
        notificationContainer.insertBefore(card, notificationContainer.firstChild);
    }
}

function createFriendshipElement(notification){
    card = createGeneralNotificationCard();
    card.id = assignGeneralCardId(notification);
    card.addEventListener("click", function(){
        window.location.href = notification['profile_url'];
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
    card.appendChild(createGeneralTimestampElement(notification));
    return card;
}

/*
    Create a Notification Card for a FriendRequest payload
*/
function createFriendRequestElement(notification){
    card = createGeneralNotificationCard()
    card.id = assignGeneralCardId(notification)
    card.addEventListener("click", function(){
        window.location.href = notification['profile_url'];
    })

    div1 = document.createElement("div")
    div1.classList.add("d-flex", "flex-row", "align-items-start")
    div1.id = assignGeneralDiv1Id(notification)
    
    img = createGeneralProfileImageThumbnail(notification)
    div1.appendChild(img)

    span = document.createElement("span")
    span.classList.add("m-auto")
    span.innerHTML = notification['verb']
    span.id = assignGeneralVerbId(notification)
    div1.appendChild(span)
    card.appendChild(div1)

    div2 = document.createElement("div")
    div2.classList.add("d-flex", "flex-row", "mt-2")
    div2.id = assignGeneralDiv2Id(notification)

    pos_action = document.createElement("a")
    pos_action.classList.add("btn", "btn-primary", "mr-2")
    // pos_action.href = "#"
    pos_action.innerHTML = "Accept"
    pos_action.addEventListener("click", function(e){
        e.stopPropagation();
        handleFriendRequest(notification['content_object_id'], accept=true, card.id);
    })
    pos_action.id = assignGeneralPosActionId(notification)
    div2.appendChild(pos_action)

    neg_action = document.createElement("a")
    neg_action.classList.add("btn", "btn-secondary")
    // neg_action.href = "#"
    neg_action.innerHTML = "Decline"
    neg_action.addEventListener("click", function(e){
        e.stopPropagation();
        handleFriendRequest(notification['content_object_id'], accept=false, card.id);
    })
    neg_action.id = assignGeneralNegActionId(notification)
    div2.appendChild(neg_action)
    card.appendChild(div2)

    card.appendChild(createGeneralTimestampElement(notification))
    return card
}

// Handle Friend Request
function handleFriendRequest(requestID, accept, cardID){
    url = `/friendships/handle_friend_request/${requestID}/`;
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
    document.getElementById(cardID).remove();
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

/*
    Timestamp at the bottom of each notification card
*/
function createGeneralTimestampElement(notification){
    const notificationTime = notification['timestamp'];
    const timestamp = document.createElement("p");
    timestamp.classList.add("small", "pt-2", "timestamp-text");
    timestamp.setAttribute('isotime', notificationTime);
    timestamp.innerHTML = dateTimeToYMWDHMS(notificationTime);
    timestamp.id = assignGeneralTimestampId(notification);
    return timestamp;
}
/*
    Calculate the seconds, minutes, hours, days, weeks and ... difference between notification and now datetime
*/
function dateTimeToYMWDHMS(datetime) {
    const startDate = new Date(datetime);
    const endDate = new Date();
    const seconds = (endDate.getTime() - startDate.getTime()) / 1000;
    const s = Math.floor(seconds % 60);
    const m = Math.floor(seconds % 3600 / 60);
    const h = Math.floor(seconds % (3600*24) / 3600);
    const d = Math.floor(seconds % ((3600*24)*7) / (3600*24));
    const w = Math.floor(seconds % ((3600*24)*30) / ((3600*24)*7));
    const M = Math.floor(seconds % (((3600*24)*30)*12) / ((3600*24)*30));
    const y = Math.floor(seconds / (((3600*24)*30)*12));
    const yDisplay = y > 0 ? y + (y == 1 ? " year, ": " years, ") : "";
    const MDisplay = M > 0 ? M + (M == 1 ? " month, ": " months, ") : "";
    const wDisplay = w > 0 ? w + (w == 1 ? " week, ": " weeks, ") : "";
    const dDisplay = d > 0 ? d + (d == 1 ? " day, " : " days, ") : "";
    const hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
    const mDisplay = m > 0 ? m + (m == 1 ? " minute, " : " minutes, ") : "";
    const sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";
    return yDisplay + MDisplay + wDisplay + dDisplay + hDisplay + mDisplay + sDisplay;
}

/*
    Update time of notification cards repeatedly every 5 seconds
*/
function updateNotificationsTime() {
    let listItems = document.querySelectorAll('.timestamp-text');
    listItems = Array.from(listItems);
    listItems.forEach(item => {
        item.innerHTML = dateTimeToYMWDHMS(item.getAttribute('isotime'));
    })
}
setInterval(updateNotificationsTime, 5000);

/*
    Sets the scroll listener for when user scrolls to bottom of notification menu.
    It will retrieve the next page of results.
*/
const menu = document.getElementById("id_general_notifications_container")
menu.addEventListener("scroll", function(e){
    if ((menu.scrollTop) >= (menu.scrollHeight - menu.offsetHeight) && canUserLoadGeneralNotifications) {
        canUserLoadGeneralNotifications = false;
        getGeneralNotifications();
    }
});

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

