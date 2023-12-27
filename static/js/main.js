function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const items = document.getElementsByClassName('vote-section')

for (let item of items) {
    const [buttonDown, counter, buttonUp] = item.children;
    buttonDown.addEventListener('click', () => {
        alert('Hello!');
    })
    buttonUp.addEventListener('click', () => {
        const formData = new FormData();

        formData.append('question_id', buttonUp.dataset.id)

        const request = new Request('/questionupvote/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        });

        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                counter.innerHTML = data.count
            });
    })
}
